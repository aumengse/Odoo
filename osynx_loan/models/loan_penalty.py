from odoo import models, fields, api
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
import calendar

class LoanInterest(models.Model):
    _name = 'loan.penalty'
    _description = 'Loan Penalty'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('member.account',string="Member")
    loan_id = fields.Many2one('loan.account',string="Reference Loan")
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

    def action_cron_late_contribution_fee(self):
        date_today = datetime.today().date()
        company_id = self.env.company

        if date_today.day == (int(company_id.grace_period) + 1):
            member_ids = self.env['member.account'].search([])

            prev_month = date_today + relativedelta(months=-1)

            _, num_days = calendar.monthrange(prev_month.year, prev_month.month)

            date_from = prev_month.replace(day=1)
            date_to = date(prev_month.year, prev_month.month, num_days)

            for member in member_ids:
                contribution_id = self.env['member.contribution'].search([('member_account_id','=',member.id),
                                                                          ('date','>=', date_from),
                                                                          ('date','<=', date_to),
                                                                          ('state','=', 'validate'),
                                                                          ])

                if contribution_id:
                    pass
                else:
                    self.create({
                        'type': 'late_contribution',
                        'date': date_today,
                        'name': member.id,
                        'amount': company_id.contribution_late_fee,
                    })

    def action_cron_expired_loan_fee(self):
        date_today = datetime.today().date()
        company_id = self.env.company

        expired_loan_ids = self.env['loan.account'].search([
            ('date_to', '<=', date_today),
            ('state', '=', 'approved'),
        ])

        for rec in expired_loan_ids:
            if rec.date_to.day == date_today.day:
                self.create({
                    'type': 'loan_expired',
                    'date': date_today,
                    'name': rec.guarantor_id.id,
                    'loan_id': rec.id,
                    'amount': company_id.contribution_late_fee,
                })

                rec.write({
                    'state': 'expired'
                })



