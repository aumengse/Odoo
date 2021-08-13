from odoo import models, fields, api

class MemberContribution(models.Model):
    _name = 'member.contribution'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Member Contributions'

    name = fields.Many2one('res.partner',string="Name",default=lambda self: self.env.user.partner_id.id)
    member_account_id = fields.Many2one('member.account', string="Account")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        related='company_id.currency_id', readonly=True)
    date = fields.Date(string="Date")
    amount = fields.Monetary(currency_field='currency_id')
    state = fields.Selection([('draft',"Draft"),
                              ('process', "Processing"),
                              ('validate', "Validated")
                              ],default='draft')
