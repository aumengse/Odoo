from odoo import models, fields, api, _

class TrainingProgramDocumentType(models.Model):
    _name = 'training.program.document.type'
    _description = 'Training Document Type'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    active = fields.Boolean(string="Active", default=True)
