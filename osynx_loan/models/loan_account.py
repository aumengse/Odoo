from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime

class LoanAccount(models.Model):
    _name = 'loan.account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Loan Account'

    _rec_name = 'display_name'

    display_name = fields.Char(string="Account Name", compute="compute_display_name", store=True)
    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        related='company_id.currency_id', readonly=True)

    guarantor_id = fields.Many2one('member.account',string="Guarantor")
    borrower_id = fields.Many2one('res.partner',string="Borrower")
    date_from = fields.Date(string="Start")
    date_to = fields.Date(string="End", compute='compute_date_to')
    principal = fields.Monetary(string="Principal Amount", currency_field='currency_id')
    term = fields.Integer(string="Term")
    interest_id = fields.Many2one('loan.interest',string="Interest Rate")
    monthly_interest = fields.Monetary(string="Monthly Interest", currency_field='currency_id', compute='compute_interest')
    total_interest = fields.Monetary(string="Total Interest", currency_field='currency_id', compute='compute_interest')

    coop_earning = fields.Monetary(string="Company Earning", currency_field='currency_id', compute='compute_interest')
    guarantor_earning = fields.Monetary(string="Guarantor Earning", currency_field='currency_id', compute='compute_interest')
    state = fields.Selection([('draft', "Draft"),
                              ('queue', "On Queue"),
                              ('approve', "Approved"),
                              ('paid', "Fully Paid")
                              ], default='draft', string="State", tracking=True)
    line_ids = fields.One2many('loan.account.line','loan_id',string="Loan Schedule")
    payment_ids = fields.One2many('loan.account.payment', 'loan_id', string="Loan Payment")
    total_loan = fields.Monetary(string="Total Loan", currency_field='currency_id', compute='compute_totals')
    total_payment = fields.Monetary(string="Total Payment", currency_field='currency_id', compute='compute_totals')
    total_balance = fields.Monetary(string="Balance", currency_field='currency_id', compute='compute_totals')
    total_company_earning = fields.Monetary(string="Total Company Earning", currency_field='currency_id', compute='compute_total_earning')
    total_guarantor_earning = fields.Monetary(string="Total Guarantor Earning", currency_field='currency_id', compute='compute_total_earning')

    @api.onchange('borrower_id')
    def onchange_borrower_id(self):
        member_id = self.env['member.account'].search([('partner_id', '=', self.borrower_id.id)])
        if member_id:
            interest_id = self.env['loan.interest'].search([('type','=','member')],limit=1)
        else:
            interest_id = self.env['loan.interest'].search([('type', '=', 'nonmember')], limit=1)
        self.interest_id = interest_id.id

    @api.depends('date_from', 'term')
    def compute_date_to(self):
        for rec in self:
            rec.date_to = False
            if rec.date_from:
                rec.date_to = rec.date_from + relativedelta(months=rec.term)

    @api.depends('principal', 'interest_id')
    def compute_interest(self):
        for rec in self:
            rec.monthly_interest = (rec.principal * (rec.interest_id.interest / 100))
            rec.coop_earning = (rec.principal * (rec.interest_id.coop_rate / 100))
            rec.guarantor_earning = (rec.principal * (rec.interest_id.guarantor_rate / 100))
            rec.total_interest = rec.monthly_interest * rec.term

    @api.depends('line_ids')
    def compute_totals(self):
        for rec in self:
            rec.total_loan = sum(r.amount for r in rec.line_ids)
            rec.total_payment = sum(r.amount for r in rec.payment_ids.filtered(lambda r: r.state == 'validate'))
            rec.total_balance = rec.total_loan - rec.total_payment

            if rec.state != 'paid':
                if rec.total_balance == 0.00:
                    rec.state = 'paid'

    @api.depends('payment_ids')
    def compute_total_earning(self):
        for rec in self:
            rec.total_guarantor_earning = sum(r.member_earning for r in rec.payment_ids)
            rec.total_company_earning = sum(r.company_earning for r in rec.payment_ids)

    @api.depends('name', 'borrower_id')
    def compute_display_name(self):
        for rec in self:
            rec.display_name = "%s - %s" % (rec.borrower_id.name, rec.name)

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('loan.account.sequence')
        vals.update({
            'name': name
        })
        res = super(LoanAccount, self).create(vals)
        return res

    def action_compute_installment(self):
        self.line_ids.unlink()
        lines = []
        date_from = self.date_from
        for rec in range(self.term):
            date_from += relativedelta(months=1)

            val = (0,0, {
                'date': date_from,
                'amount': self.monthly_interest,
                'company_earning': self.coop_earning,
                'guarantor_earning': self.guarantor_earning,
                'description': "Monthly Interest",

            })
            lines.append(val)

        principal_val = (0, 0, {
            'date': date_from,
            'amount': self.principal,
            'description': 'Principal Amount',
        })
        lines.append(principal_val)
        self.line_ids = lines

    def action_queue(self):
        self.state = 'queue'

    def action_approve(self):
        for rec in self:
            rec.state = 'approve'

class LoanAccountLine(models.Model):
    _name = 'loan.account.line'
    _description = 'Loan Account Line'

    name = fields.Date(string="Name", related='date')
    date = fields.Date(string="Due Date")
    amount = fields.Float(string="Amount")
    company_earning = fields.Float(string="Company")
    guarantor_earning = fields.Float(string="Guarantor")
    description = fields.Char(string="Description")
    state = fields.Selection([('unpaid', "Unpaid"),
                              ('paid', "Paid"),
                              ], default='unpaid', string="State")
    loan_id = fields.Many2one('loan.account', string="Loan")
    borrower_id = fields.Many2one(related='loan_id.borrower_id')
    guarantor_id = fields.Many2one(related='loan_id.borrower_id')
    active = fields.Boolean(string="Active", default=True)


class LoanAccountPayment(models.Model):
    _name = 'loan.account.payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Loan Account Payment'

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    date = fields.Date(string="Date",default=datetime.today().date())
    amount = fields.Float(string="Amount")
    member_id = fields.Many2one('member.account', string="Member", related='loan_id.guarantor_id')
    # loan_id = fields.Many2one('loan.account', string="Loan", domain="[('guarantor_id','=','member_id'),('state','=','approve')]")
    loan_id = fields.Many2one('loan.account', string="Loan")
    currency_id = fields.Many2one(related='loan_id.currency_id')
    principal = fields.Monetary(related='loan_id.principal')
    monthly_interest = fields.Monetary(related='loan_id.monthly_interest')
    total_interest = fields.Monetary(related='loan_id.total_interest')
    company_earning = fields.Float(string="Company Earning", compute='compute_total_earning')
    member_earning = fields.Float(string="Member Earning", compute='compute_total_earning')
    type = fields.Selection([('interest', "Interest"),
                             ('Principal', "Principal"),
                             ], string="Payment Type")
    state = fields.Selection([('draft', "Draft"),
                              ('process', "Processing"),
                              ('validate', "Validated")
                              ], default='draft', tracking=True)

    @api.depends('amount','type')
    def compute_total_earning(self):
        for rec in self:
            rec.member_earning = 0.00
            rec.company_earning = 0.00
            if rec.type == 'interest':
                if rec.loan_id.interest_id.type == 'nonmember':
                    rec.member_earning = (rec.amount * (rec.loan_id.interest_id.guarantor_rate / 100))
                    rec.company_earning = (rec.amount * (rec.loan_id.interest_id.coop_rate / 100))
                else:
                    rec.company_earning = rec.amount

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('loan.account.payment.sequence')
        vals.update({
            'name': name
        })
        res = super(LoanAccountPayment, self).create(vals)
        return res

    def action_submit(self):
        self.state = 'process'

    def action_validate(self):
        for rec in self:
            rec.state = 'validate'