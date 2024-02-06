# -*- coding: utf-8 -*-
{
    'name': "Addenda Marelli",

    'summary': """Addenda Marelli""",

    'description': """Addenda Marelli""",

    'author': "Networkers",
    'website': "https://suitedoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '16.0.1',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': [
        'l10n_mx_edi'
    ],

    # always loaded
    'data': [
        'data/addenda_marelli.xml',
    ],
}
