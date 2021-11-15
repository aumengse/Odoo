from odoo import api, fields, models
from odoo.addons.osynx_loan.reports.report_loan_summary import ReportLoanSummary
from datetime import datetime, timedelta

class ReportMemberStatement(models.AbstractModel):
    _name = 'report.osynx_loan.report_member_statements'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['member.account'].browse(docids)

        dividend = ReportLoanSummary.get_actual_dividend(self,docs.date_to)
        member_earning = sum(r.member_earning for r in self.env['loan.account.payment'].search([
            ('member_id','=',docs.id),
            ('date','<=',docs.date_to),
            ('state','=','validate'),
            ('member_earning','!=',0),
        ]))

        return {
            'doc_ids': docids,
            'doc_model': docs._name,
            'docs': docs,
            'dividend': dividend,
            'member_earning': member_earning,
        }