from odoo import models, fields, api, _
from odoo.addons.osynx_loan.reports.report_summary import ReportSummary

class ReportPayoutSummary(models.AbstractModel):
    _name = 'report.osynx_loan.report_payout_summary'
    _description = 'Payout Summary'

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

            total_payment += sum(payment.amount for payment in
                                 loan.payment_ids.filtered(lambda r: r.payment_type not in ['penalty']))
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
        if docs.member_ids:
            member_ids = self.env['member.account'].search([('id','in',docs.member_ids.ids)])

        payment_obj = self.env['loan.account.payment']


        records = []
        dividend = ReportSummary.get_actual_dividend(self, docs.date_to)
        dividend_forecasted = ReportSummary.get_forecast_dividend(self, docs)

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
        }