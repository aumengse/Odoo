# -*- coding: utf-8 -*-
{
    'name': "Loan Management (Cooperative)",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Osynx Solutions",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website_form'],

    # always loaded
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/config_data.xml',
        'data/website_page.xml',
        'data/ir_sequence.xml',
        'data/ir_actions_server.xml',
        'data/ir_cron.xml',
        'data/loan_interest_data.xml',
        'data/mail_template.xml',
        'wizard/loan_extend_wizard_views.xml',
        'wizard/loan_report_wizard_views.xml',
        'reports/report.xml',
        'reports/report_summary.xml',
        'reports/report_loan_payout_summary.xml',
        'reports/report_member_statement.xml',
        'reports/report_loan_account.xml',
        'views/assets.xml',
        'views/loan_interest_views.xml',
        'views/member_account_views.xml',
        'views/member_contribution_views.xml',
        'views/loan_account_views.xml',
        'views/loan_penalty_views.xml',
        'views/menuitem.xml',
        'views/res_config_settings_views.xml',
        # 'views/website_contributions.xml',
        'views/website_loan_payments.xml',
        'views/website_submit_payment.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
