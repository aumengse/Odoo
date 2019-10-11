# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.addons.google_drive.models.google_drive import GoogleDrive
from odoo.exceptions import Warning
import odoo
from odoo.http import content_disposition
import pytz
import requests
import logging
_logger = logging.getLogger(__name__)

from ftplib import FTP
import os
import datetime

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib
import time
import base64
import socket
import json


try:
    import paramiko
except ImportError:
    raise ImportError(
        'This module needs paramiko to automatically write backups to the FTP through SFTP. Please install paramiko on your system. (sudo pip3 install paramiko)')


def execute(connector, method, *args):
    res = False
    try:
        res = getattr(connector, method)(*args)
    except socket.error as error:
        _logger.critical('Error while executing the method "execute". Error: ' + str(error))
        raise error
    return res


class DbBackup(models.Model):
    _name = 'db.backup'
    _description = 'Backup configuration record'

    @api.multi
    def get_db_list(self, host, port, context={}):
        uri = 'http://' + host + ':' + port
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        db_list = execute(conn, 'list')
        return db_list

    @api.multi
    def _get_db_name(self):
        dbName = self._cr.dbname
        return dbName

    # Columns for local server configuration
    host = fields.Char('Host', required=True, default='localhost')
    port = fields.Char('Port', required=True, default=8069)
    name = fields.Char('Database', required=True, help='Database you want to schedule backups for',
                       default=_get_db_name)
    folder = fields.Char('Backup Directory', help='Absolute path for storing the backups', required='True',
                         default='/odoo/backups')
    backup_type = fields.Selection([('zip', 'Zip'), ('dump', 'Dump')], 'Backup Type', required=True, default='zip')
    autoremove = fields.Boolean('Auto. Remove Backups',
                                help='If you check this option you can choose to automaticly remove the backup after xx days')
    days_to_keep = fields.Integer('Remove after x days',
                                  help="Choose after how many days the backup should be deleted. For example:\nIf you fill in 5 the backups will be removed after 5 days.",
                                  required=True)

    # Columns fro Google Drive
    is_upload = fields.Boolean('Upload to Google Drive',
                               help="If you check this option you can specify the details needed to upload to google drive.")
    drive_folder_id = fields.Char(string='Folder ID',
                                  help="make a folder on drive in which you want to upload files; then open that folder; the last thing in present url will be folder id")
    gdrive_email_notif_ids = fields.Many2many('res.users', string="Person to Notify")
    drive_autoremove = fields.Boolean('Auto. Remove Uploaded Backups',
                                      help='If you check this option you can choose to automaticly remove the backup after xx days')

    drive_to_remove = fields.Integer('Remove after x days',
                                     help="Choose after how many days the backup should be deleted. For example:\nIf you fill in 5 the backups will be removed after 5 days.",
                                    )

    @api.depends('google_drive_authorization_code')
    def _compute_drive_uri(self):
        google_drive_uri = self.env['google.service']._get_google_token_uri('drive', scope=self.env[
            'google.drive.config'].get_google_scope())
        for config in self:
            config.google_drive_uri = google_drive_uri

    def set_values(self):
        params = self.env['ir.config_parameter'].sudo()
        authorization_code_before = params.get_param('google_drive_authorization_code')
        super(DbBackup, self).set_values()
        authorization_code = self.google_drive_authorization_code
        refresh_token = False
        if authorization_code and authorization_code != authorization_code_before:
            refresh_token = self.env['google.service'].generate_refresh_token('drive', authorization_code)
        params.set_param('google_drive_refresh_token', refresh_token)

    @api.multi
    def _check_db_exist(self):
        self.ensure_one()

        db_list = self.get_db_list(self.host, self.port)
        if self.name in db_list:
            return True
        return False

    _constraints = [(_check_db_exist, _('Error ! No such database exists!'), [])]


    @api.model
    def schedule_backup(self):
        conf_ids = self.search([])

        for rec in conf_ids:
            db_list = self.get_db_list(rec.host, rec.port)

            if rec.name in db_list:
                try:
                    if not os.path.isdir(rec.folder):
                        os.makedirs(rec.folder)
                except:
                    raise
                # Create name for dumpfile.
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
                date_today = pytz.utc.localize(datetime.datetime.today()).astimezone(user_tz)
                bkp_file = '%s_%s.%s' % (rec.name,date_today.strftime('%Y-%m-%d_%H_%M_%S'), rec.backup_type)

                file_path = os.path.join(rec.folder, bkp_file)
                uri = 'http://' + rec.host + ':' + rec.port
                conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
                bkp = ''
                try:
                    # try to backup database and write it away
                    fp = open(file_path, 'wb')
                    odoo.service.db.dump_db(rec.name, fp, rec.backup_type)
                    fp.close()
                except Exception as error:
                    _logger.debug(
                        "Couldn't backup database %s. Bad database administrator password for server running at http://%s:%s" % (
                        rec.name, rec.host, rec.port))
                    _logger.debug("Exact error from the exception: " + str(error))
                    continue

            else:
                _logger.debug("database %s doesn't exist on http://%s:%s" % (rec.name, rec.host, rec.port))

            """
            Remove all old files (on local server) in case this is configured..
            """
            if rec.autoremove:
                dir = rec.folder
                # Loop over all files in the directory.
                for f in os.listdir(dir):
                    fullpath = os.path.join(dir, f)
                    # Only delete the ones wich are from the current database
                    # (Makes it possible to save different databases in the same folder)
                    if rec.name in fullpath:
                        timestamp = os.stat(fullpath).st_ctime
                        createtime = datetime.datetime.fromtimestamp(timestamp)
                        now = datetime.datetime.now()
                        delta = now - createtime
                        if delta.days >= rec.days_to_keep:
                            # Only delete files (which are .dump and .zip), no directories.
                            if os.path.isfile(fullpath) and (".dump" in f or '.zip' in f):
                                _logger.info("Delete local out-of-date file: " + fullpath)
                                os.remove(fullpath)

            self.google_drive_upload(rec, file_path, bkp_file)

    @api.multi
    def google_drive_upload(self, rec, file_path, bkp_file):
        g_drive = self.env['google.drive.config']
        access_token = GoogleDrive.get_access_token(g_drive)
        # GOOGLE DRIVE UPLOAP
        if rec.is_upload:
            headers = {"Authorization": "Bearer %s" % (access_token)}
            para = {
                "name": "%s" % (str(bkp_file)),
                "parents": ["%s" % (str(rec.drive_folder_id))]
            }
            files = {
                'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
                'file': open("%s" % (str(file_path)), "rb")
            }
            r = requests.post(
                "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                headers=headers,
                files=files
            )

            # SENDING EMAIL NOTIFICATION
            if r.status_code == 200:
                email_to = ""
                for record in rec.gdrive_email_notif_ids.mapped('login'):
                    email_to += record + ','

                notification_template = self.env['ir.model.data'].sudo().get_object('auto_backup_upload',
                                                                                    'email_google_drive_upload')
                values = notification_template.generate_email(self.id)
                values['email_from'] = self.env['res.users'].browse(self.env.uid).company_id.email
                values['email_to'] = email_to
                values['subject'] = "Google Drive Upload Successful"
                values['body_html'] = "<h3>Backup Successfully Uploaded!</h3>" \
                                      "Please see below details. <br/> <br/> " \
                                      "<b>Backup File: %s" % (str(bkp_file)) + \
                                      " <a href='https://drive.google.com/drive/u/0/folders/%s'>Open</a></b>" % (
                                          str(rec.drive_folder_id))

                send_mail = self.env['mail.mail'].create(values)
                send_mail.send(True)
            else:
                response = r.json()
                code = response['error']['code']
                message = response['error']['errors'][0]['message']
                reason = response['error']['errors'][0]['reason']

                email_to = ""
                for rec in rec.gdrive_email_notif_ids.mapped('login'):
                    email_to += rec + ','

                notification_template = self.env['ir.model.data'].sudo().get_object('auto_backup_upload',
                                                                                    'email_google_drive_upload')
                values = notification_template.generate_email(self.id)
                values['email_from'] = self.env['res.users'].browse(self.env.uid).company_id.email
                values['email_to'] = email_to
                values['subject'] = "Google Drive Upload Failed"
                values['body_html'] = "<h3>Backup Upload Failed!</h3>" \
                                      "Please see below details. <br/> <br/> " \
                                      "<table style='width:100%'>" \
                                      "<tr> " \
                                      "<th align='left'>Backup</th>" \
                                      "<td>" + (str(bkp_file)) + "</td></tr>" \
                                                                 "<tr> " \
                                                                 "<th align='left'>Code</th>" \
                                                                 "<td>" + str(code) + "</td>" \
                                                                                      "</tr>" \
                                                                                      "<tr>" \
                                                                                      "<th align='left'>Message</th>" \
                                                                                      "<td>" + str(
                    message) + "</td>" \
                               "</tr>" \
                               "<tr>" \
                               "<th align='left'>Reason</th>" \
                               "<td>" + str(reason) + "</td>" \
                                                      "</tr> " \
                                                      "</table>"

                send_mail = self.env['mail.mail'].create(values)
                send_mail.send(True)

        # AUTO REMOVE UPLOADED FILE
        if rec.drive_autoremove:
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            params = {
                'access_token': access_token,
                'q': "mimeType='application/%s'" % (rec.backup_type),
                # 'q': "mimeType='application/zip'",
                'fields': "nextPageToken,files(id,name, createdTime, modifiedTime, mimeType)"
            }
            url = "/drive/v3/files"
            status, content, ask_time = self.env['google.service']._do_request(url, params, headers, type='GET')

            for item in content['files']:
                date_today = datetime.datetime.today().date()
                create_date = datetime.datetime.strptime(str(item['createdTime'])[0:10], '%Y-%m-%d').date()

                delta = date_today - create_date
                if delta.days >= rec.drive_to_remove:
                    params = {
                        'access_token': access_token
                    }
                    url = "/drive/v3/files/%s" % (item['id'])
                    response = self.env['google.service']._do_request(url, params, headers, type='DELETE')
