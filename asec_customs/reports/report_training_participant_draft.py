import datetime

from odoo import models, fields, api, _

class ReportTrainingParticipantDraft(models.AbstractModel):
    _name = 'report.asec_customs.report_training_participant_draft'
    _description = 'ReportTraining Participant Draft'

    def _get_report_values(self, docids, data=None):
        docs = self.env['training.program'].browse(docids)

        records = []

        for rec in docs.mapped('participant_ids').sorted(key=lambda r: r.name):
            # complete_count = 0
            #
            # document_ids = self.env['training.program.document'].search([('employee_id','=',rec.id)])
            # document_security_licensed = document_ids.filtered(lambda r: r.document_type_id.type == 'security_licensed')
            # document_nbi_clearance = document_ids.filtered(lambda r: r.document_type_id.type == 'nbi_clearance')
            # document_police_clearance = document_ids.filtered(lambda r: r.document_type_id.type == 'police_clearance')
            # document_ishihara_test = document_ids.filtered(lambda r: r.document_type_id.type == 'ishihara_tes')
            # document_coe = document_ids.filtered(lambda r: r.document_type_id.type == 'coe')
            #
            # if document_security_licensed:
            #     complete_count += 1
            # else:
            #     if document_nbi_clearance or document_police_clearance:
            #         complete_count += 1
            #
            # if document_coe:
            #     complete_count += 1
            # if document_ishihara_test:
            #     complete_count += 1


            records.append({
                'employee_id': rec,
                # 'document_security_licensed': document_security_licensed,
                # 'document_nbi_clearance':  document_nbi_clearance,
                # 'document_police_clearance': document_police_clearance,
                # 'document_ishihara_test': document_ishihara_test,
                # 'document_coe': document_coe,
                # 'remark': "Completed" if complete_count >= 3 else "Incomplete"
            })

        return {
            'doc_ids': docids,
            'docs': docs,
            'date_generated': datetime.datetime.today(),
            'records': records,
            'type': type,
            'report_type': data.get('report_type') if data else '',
        }
