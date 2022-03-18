from odoo import models, fields, api, _

class TrainingProgramDocumentType(models.Model):
    _name = 'training.program.document.type'
    _description = 'Training Document Type'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    description = fields.Char(string="Description")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    type = fields.Selection([
        ('security_licensed', 'Security Licensed'),
        ('nbi_clearance', 'NBI Clearance'),
        ('police_clearance', 'Police Clearance'),
        ('local_clearance', 'Local Clearance'),
        ('ishihara_test', 'Ishihara Test Result'),
        ('coe', 'Certificate of Employment'),
        ('certificate', 'Certificates'),
        ('ots', 'OTS Identification'),
        ('other', 'Other')], string='Type',
        default='other', required=True)