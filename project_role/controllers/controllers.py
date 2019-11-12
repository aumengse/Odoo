# -*- coding: utf-8 -*-
from odoo import http

# class ProjectRole(http.Controller):
#     @http.route('/project_role/project_role/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_role/project_role/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_role.listing', {
#             'root': '/project_role/project_role',
#             'objects': http.request.env['project_role.project_role'].search([]),
#         })

#     @http.route('/project_role/project_role/objects/<model("project_role.project_role"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_role.object', {
#             'object': obj
#         })