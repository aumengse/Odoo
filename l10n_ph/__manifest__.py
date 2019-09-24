# -*- coding: utf-8 -*-
{
    'name': "Philippine - Localization",

    'summary': """
        Philippine base location (source: http://www.philgis.org/):
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Aurel Balanay - Evanscor Technology Solutions Inc.",
    'website': "http://www.evanscor.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '0',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/ph_localization_views.xml',
        'views/menuitem_views.xml',
        'views/res_partner_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'post_init_hook': 'add_philippines_location',
}