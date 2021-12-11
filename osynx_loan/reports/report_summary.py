from odoo import models, fields, api, _

class ReportSummary(models.AbstractModel):
    _name = 'report.osynx_loan.report_summary'
    _description = 'Employee Loan Summary'

    def get_actual_dividend(self,date_to):
        nonmember_interest_id = self.env.ref('osynx_loan.loan_interest_nonmember')
        total_member = self.env['member.account'].search_count([])
        total_penalty = sum(
            r.amount for r in self.env['loan.account.payment'].search([
                ('state', '=', 'validate'),
                ('date', '<=', date_to),
                ('payment_type', '=', 'penalty'),
                ('loan_id.interest_id.type', '=', 'member'),
            ]))

        total_interest_member = sum(
            r.amount for r in self.env['loan.account.payment'].search([
                ('state', '=', 'validate'),
                ('date', '<=', date_to),
                ('payment_type', '=', 'interest'),
                ('loan_id.interest_id.type', '=', 'member'),
            ]))
        total_interest_nonmember = sum(
            r.amount for r in self.env['loan.account.payment'].search([
                ('state', '=', 'validate'),
                ('date', '<=', date_to),
                ('payment_type', '=', 'interest'),
                ('loan_id.interest_id.type', '=', 'nonmember'),
            ])) * (nonmember_interest_id.coop_rate / 100)

        total_interest_guarantor = sum(
            r.amount for r in self.env['loan.account.payment'].search([
                ('state', '=', 'validate'),
                ('date', '<=', date_to),
                ('payment_type', '=', 'interest'),
                ('loan_id.interest_id.type', '=', 'nonmember'),
            ])) * (nonmember_interest_id.guarantor_rate / 100)

        total_interest = total_interest_member + total_interest_nonmember + total_interest_guarantor
        total_coop_earning = (total_interest + total_penalty) - total_interest_guarantor
        member_dividend = total_coop_earning / total_member

        dividend_actual = {
            'total_interest_member': total_interest_member,
            'total_interest_nonmember': total_interest_nonmember,
            'total_interest_guarantor': total_interest_guarantor,
            'total_coop_earning': total_coop_earning,
            'total_interest': total_interest,
            'total_penalty': total_penalty,
            'total_member': total_member,
            'member_dividend': member_dividend,
        }

        return dividend_actual

    def get_forecast_dividend(self,docs):
        nonmember_interest_id = self.env.ref('osynx_loan.loan_interest_nonmember')
        total_member = self.env['member.account'].search_count([])

        total_penalty = sum(r.amount for r in self.env['loan.penalty'].search([
            ('state', '=', 'validate'),
            ('date', '<=', docs.date_to),
        ]))

        total_interest_member = sum(
            r.total_interest for r in self.env['loan.account'].search([('interest_id.type', '=', 'member')]))
        total_interest_nonmember = sum(
            r.total_interest for r in self.env['loan.account'].search([('interest_id.type', '=', 'nonmember')])) * (
                                           nonmember_interest_id.coop_rate / 100)
        total_interest_guarantor = sum(
            r.total_interest for r in self.env['loan.account'].search([('interest_id.type', '=', 'nonmember')])) * (
                                           nonmember_interest_id.guarantor_rate / 100)

        dividend_forecast = {
            'total_interest_member': total_interest_member,
            'total_interest_nonmember': total_interest_nonmember,
            'total_interest_guarantor': total_interest_guarantor,
            'total_interest': total_interest_member + total_interest_nonmember + total_interest_guarantor,
            'total_penalty': total_penalty,
            'total_member': total_member,
        }
        return dividend_forecast

    def get_summary_profit_forecast(self,docs):
        total_member = self.env['member.account'].search_count([])
        total_loans = sum(r.total_loan for r in self.env['loan.account'].search([]))
        total_principal = sum(r.principal for r in self.env['loan.account'].search([]))
        total_interest_profit = total_loans - total_principal

        total_penalty = sum(r.amount for r in self.env['loan.penalty'].search([
            ('state', '=', 'validate'),
            ('date', '<=', docs.date_to),
        ]))
        total_forecast_profit = total_interest_profit + total_penalty

        summary_profit_forecast = {
            'total_principal': total_principal,
            'total_loans': total_loans,
            'total_interest_profit': total_interest_profit,
            'total_penalty': total_penalty,
            'total_forecast_profit': total_forecast_profit,
            'total_member': total_member,
            'forecasted_member_dividend': total_forecast_profit / total_member,
        }
        return summary_profit_forecast

    def get_summary_receivable(self,docs):
        total_principal = sum(r.principal for r in self.env['loan.account'].search([]))
        total_interest = sum(r.total_interest for r in self.env['loan.account'].search([]))
        total_loans = sum(r.total_loan for r in self.env['loan.account'].search([]))

        total_payments = sum(r.amount for r in self.env['loan.account.payment'].search([
            ('state', '=', 'validate'),
            ('date', '<=', docs.date_to),
            ('payment_type', 'in', ['interest', 'principal', 'penalty']),
        ]))

        summary_receivable = {
            'total_principal': total_principal,
            'total_interest': total_interest,
            'total_loans': total_loans,
            'total_payments': total_payments,
            'total_receivable': total_loans - total_payments,
        }
        return summary_receivable

    def get_summary_loanable(self,docs):
        total_contribution = sum(r.amount for r in self.env['loan.account.payment'].search([
            ('state', '=', 'validate'),
            ('date', '<=', docs.date_to),
            ('payment_type', 'in', ['contribution']),
        ]))
        total_payments = sum(r.amount for r in self.env['loan.account.payment'].search([
            ('state', '=', 'validate'),
            ('date', '<=', docs.date_to),
            ('payment_type', 'in', ['interest', 'principal', 'penalty']),
        ]))

        total_contri_payment = total_contribution + total_payments
        total_loans = sum(r.total_loan for r in self.env['loan.account'].search([]))
        total_principal = sum(r.principal for r in self.env['loan.account'].search([]))

        summary_loanable = {
            'total_contribution': total_contribution,
            'total_payments': total_payments,
            'total_contri_payment': total_contri_payment,
            'total_principal': total_principal,
            'total_loanable': total_contri_payment - total_loans,
        }
        return summary_loanable

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': docs,
            'summary_loanable': self.get_summary_loanable(docs),
            'summary_receivable': self.get_summary_receivable(docs),
            'summary_profit_forecast': self.get_summary_profit_forecast(docs),
            'dividend_forecast': self.get_forecast_dividend(docs),
            'dividend_actual': self.get_actual_dividend(docs.date_to),
            'report_type': data.get('report_type') if data else '',
        }