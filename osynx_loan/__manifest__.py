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
        'security/ir.model.access.csv',
        'data/config_data.xml',
        'data/website_page.xml',
        'views/member_contribution_views.xml',
        'views/menuitem.xml',
        'views/website_contributions.xml',
        'views/website_submit_contribution_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
