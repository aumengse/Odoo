# -*- coding: utf-8 -*-
{
    'name': "ASEC- Training Programs",

    'summary': """
       ASEC- custom modules
       """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Aurel",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/training_program_stage_data.xml',
        'views/training_program_stage_views.xml',
        'views/training_program_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
