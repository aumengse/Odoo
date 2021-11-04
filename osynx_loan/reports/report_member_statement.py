from odoo import api, fields, models, _

class ReportMemberStatement(models.AbstractModel):
    _name = 'report.osynx_loan.report_member_statement'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['member.account'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': docs._name,
            'docs': docs,
        }