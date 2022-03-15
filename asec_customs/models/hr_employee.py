from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    last_name = fields.Char(string="Last Name")