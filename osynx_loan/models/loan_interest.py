from odoo import models, fields, api

class LoanInterest(models.Model):
    _name = 'loan.interest'
    _description = 'Loan Interest'

    name = fields.Char(string="Name")
    interest = fields.Float(string="Interest")
    coop_rate = fields.Float(string="Coop Rate")
    guarantor_rate = fields.Float(string="Guarantor Rate")
    type = fields.Selection([('member', "Member"),
                              ('nonmember', "Non-Member"),
                              ], string="Type")
