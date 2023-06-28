# -*- coding: utf-8 -*-
{
    'name': "Analytic Stock",
    'summary': """Analytic Stock""",
    'description': """Analytic Stock""",
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': 'Accounting/Accounting',
    'version': '0.1',
    'depends': ['stock_account', 'purchase', 'sale', 'analytic'],
    'data': [
        'views/inherit_stock_picking_views.xml',
        'views/inherit_analytic_account_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
