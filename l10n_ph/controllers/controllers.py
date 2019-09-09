# -*- coding: utf-8 -*-
from odoo import http

# class PhpLocalization(http.Controller):
#     @http.route('/etsi_localization/etsi_localization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/etsi_localization/etsi_localization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('etsi_localization.listing', {
#             'root': '/etsi_localization/etsi_localization',
#             'objects': http.request.env['etsi_localization.etsi_localization'].search([]),
#         })

#     @http.route('/etsi_localization/etsi_localization/objects/<model("etsi_localization.etsi_localization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('etsi_localization.object', {
#             'object': obj
#         })