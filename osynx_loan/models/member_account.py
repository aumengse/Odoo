from odoo import models, fields, api

class MemberAccount(models.Model):
    _name = 'member.account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Member Account'

    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner',string="Member")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    date_from = fields.Date(string="Start")
    date_to = fields.Date(string="End")
    active = fields.Boolean(string="Active", default=True)
    line_ids = fields.One2many('member.contribution','member_account_id',string="Contributions")


    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('member.account.sequence')
        vals.update({
            'name': name
        })
        res = super(MemberAccount, self).create(vals)
        return res