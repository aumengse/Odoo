from odoo import models, fields, api

class TrainingProgramStage(models.Model):
    _name = 'training.program.stage'
    _description = 'Training Program Stages'
    _order = 'sequence, id'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    active = fields.Boolean(string="Active", default=True)
    sequence = fields.Integer('Sequence', default=10)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
