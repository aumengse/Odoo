# -*- coding: utf-8 -*-
# from odoo import http


# class /opt/test/asecCustoms(http.Controller):
#     @http.route('//opt/test/asec_customs//opt/test/asec_customs', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('//opt/test/asec_customs//opt/test/asec_customs/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('/opt/test/asec_customs.listing', {
#             'root': '//opt/test/asec_customs//opt/test/asec_customs',
#             'objects': http.request.env['/opt/test/asec_customs./opt/test/asec_customs'].search([]),
#         })

#     @http.route('//opt/test/asec_customs//opt/test/asec_customs/objects/<model("/opt/test/asec_customs./opt/test/asec_customs"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('/opt/test/asec_customs.object', {
#             'object': obj
#         })
