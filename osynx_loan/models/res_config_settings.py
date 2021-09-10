from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    contribution_due_day = fields.Selection(related='company_id.contribution_due_day', readonly=False)
    contribution_late_fee = fields.Float(related='company_id.contribution_late_fee', readonly=False)
    grace_period = fields.Selection(related='company_id.grace_period', readonly=False)