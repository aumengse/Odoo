# -*- coding: utf-8 -*-
{
    'name': "Database Auto-Backup Upload",

    'summary': """
        Automatically Upload backup to Google Drive.
        """,

    'description': """
        Requirement:
        auto_backup module of yenthe
    """,

    'author': "Aurel Balanay - Evanscor Technology Solutions Incc",
    'website': "http://www.evanscor.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Generic Modules',
    'version': '10.1',

    # any module necessary for this one to work correctly
    'depends': ['base','google_drive','auto_backup'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/db_backup_views.xml',
        'views/templates/auto_backup_mail_templates.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}