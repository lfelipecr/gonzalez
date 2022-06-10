# -*- coding: utf-8 -*-
{
    'name': "l10n_cr_gonzales",

    'summary': """
        Módulo personalizado para PRODUCTOS GONZALES""",

    'description': """
        Personalizaciones para PRODUCTOS GONZALES
    """,

    'author': "BPC Latam",
    'website': "https://bpclatam.odoo.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '14.0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'data/ir_sequence.xml',
        'views/account_move_views.xml',
        'views/sale_views.xml',
        'views/res_partner_views.xml',
        'views/product_views.xml',
        'wizard/sale_order_import_wizard.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
