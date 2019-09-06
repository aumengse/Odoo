from odoo.addons.google_drive.models.google_drive import GoogleDrive
from odoo import models, fields, api, tools, _
from odoo.exceptions import Warning
import json,\
    os,\
    re,\
    pytz,\
    requests,\
    logging,\
    xmlrpclib,\
    datetime,\
    functools,\
    shutil,\
    pysftp
_logger = logging.getLogger(__name__)

class DbBackup(models.Model):
    _inherit = 'db.backup'

    # Columns fro Google Drive
    is_upload = fields.Boolean('Upload to Google Drive',
                               help="If you check this option you can specify the details needed to upload to google drive.")
    drive_folder_id = fields.Char(string='Folder ID',
                                  help="make a folder on drive in which you want to upload files; then open that folder; the last thing in present url will be folder id")
    gdrive_email_notif_ids = fields.Many2many('res.users', string="Email Notification")
    drive_autoremove = fields.Boolean('Auto. Remove Uploaded Backups',
                                      help='If you check this option you can choose to automaticly remove the backup after xx days')

    drive_to_remove = fields.Integer('Remove after x days',
                                     help="Choose after how many days the backup should be deleted. For example:\nIf you fill in 5 the backups will be removed after 5 days.",
                                     )

    @api.multi
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
                #Create name for dumpfile.
                user_tz = self.env.user.tz or str(pytz.utc)
                local = pytz.timezone(user_tz)
                today = datetime.datetime.strftime(pytz.utc.localize(datetime.datetime.today()).astimezone(local), '%d_%m_%Y_%H_%M_%S')
                bkp_file='%s_%s.%s' % (rec.name,today, rec.backup_type)
                file_path = os.path.join(rec.folder,bkp_file)
                uri = 'http://' + rec.host + ':' + rec.port
                conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
                bkp=''
                try:
                    bkp_resp = requests.post(
                        uri + '/web/database/backup', stream = True,
                        data = {
                            'master_pwd': tools.config['admin_passwd'],
                            'name': rec.name,
                            'backup_format': rec.backup_type
                        }
                    )
                    bkp_resp.raise_for_status()
                except:
                    _logger.debug("Couldn't backup database %s. Bad database administrator password for server running at http://%s:%s" %(rec.name, rec.host, rec.port))
                    continue
                with open(file_path,'wb') as fp:
                    # see https://github.com/kennethreitz/requests/issues/2155
                    bkp_resp.raw.read = functools.partial(
                        bkp_resp.raw.read, decode_content=True)
                    shutil.copyfileobj(bkp_resp.raw, fp)
            else:
                _logger.debug("database %s doesn't exist on http://%s:%s" %(rec.name, rec.host, rec.port))

            # Check if user wants to write to SFTP or not.
            if rec.sftp_write is True:
                try:
                    # Store all values in variables
                    dir = rec.folder
                    pathToWriteTo = rec.sftp_path
                    ipHost = rec.sftp_host
                    portHost = rec.sftp_port
                    usernameLogin = rec.sftp_user
                    passwordLogin = rec.sftp_password
                    # Connect with external server over SFTP
                    srv = pysftp.Connection(host=ipHost, username=usernameLogin, password=passwordLogin, port=portHost)
                    # set keepalive to prevent socket closed / connection dropped error
                    srv._transport.set_keepalive(30)
                    # Move to the correct directory on external server. If the user made a typo in his path with multiple slashes (/odoo//backups/) it will be fixed by this regex.
                    pathToWriteTo = re.sub('([/]{2,5})+','/',pathToWriteTo)
                    _logger.debug('sftp remote path: %s' % pathToWriteTo)
                    try:
                        srv.chdir(pathToWriteTo)
                    except IOError:
                        #Create directory and subdirs if they do not exist.
                        currentDir = ''
                        for dirElement in pathToWriteTo.split('/'):
                            currentDir += dirElement + '/'
                            try:
                                srv.chdir(currentDir)
                            except:
                                _logger.info('(Part of the) path didn\'t exist. Creating it now at ' + currentDir)
                                #Make directory and then navigate into it
                                srv.mkdir(currentDir, mode=777)
                                srv.chdir(currentDir)
                                pass
                    srv.chdir(pathToWriteTo)
                    # Loop over all files in the directory.
                    for f in os.listdir(dir):
                        if rec.name in f:
                            fullpath = os.path.join(dir, f)
                            if os.path.isfile(fullpath):
                                if not srv.exists(f):
                                    _logger.info('The file %s is not yet on the remote FTP Server ------ Copying file' % fullpath)
                                    srv.put(fullpath)
                                    _logger.info('Copying File % s------ success' % fullpath)
                                else:
                                    _logger.debug('File %s already exists on the remote FTP Server ------ skipped' % fullpath)

                    # Navigate in to the correct folder.
                    srv.chdir(pathToWriteTo)

                    # Loop over all files in the directory from the back-ups.
                    # We will check the creation date of every back-up.
                    for file in srv.listdir(pathToWriteTo):
                        if rec.name in file:
                            # Get the full path
                            fullpath = os.path.join(pathToWriteTo,file)
                            # Get the timestamp from the file on the external server
                            timestamp = srv.stat(fullpath).st_atime
                            createtime = datetime.datetime.fromtimestamp(timestamp)
                            now = datetime.datetime.now()
                            delta = now - createtime
                            # If the file is older than the days_to_keep_sftp (the days to keep that the user filled in on the Odoo form it will be removed.
                            if delta.days >= rec.days_to_keep_sftp:
                                # Only delete files, no directories!
                                if srv.isfile(fullpath) and (".dump" in file or '.zip' in file):
                                    _logger.info("Delete too old file from SFTP servers: " + file)
                                    srv.unlink(file)
                    # Close the SFTP session.
                    srv.close()
                except Exception, e:
                    _logger.debug('Exception! We couldn\'t back up to the FTP server..')
                    #At this point the SFTP backup failed. We will now check if the user wants
                    #an e-mail notification about this.
                    if rec.send_mail_sftp_fail:
                        try:
                            ir_mail_server = self.pool.get('ir.mail_server')
                            message = "Dear,\n\nThe backup for the server " + rec.host + " (IP: " + rec.sftp_host + ") failed.Please check the following details:\n\nIP address SFTP server: " + rec.sftp_host + "\nUsername: " + rec.sftp_user + "\nPassword: " + rec.sftp_password + "\n\nError details: " + tools.ustr(e) + "\n\nWith kind regards"
                            msg = ir_mail_server.build_email("auto_backup@" + rec.name + ".com", [rec.email_to_notify], "Backup from " + rec.host + "(" + rec.sftp_host + ") failed", message)
                            ir_mail_server.send_email(self._cr, self._uid, msg)
                        except Exception:
                            pass

            """
            Remove all old files (on local server) in case this is configured..
            """
            if rec.autoremove:
                dir = rec.folder
                # Loop over all files in the directory.
                for f in os.listdir(dir):
                    fullpath = os.path.join(dir, f)
                    # Only delete the ones wich are from the current database (Makes it possible to save different databases in the same folder)
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

            self.google_drive_upload(rec,file_path,bkp_file)

    @api.multi
    def google_drive_upload(self,rec,file_path,bkp_file):
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
                                      "<td>" + str(message) + "</td>" \
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
                'q': "mimeType='application/%s'" %(rec.backup_type),
                # 'q': "mimeType='application/zip'",
                'fields': "nextPageToken,files(id,name, createdTime, modifiedTime, mimeType)"
            }
            url = "/drive/v3/files"
            status, content, ask_time = self.env['google.service']._do_request(url, params, headers,type='GET')

            for item in content['files']:
                date_today = datetime.datetime.today().date()
                create_date = datetime.datetime.strptime(str(item['createdTime'])[0:10],'%Y-%m-%d').date()

                delta = date_today - create_date
                if delta.days >= rec.drive_to_remove:
                    params = {
                        'access_token': access_token
                    }
                    url = "/drive/v3/files/%s" % (item['id'])
                    response = self.env['google.service']._do_request(url, params, headers, type='DELETE')
