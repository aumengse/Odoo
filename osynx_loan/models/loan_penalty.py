from odoo import models, fields, api
from datetime import datetime

class LoanInterest(models.Model):
    _name = 'loan.penalty'
    _description = 'Loan Penalty'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('member.account',string="Member")
    date = fields.Date(string="Date", default=datetime.today().date())
    type = fields.Selection([('late_contribution', "Late Contribution"),
                              ('loan_expired', "Expired Loan"),
                              ], string="Type")
    amount = fields.Float(string="Amount")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean(string="Active", default=True)

    state = fields.Selection([('draft', "Draft"),
                              ('process', "Processing"),
                              ('validate', "Validated")
                              ], default='draft')

    def action_submit(self):
        self.state = 'process'

    def action_validate(self):
        self.state = 'validate'
