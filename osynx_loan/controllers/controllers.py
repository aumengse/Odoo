from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from werkzeug.exceptions import NotFound


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

        return request.render("osynx_loan.submit_member_contribution", {
            'job': [],
        })
