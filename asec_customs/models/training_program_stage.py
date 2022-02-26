from odoo import models, fields, api

class TrainingProgramStage(models.Model):
    _name = 'training.program.stage'
    _description = 'Training Program Stages'
    _order = 'sequence, id'

    name = fields.Char()
    code = fields.Char()
    sequence = fields.Integer('Sequence', default=10)
