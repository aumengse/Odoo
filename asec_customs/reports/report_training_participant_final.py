from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import pytz, calendar, math

class ReportTrainingParticipantFinal(models.AbstractModel):
    _name = 'report.asec_customs.report_training_participant_final'
    _description = 'ReportTraining Participant Final'

    def _get_report_values(self, docids, data=None):
        docs = self.env['training.program'].browse(docids)

        records = []
        for rec in docs.mapped('employee_ids').sorted(key=lambda r: r.name):
            document_ids = self.env['training.program.document'].search([('employee_id', '=', rec.id)])
            document_local_clearance = document_ids.filtered(lambda r: r.document_type_id.type == 'local_clearance')
            document_ots = document_ids.filtered(lambda r: r.document_type_id.type == 'ots_id')
            document_certificate = document_ids.filtered(lambda r: r.document_type_id.type == 'certificate')
            document_ishihara_test = document_ids.filtered(lambda r: r.document_type_id.type == 'ishihara_tes')
            document_coe = document_ids.filtered(lambda r: r.document_type_id.type == 'coe')

            records.append({
                'employee_id': rec,
                'document_local_clearance': document_local_clearance,
                'document_ots': document_ots,
                'document_certificate': document_certificate,
                'document_ishihara_test': document_ishihara_test,
                'document_coe': document_coe,
            })

        return {
            'doc_ids': docids,
            'docs': docs,
            'records': records,
            'type': type,
            'report_type': data.get('report_type') if data else '',
        }