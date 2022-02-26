from odoo import models, fields, api, _

class TrainingProgram(models.Model):
    _name = 'training.program'
    _description = 'Training Programs'

    def _default_stage_id(self):
        default_stage = self.env['training.program.stage'].search([('name', '=', _('New'))], limit=1)
        if not default_stage:
            default_stage = self.env['training.program.stage'].create({
                'name': _("New"),
                'sequence': 0,
                'code': 'new',
            })
        return default_stage.id

    name = fields.Char()
    stage_id = fields.Many2one('training.program.stage', string="State", default=_default_stage_id)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string="Contact")
    employee_id = fields.Many2one('hr.employee', string="Instructor")
    date_start = fields.Datetime(string="Training Start")
    date_end = fields.Datetime(string="Training End")
    user_id = fields.Many2one('res.users', 'User',default=lambda self: self.env.uid)