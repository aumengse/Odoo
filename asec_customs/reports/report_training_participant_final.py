from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import pytz, calendar, math

class ReportTrainingParticipantFinal(models.AbstractModel):
    _name = 'report.asec_customs.report_training_participant_final'
    _description = 'ReportTraining Participant Final'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        user_tz = pytz.timezone(self.env.user.tz or 'UTC')

        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': docs,
            'period': "%s - %s" %(docs.date_from.strftime('%m/%d/%Y'),docs.date_to.strftime('%m/%d/%Y')),
            'type': type,
            'report_type': data.get('report_type') if data else '',
        }