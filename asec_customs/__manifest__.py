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
        'data/training_program_document_type_data.xml',
        'data/ir_sequence.xml',
        'reports/report_training_participant_draft.xml',
        'reports/report_training_participant_final.xml',
        'reports/report.xml',
        'views/training_program_stage_views.xml',
        'views/training_program_courses_views.xml',
        'views/training_program_venue_views.xml',
        'views/training_program_document_type_views.xml',
        'views/training_program_document_views.xml',
        'views/training_program_views.xml',
        'views/menuitems.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
