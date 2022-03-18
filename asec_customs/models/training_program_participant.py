from odoo import models, fields, api, _

class TrainingProgramParticipant(models.Model):
    _name = 'training.program.participant'
    _description = 'Training Program Participant'

    name = fields.Char(string="Name", related='employee_id.name')
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    gender = fields.Selection(related='employee_id.gender', related_sudo=True)
    program_id = fields.Many2one('training.program', string="Training Program")
    document_lesp_id = fields.Many2one('training.program.document', string="LESP/Security Licensed")
    document_nbi_id = fields.Many2one('training.program.document', string="NBI Clearance")
    document_police_id = fields.Many2one('training.program.document', string="Police Clearance")
    document_ishihara_id = fields.Many2one('training.program.document', string="Ishihara Test")
    document_coe_id = fields.Many2one('training.program.document', string="COE")
    ishihara_result = fields.Selection(related='document_ishihara_id.ishihara_result')
    state = fields.Selection([
        ('incomplete', 'Incomplete'),
        ('complete','Complete'),
        ('disqualified','Disqualified'),
    ],string="Request Status",default='incomplete', compute='compute_state')
    attendance_status = fields.Selection([
        ('done','Present'),
        ('blocked','Not Present'),
    ],string="Attendance Status")
    remarks = fields.Text(string="Remarks")

    def action_upload_document(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'training.program.document',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_program_id': self.program_id.id,
                'default_employee_id': self.employee_id.id,
            }
        }

    @api.depends('document_lesp_id','document_nbi_id','document_police_id','document_ishihara_id','document_coe_id')
    def compute_state(self):
        for rec in self:
            complete_count = 0

            if rec.document_lesp_id:
                complete_count += 1
            else:
                if rec.document_nbi_id or rec.document_police_id:
                    complete_count += 1

            if rec.document_coe_id:
                complete_count += 1

            if rec.document_ishihara_id:
                if rec.ishihara_result == 'not_defective':
                    complete_count += 1
                else:
                    rec.state = 'disqualified'

            if rec.state != 'disqualified':
                if complete_count >= 3:
                    rec.state = 'complete'
                else:
                    rec.state = 'incomplete'
            # else:
            #     rec.state = 'incomplete'