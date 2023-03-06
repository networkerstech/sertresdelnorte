# -*- coding: utf-8 -*-
{
    'name': " s_custom_sale",

    'summary': """s_custom_sale""",
    'description': """ s_custom_sale""",
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': 'sale',
    'version': '0.1',
    'depends': ['base', 'sale_management'],
    'data': [
        'views/inherit_sale_order_views.xml',
        'views/inherit_analytic_account_views.xml'
    ],
    'installable': True,
    'auto_install': False
}
