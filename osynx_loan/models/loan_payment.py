from odoo import models, fields, api

class LoanAccount(models.Model):
    _name = 'loan.account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Loan Account'

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner',string="Guarantor")
    borrower_id = fields.Many2one('res.partner',string="Borrower")
    date_from = fields.Date(string="Start")
    date_to = fields.Date(string="End")
    principal = fields.Float(string="Principal Amount")
    term = fields.Float(string="Term")
    interest = fields.Many2one('loan.interest',string="Interest")
    state = fields.Selection([('draft', "Draft"),
                              ('queue', "On Queue"),
                              ('approve', "Approved")
                              ], default='draft')


    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('loan.account.sequence')
        vals.update({
            'name': name
        })
        res = super(LoanAccount, self).create(vals)
        return res