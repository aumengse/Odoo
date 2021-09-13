from odoo import fields, http, _
from odoo.http import request, Controller, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from werkzeug.exceptions import NotFound

import base64

class MemberContributionPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(MemberContributionPortal, self)._prepare_portal_layout_values()
        contribution_count = request.env['member.contribution'].search([])
        values.update({
            'contribution_count': len(contribution_count),
        })
        return values

    @http.route(['/my/contributions', '/my/contribution/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_contributions(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                                search_in='all', groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        contribution_ids = request.env['member.contribution'].search([])

        values.update({
            'page_name': 'contributions',
            'contributions': contribution_ids,
        })
        return request.render("osynx_loan.portal_my_contributions", values)

    @http.route('''/submit/contribution''', type='http', auth="public", website=True, sitemap=True)
    def submit_contribution(self, **kwargs):
        default_partner_id = request.env.user.partner_id

        user_ids = request.env['res.users'].sudo().search([('id','!=', request.env.user.id)])
        partner_ids = user_ids.mapped('partner_id')

        return request.render("osynx_loan.submit_member_contribution", {
            'partner_ids': partner_ids,
            'default_partner_id': default_partner_id,
        })

class LoanPaymentPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(LoanPaymentPortal, self)._prepare_portal_layout_values()
        payment_count = request.env['loan.account.payment'].search([])
        values.update({
            'payment_count': len(payment_count),
        })
        return values

    @http.route(['/my/loanpayments', '/my/loanpayments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_loan_payments(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                                search_in='all', groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        loan_payment_ids = request.env['loan.account.payment'].search([])

        values.update({
            'page_name': 'loan_payments',
            'loan_payments': loan_payment_ids,
        })
        return request.render("osynx_loan.portal_my_loan_payments", values)

    @http.route('''/submit/payment''', type='http', auth="public", website=True, sitemap=True)
    def submit_payment(self, **kwargs):
        default_partner_id = request.env.user.partner_id

        user_ids = request.env['res.users'].sudo().search([('id','!=', request.env.user.id)])
        partner_ids = user_ids.mapped('partner_id')

        return request.render("osynx_loan.submit_member_contribution", {
            'partner_ids': partner_ids,
            'default_partner_id': default_partner_id,
        })

class ContributionForm(Controller):

    @route(['/contribution/form'], type='http', auth='public', website=True)
    def contribution_form(self, redirect=None, **kw):
        # here in kw you can get the inputted value

        contribution_obj = request.env['member.contribution']

        values = {
            'name': request.env['res.partner'].browse(kw.get('partner_id')).id,
            'date': kw.get('date'),
            'amount': kw.get('amount')
        }
        record = contribution_obj.create(
            values
        )

        Attachments = request.env['ir.attachment']
        name = kw.get('attachment').filename
        file = kw.get('attachment')
        attachment = file.read()
        attachment_id = Attachments.sudo().create({
            'name': name,
            # 'datas_fname': name,
            'res_name': name,
            'type': 'binary',
            'res_model': record._name,
            'res_id': record.id,
            'datas': base64.encodebytes(attachment),
        })

        response = request.render("osynx_loan.contribution_success", {})
        return response