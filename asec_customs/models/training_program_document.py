from odoo import models, fields, api, _

class TrainingProgramDocument(models.Model):
    _name = 'training.program.document'
    _description = 'Training Documents'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    document_type_id = fields.Many2one('training.program.document.type', string='Document', tracking=True)
    document_type_type = fields.Selection(related='document_type_id.type')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    program_id = fields.Many2one('training.program', 'Training Program', tracking=True)
    attachment = fields.Binary(string="Attachment", tracking=True, attachment=True)
    attachment_name = fields.Char('Attachment Name')
    attachment_id = fields.Many2one('ir.attachment', string="Attachment ID", tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", tracking=True,)
    date_expiry = fields.Date(string="Expiry Date", tracking=True)
    ishihara_result = fields.Selection([
        ('not_defective', 'Not Defective'),
        ('defective', 'Defective'),
    ], string="Ishihara Test Result")

    def create_attachment(self,vals,res):
        attachment_id = self.env['ir.attachment'].create({
            'name': vals['name'] if 'name' in vals else res.name,
            'datas': vals['attachment'],
            'res_model': self._name,
            'res_id': res.id,
            'type': 'binary',
        })

        return attachment_id

    @api.model
    def create(self, vals):
        res = super(TrainingProgramDocument, self).create(vals)
        if vals.get('attachment'):
            attachment_id = self.create_attachment(vals,res)
            res.write({
                'attachment_id': attachment_id.id
            })

        participant_id = self.env['training.program.participant'].search([('program_id', '=', res.program_id.id),
                                                                          ('employee_id', '=', res.employee_id.id)])

        if res.document_type_type == 'security_licensed':
            participant_id.document_lesp_id = res.id
        elif res.document_type_type == 'nbi_clearance':
            participant_id.document_nbi_id = res.id
        elif res.document_type_type == 'police_clearance':
            participant_id.document_police_id = res.id
        elif res.document_type_type == 'ishihara_test':
            participant_id.document_ishihara_id = res.id
        elif res.document_type_type == 'coe':
            participant_id.document_coe_id = res.id
        return res

    def write(self, vals):
        res = super(TrainingProgramDocument, self).write(vals)
        if 'attachment' in vals:
            attachment_id = self.create_attachment(vals, self)
            self.write({
                'attachment_id': attachment_id.id
            })
        return res

    @api.onchange('program_id')
    def onchange_program_id(self):
        employee_ids = self.program_id.participant_ids.mapped('employee_id')
        if self.program_id.participant_ids.mapped('employee_id'):
            domain = [('id','in',employee_ids.ids)]
            return {'domain': {'employee_id': domain}}
