from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime

class LoanExtendWizard(models.TransientModel):
    _name = "loan.extend.wizard"
    _description = "Loan Extend Wizard"

    @api.model
    def default_get(self, fields_list):
        res = super(LoanExtendWizard, self).default_get(fields_list)

        context = self.env.context
        active_id = context.get('active_id')
        loan_account_id = self.env[context.get('active_model')].browse(active_id)

        res['date_from'] = loan_account_id.date_to
        return res

    date_from = fields.Date(string="Old Maturity Date")
    date_to = fields.Date(string="New Maturity Date", compute='compute_date_to', store=True)
    extended_term = fields.Integer(string="Term Extension")

    @api.depends('date_from', 'extended_term')
    def compute_date_to(self):
        for rec in self:
            rec.date_to = False
            if rec.date_from:
                rec.date_to = rec.date_from + relativedelta(months=rec.extended_term)


    def action_extend(self):
        context = self.env.context
        active_id = context.get('active_id')

        loan_account_id = self.env[context.get('active_model')].browse(active_id)

        loan_account_id.with_context({
            'new_term': self.extended_term
        }).action_extend()

        loan_account_id.action_compute_installment()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Occupants Added!',
                'type': 'rainbow_man',
            }
        }