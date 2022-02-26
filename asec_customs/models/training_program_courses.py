from odoo import models, fields, api, _

class TrainingProgramCourses(models.Model):
    _name = 'training.program.courses'
    _description = 'Training Courses'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active",default=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)