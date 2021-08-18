from odoo import models, fields, api

class MemberAccount(models.Model):
    _name = 'member.account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Member Account'
    _rec_name = 'display_name'

    display_name = fields.Char(string="Account Name", compute="compute_display_name")
    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner',string="Member")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    date_from = fields.Date(string="Start")
    date_to = fields.Date(string="End")
    active = fields.Boolean(string="Active", default=True)
    line_ids = fields.One2many('member.contribution','member_account_id',string="Contributions")
    loan_ids = fields.One2many('loan.account','guarantor_id',string="Loans")
    total_capital = fields.Float(string="Total Capital", compute='compute_total_capital')
    total_commission = fields.Float(string="Total Commission", compute='compute_total_commission')
    total_earning = fields.Float(string="Total Earning", compute='compute_total_profit')

    @api.depends('line_ids')
    def compute_total_capital(self):
        for rec in self:
            rec.total_capital = sum(r.amount for r in rec.line_ids)\

    @api.depends('loan_ids')
    def compute_total_commission(self):
        for rec in self:
            rec.total_commission = sum(r.total_guarantor_earning for r in rec.loan_ids)\

    @api.depends('total_capital','total_commission')
    def compute_total_profit(self):
        for rec in self:
            rec.total_earning = rec.total_capital + rec.total_commission

    @api.depends('name','partner_id')
    def compute_display_name(self):
        for rec in self:
            rec.display_name = "%s - %s" %(rec.partner_id.name,rec.name)

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('member.account.sequence')
        vals.update({
            'name': name
        })
        res = super(MemberAccount, self).create(vals)
        return res