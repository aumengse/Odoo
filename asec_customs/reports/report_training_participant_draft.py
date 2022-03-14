from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import pytz, calendar, math

class ReportTrainingParticipantDraft(models.AbstractModel):
    _name = 'report.asec_customs.report_training_participant_draft'
    _description = 'ReportTraining Participant Draft'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        user_tz = pytz.timezone(self.env.user.tz or 'UTC')

        records = []
        domain = []
        if docs.department_ids:
            domain.append(('department_id','in', docs.department_ids.ids))
        if docs.employee_ids:
            domain.append(('employee_id', 'in', docs.employee_ids.ids))
        if docs.location_id:
            domain.append(('employee_id.location_id', '=', docs.location_id.id))



        employee_ids = self.env['hr.attendance'].search(domain).mapped('employee_id').sorted(
                key=lambda r: str(r.last_name) or str(r.first_name) or str(r.middles_name))

        if docs.is_alias:
            employee_ids = self.env['hr.attendance'].search(domain).mapped('employee_id').sorted(
                key=lambda r: str(r.alias))

        records = docs.get_attendance_data(employee_ids)

        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': docs,
            'period': "%s - %s" %(docs.date_from.strftime('%m/%d/%Y'),docs.date_to.strftime('%m/%d/%Y')),
            'records': records,
            'type': type,
            'report_type': data.get('report_type') if data else '',
        }