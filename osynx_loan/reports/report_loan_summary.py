from odoo import models, fields, api, _
from odoo.addons.osynx_loan.reports.report_summary import ReportSummary

class ReportLoanSummary(models.AbstractModel):
    _name = 'report.osynx_loan.report_loan_summary'
    _description = 'Loan Summary'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        loan_ids = self.env['loan.account'].search([
            ('state','!=','paid'),
            # ('date_to','<=',docs.date_to),
        ]).sorted(key=lambda r: r.borrower_id.name)

        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': docs,
            'loan_ids': loan_ids,
        }