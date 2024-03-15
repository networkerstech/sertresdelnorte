# -*- coding: utf-8 -*-

{
    'name': 'Addenda Pepsico',
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': 'sale',
    'sequence': 50,
    'summary': "Addenda Pepsico",
    'version': '16.1.0.1',
    'description': """Addenda Pepsico""",
    'depends': [
        'base',
        'account',
        'account_accountant',
        'sale_management',
        'l10n_mx_edi'
    ],
    'data': [
        'data/pepsico.xml',
        'views/inherit_res_company_views.xml',
        'views/inherit_account_move_views.xml'
    ],
    'demo': [],
    'qweb': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False
}