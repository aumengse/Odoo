from odoo import models, fields, api, _

class TrainingProgramDocument(models.Model):
    _name = 'training.program.document'
    _description = 'Training Documents'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    document_type_id = fields.Many2one('training.program.document.type', string='Document', tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    program_id = fields.Many2one('training.program', 'Training Program')
    attachment = fields.Binary(string="Attachment", tracking=True)
    attachment_id = fields.Many2one('ir.attachment', string="Attachment ID")
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, vals):
        res = super(TrainingProgramDocument, self).create(vals)
        if vals.get('attachment'):
            attachment_id = self.env['ir.attachment'].create({
                'name': vals['name'],
                'datas': vals['attachment'],
                'res_model': self._name,
                'res_id': res.id,
                'type': 'binary',
            })

            res.write({
                'attachment_id': attachment_id.id
            })

        return res
