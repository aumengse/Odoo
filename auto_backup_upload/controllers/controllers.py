# -*- coding: utf-8 -*-
from odoo import http

# class AutoBackupUpload(http.Controller):
#     @http.route('/auto_backup_upload/auto_backup_upload/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/auto_backup_upload/auto_backup_upload/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('auto_backup_upload.listing', {
#             'root': '/auto_backup_upload/auto_backup_upload',
#             'objects': http.request.env['auto_backup_upload.auto_backup_upload'].search([]),
#         })

#     @http.route('/auto_backup_upload/auto_backup_upload/objects/<model("auto_backup_upload.auto_backup_upload"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('auto_backup_upload.object', {
#             'object': obj
#         })