from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from collections import OrderedDict
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.tools import date_utils, groupby as groupbyelem
from operator import itemgetter

from odoo.osv.expression import OR
from odoo.addons.portal.controllers.mail import _message_post_helper


class MemberContributionPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(MemberContributionPortal, self)._prepare_portal_layout_values()
        contribution_count = request.env['member.contribution'].search([])
        values.update({
            'contribution_count': contribution_count,
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
