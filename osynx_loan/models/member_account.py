import base64

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval

class MemberAccount(models.Model):
    _name = 'member.account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Member Account'
    _rec_name = 'display_name'
    _order = 'display_name'

    display_name = fields.Char(string="Account Name", compute="compute_display_name", store=True)
    name = fields.Char(string="Reference")
    partner_id = fields.Many2one('res.partner',string="Member")
    email = fields.Char(related='partner_id.email')
    mobile = fields.Char(related='partner_id.mobile')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean(string="Active", default=True)
    date_from = fields.Date(string="Start")
    date_to = fields.Date(string="End")
    # line_ids = fields.One2many('member.contribution','member_account_id',string="Contributions")
    payment_ids = fields.One2many('loan.account.payment', 'member_id', string="Payments")
    loan_ids = fields.One2many('loan.account','guarantor_id',string="Loans")
    payment_ids = fields.One2many('loan.account.payment','member_id',string="Payments")
    penalty_ids = fields.One2many('loan.penalty', 'name', string="Penalty")
    total_capital = fields.Float(string="Total Capital", compute='compute_total_capital')
    total_commission = fields.Float(string="Total Commission", compute='compute_total_commission')
    total_dividend = fields.Float(string="Total Dividend", compute='compute_total_dividend')
    total_penalty = fields.Float(string="Total Penalty", compute='compute_total_penalty')
    total_earning = fields.Float(string="Total Earning", compute='compute_total_profit')
    state = fields.Selection([('running', "Running"),
                              ('close', "Closed"),
                              ], default='running', string="State", tracking=True)

    @api.depends('payment_ids')
    def compute_total_capital(self):
        for rec in self:
            rec.total_capital = sum(r.amount for r in self.env['loan.account.payment'].search([
                ('state', '=', 'validate'),
                ('payment_type', 'in', ['contribution']),
                ('member_id', '=', rec.id),
            ]))

            # rec.total_capital = sum(r.amount for r in rec.line_ids.filtered(lambda r:
            #                                                                 r.state == 'validate'))

    @api.depends('payment_ids')
    def compute_total_commission(self):
        for rec in self:
            rec.total_commission = sum(r.total_guarantor_earning for r in rec.loan_ids)

    @api.depends('payment_ids')
    def compute_total_dividend(self):
        for rec in self:
            member_count = self.search_count([])

            rec.total_dividend = 0.00
            if member_count:
                total_payments = sum(r.company_earning for r in self.env['loan.account.payment'].search([('state','=','validate')]))
                rec.total_dividend = total_payments / member_count

    @api.depends('penalty_ids')
    def compute_total_penalty(self):
        for rec in self:
            total_penalty = sum(r.amount for r in self.penalty_ids.search([
                ('state','=','validate'),
                ('type','=','late_contribution'),
            ]))
            rec.total_penalty = total_penalty

    @api.depends('total_capital','total_commission')
    def compute_total_profit(self):
        for rec in self:
            rec.total_earning = rec.total_capital + rec.total_commission + rec.total_dividend

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

    def action_show_contributions(self):
        return {
            'name': _('Contributions'),
            'view_mode': 'tree,form',
            'res_model': 'loan.account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('member_id', '=', self.id),
                       ('payment_type', '=', 'contribution')],
            'context': {
                'default_payment_type': 'contribution',
                'default_member_id': self.id,
            }
        }

    def action_show_payments(self):
        return {
            'name': _('Payments'),
            'view_mode': 'tree,form',
            'res_model': 'loan.account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('member_id', '=', self.id),
                       ('payment_type', 'in', ['principal','interest'])],
            'context': {
                'default_payment_type': 'interest',
                'default_member_id': self.id,
            }
        }

    def action_show_loans(self):
        return {
            'name': _('Loans'),
            'view_mode': 'tree,form',
            'res_model': 'loan.account',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [
                ('guarantor_id', '=', self.id),
            ],
            'context': {
                'default_guarantor_id': self.id,
            }
        }

    def action_show_penalties(self):
        return {
            'name': _('Penalties'),
            'view_mode': 'tree,form',
            'res_model': 'loan.penalty',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [
                ('name', '=', self.id),
            ],
            'context': {
                'name': self.id,
            }
        }

    def action_send(self):
        for member in self:
            report = self.env.ref('osynx_loan.action_report_member_statement_of_account', False)
            pdf_content, content_type = report.sudo()._render_qweb_pdf(member.id)

            pdf_name = _("Member Statement - %s" %member.partner_id.name)
            # Sudo to allow payroll managers to create document.document without access to the
            # application
            attachment = self.env['ir.attachment'].sudo().create({
                'name': pdf_name,
                'type': 'binary',
                'datas': base64.encodebytes(pdf_content),
                'res_model': member._name,
                'res_id': member.id
            })
            # Send email to employees
            template = self.env.ref('osynx_loan.mail_template_member_statement', raise_if_not_found=False)
            if template:
                email_values = {
                    'attachment_ids': attachment,
                }
                template.send_mail(
                    member.id,
                    email_values=email_values,
                    notif_layout='mail.mail_notification_light',
                    force_send=True
                )
