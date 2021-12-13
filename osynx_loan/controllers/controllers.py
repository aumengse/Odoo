from odoo import fields, http, _
from odoo.http import request, Controller, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from werkzeug.exceptions import NotFound
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict

import base64

# class MemberContributionPortal(CustomerPortal):
#     def _prepare_portal_layout_values(self):
#         values = super(MemberContributionPortal, self)._prepare_portal_layout_values()
#         contribution_count = request.env['member.contribution'].search([])
#         values.update({
#             'contribution_count': len(contribution_count),
#         })
#         return values
#
#     @http.route(['/my/contributions', '/my/contribution/page/<int:page>'], type='http', auth="user", website=True)
#     def portal_my_contributions(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
#                                 search_in='all', groupby='none', **kw):
#         values = self._prepare_portal_layout_values()
#         contribution_ids = request.env['member.contribution'].search([])
#
#         values.update({
#             'page_name': 'contributions',
#             'contributions': contribution_ids,
#         })
#         return request.render("osynx_loan.portal_my_contributions", values)
#
#     @http.route('''/submit/contribution''', type='http', auth="public", website=True, sitemap=True)
#     def submit_contribution(self, **kwargs):
#         default_partner_id = request.env.user.partner_id
#
#         user_ids = request.env['res.users'].sudo().search([('id','!=', request.env.user.id)])
#         partner_ids = user_ids.mapped('partner_id')
#
#         return request.render("osynx_loan.submit_member_contribution", {
#             'partner_ids': partner_ids,
#             'default_partner_id': default_partner_id,
#         })

class LoanPaymentPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(LoanPaymentPortal, self)._prepare_portal_layout_values()

        domain = [('member_id.partner_id', '=', request.env.user.partner_id.id)]

        payment_count = request.env['loan.account.payment'].search(domain)
        values.update({
            'payment_count': len(payment_count),
        })
        return values

    def _loan_payment_get_page_view_values(self, loan_payment_sudo, access_token, **kwargs):
        values = {
            'page_name': 'loanpayment',
            'payment': loan_payment_sudo,
        }
        return self._get_page_view_values(loan_payment_sudo, access_token, values, 'my_payment_history', False, **kwargs)

    @http.route(['/my/loanpayments', '/my/loanpayments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_loan_payments(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                                search_in='all', groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        loan_payment_sudo = request.env['loan.account.payment'].sudo()

        domain = [('member_id.partner_id', '=', request.env.user.partner_id.id)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
            'old': {'label': _('Oldest'), 'order': 'date asc'},
            'type': {'label': _('Type'), 'order': 'payment_type asc'},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'member_id': {'input': 'member_id', 'label': _('Search in Member')},
        }

        today = fields.Date.today()

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("date", "=", today)]},
            'interest': {'label': _('Interest Payment'), 'domain': [("payment_type", "=", 'interest')]},
            'principal': {'label': _('Principal Payment'), 'domain': [("payment_type", "=", 'principal')]},
            'contribution': {'label': _('Contribution Payment'), 'domain': [("payment_type", "=", 'contribution')]},
            'penalty': {'label': _('Penalty Payment'), 'domain': [("payment_type", "=", 'penalty')]},

        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if search and search_in:
            domain += [('name', 'ilike', search)]

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        payment_count = loan_payment_sudo.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/loanpayments",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby,
                      'groupby': groupby},
            total=payment_count,
            page=page,
            step=self._items_per_page
        )
        loan_payment_ids = loan_payment_sudo.search(domain, order=order, limit=self._items_per_page,
                                                    offset=pager['offset'])

        request.session['my_payment_history'] = loan_payment_ids.ids[:100]

        values.update({
            'loan_payment_ids': loan_payment_ids,
            'page_name': 'loan_payments',
            'default_url': '/my/loanpayments',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            # 'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("osynx_loan.portal_my_loan_payments", values)

    @http.route(['/my/loanpayment/<int:payment_id>'], type='http', auth="public", website=True)
    def portal_my_loan_payment(self, payment_id=None, access_token=None, **kw):
        try:
            loan_payment_sudo = self._document_check_access('loan.account.payment', payment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._loan_payment_get_page_view_values(loan_payment_sudo, access_token, **kw)
        return request.render("osynx_loan.portal_my_loan_payment", values)

    @http.route('''/submit/payment''', type='http', auth="public", website=True, sitemap=True)
    def submit_payment(self, **kwargs):
        default_partner_id = request.env.user.partner_id
        # default_member_id = request.env['member.account'].sudo().search([('partner_id','=',default_partner_id.id)])

        member_ids = request.env['member.account'].sudo().search([('partner_id','=',default_partner_id.id)])
        loan_ids = request.env['loan.account'].sudo().search([
            ('state','not in',['draft','paid']),
            ('guarantor_id','in',member_ids.ids)
        ])

        return request.render("osynx_loan.submit_payment", {
            'member_ids': member_ids,
            'loan_ids': loan_ids,
            # 'default_member_id': default_member_id,
        })

class PaymentForm(Controller):

    @route(['/payment/form'], type='http', auth='public', website=True)
    def contribution_form(self, redirect=None, **kw):
        # here in kw you can get the inputted value

        payment_obj = request.env['loan.account.payment']

        values = {
            'member_id': request.env['res.partner'].browse(kw.get('partner_id')).id,
            'date': kw.get('date'),
            'amount': kw.get('amount'),
            'payment_type': kw.get('payment_type')
        }
        record = payment_obj.create(
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

        response = request.render("osynx_loan.payment_success", {})
        return response