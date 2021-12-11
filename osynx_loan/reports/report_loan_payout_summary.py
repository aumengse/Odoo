from odoo import models, fields, api, _
from odoo.addons.osynx_loan.reports.report_summary import ReportSummary

class ReportPayoutSummary(models.AbstractModel):
    _name = 'report.osynx_loan.report_payout_summary'
    _description = 'Payout Summary'

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

    def compute_total_earning(self,docs,member,payment_obj,dividend):
        total_contribution = sum(payment.amount for payment in payment_obj.search([
            ('member_id', '=', member.id),
            ('date', '<=', docs.date_to),
            ('state', '=', 'validate'),
            ('payment_type', '=', 'contribution'),
        ]))

        total_dividend = dividend.get('member_dividend')

        total_commission = sum(payment.member_earning for payment in payment_obj.search([
            ('member_id', '=', member.id),
            ('date', '<=', docs.date_to),
            ('state', '=', 'validate'),
            ('payment_type', '=', 'interest'),
            ('member_earning', '!=', 0),
        ]))

        total_earnings = total_contribution + total_dividend + total_commission

        return {
            'total_contribution': total_contribution,
            'total_dividend': total_dividend,
            'total_commission': total_commission,
            'total_earnings': total_earnings,
        }

    def compute_total_deductions(self,docs,member,payment_obj,dividend):
        total_loan = 0.00
        total_payment = 0.00
        for loan in member.loan_ids:
            total_loan += loan.total_loan
            total_payment += loan.total_payment
        total_unpaid_loan = total_loan - total_payment

        total_unpaid_penalty = 0.00
        for penalty in member.penalty_ids.filtered(lambda r: r.state != 'paid'):
            total_unpaid_penalty += penalty.amount

        total_deductions = total_unpaid_loan + total_unpaid_penalty
        return {
            'total_unpaid_loan': total_unpaid_loan,
            'total_unpaid_penalty': total_unpaid_penalty,
            'total_deductions': total_deductions,
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        member_ids = self.env['member.account'].search([])
        payment_obj = self.env['loan.account.payment']


        records = []
        dividend = ReportSummary.get_actual_dividend(self, docs.date_to)

        for member in member_ids:
            earnings = self.compute_total_earning(docs, member, payment_obj, dividend)
            deductions = self.compute_total_deductions(docs, member, payment_obj, dividend)

            total_payout = earnings.get('total_earnings') - deductions.get('total_deductions')

            records.append({
                'account_number': member.name,
                'account_name': member.partner_id.name,
                'total_contribution': earnings.get('total_contribution'),
                'total_dividend': earnings.get('total_dividend'),
                'total_commission': earnings.get('total_commission'),
                'total_earnings': earnings.get('total_earnings'),
                'total_unpaid_loan': deductions.get('total_unpaid_loan'),
                'total_unpaid_penalty': deductions.get('total_unpaid_penalty'),
                'total_deductions': deductions.get('total_deductions'),
                'total_payout': total_payout,
            })

        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': docs,
            'records': records,
            # 'summary_loanable': self.get_summary_loanable(docs),
            # 'summary_receivable': self.get_summary_receivable(docs),
            # 'summary_profit_forecast': self.get_summary_profit_forecast(docs),
            # 'dividend_forecast': self.get_forecast_dividend(docs),
            # 'dividend_actual': self.get_actual_dividend(docs.date_to),
            # 'report_type': data.get('report_type') if data else '',
        }