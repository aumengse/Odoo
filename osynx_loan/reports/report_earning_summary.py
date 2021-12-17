from odoo import models, fields, api, _
from odoo.addons.osynx_loan.reports.report_summary import ReportSummary

class ReportEarningSummary(models.AbstractModel):
    _name = 'report.osynx_loan.report_earning_summary'
    _description = 'Earning Summary'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        loan_ids = self.env['loan.account'].search([
            # ('date_to','<=',docs.date_to),
        ]).sorted(key=lambda r: r.borrower_id.name)


        interest_ids = loan_ids.mapped('interest_id').sorted(key=lambda r: r.name)

        interests = []
        total_guarantor_earning = 0.00
        total_company_earning = 0.00

        for interest in interest_ids:
            company_earning = sum(loan.total_company_earning for loan in  loan_ids.filtered(lambda r: r.interest_id.id == interest.id))
            guarantor_earning = sum(loan.total_guarantor_earning for loan in  loan_ids.filtered(lambda r: r.interest_id.id == interest.id))

            total_company_earning += company_earning
            total_guarantor_earning += guarantor_earning

            interests.append({
                'name': "Total %s Interest" %(interest.name),
                'total_company_earning': company_earning,
                'total_guarantor_earning': guarantor_earning,
            })

        member_count = self.env['member.account'].search_count([])

        dividend = ReportSummary.get_actual_dividend(self, docs.date_to)

        # dividend = total_company_earning / member_count

        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': docs,
            'loan_ids': loan_ids,
            'interests': interests,
            'total_company_earning': total_company_earning,
            'member_count': member_count,
            'dividend': dividend.get('member_dividend'),
        }