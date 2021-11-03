from odoo import models, fields, api, _

class ReportLoanSummary(models.AbstractModel):
    _name = 'report.osynx_loan.report_loan_summary'
    _description = 'Employee Loan Summary'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        # records = []

        total_contribution = sum(r.amount for r in self.env['member.contribution'].search([
            ('state','=','validate'),
            ('date','<=',docs.date_to),
        ]))
        total_payments = sum(r.amount for r in self.env['loan.account.payment'].search([
            ('state','=','validate'),
            ('date','<=',docs.date_to),
            ('payment_type','in',['interest','principal']),
        ]))

        records = {
            'total_contribution': total_contribution,
            'total_payments': total_payments,
            'total_contri_payment': total_contribution +total_payments,
        }

        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': docs,
            'records': records,
            'report_type': data.get('report_type') if data else '',
        }