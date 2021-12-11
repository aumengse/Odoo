from odoo import models, fields, api
from datetime import datetime, date, timedelta
import calendar

class LoanReportWizard(models.TransientModel):
    _name = 'loan.report.wizard'
    _description = 'Loan Report Wizard'

    name = fields.Selection([
        ('summary','Summary Report'),
        ('payout','Payout Summary Report'),
    ], string="Reports", required=True)
    date_to = fields.Date(string="Date To", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    def generate_summary_report(self):
        data = {
            'model': 'loan.report.wizard',
            'form': self.read()[0],
        }
        if self.name == 'summary':
            return self.env.ref('osynx_loan.action_report_summary').report_action(self, data=data)
        elif self.name == 'payout':
            return self.env.ref('osynx_loan.action_report_payout_summary').report_action(self, data=data)