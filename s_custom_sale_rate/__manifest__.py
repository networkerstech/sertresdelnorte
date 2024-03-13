# -*- coding: utf-8 -*-
{
    'name': "Custom Sale Exchange Rate",
    'summary': """Custom Sale Exchange Rate for Orders and its Invoices and Payments""",
    'description': """Custom Sale Exchange Rate for Orders and its Invoices and Payments""",
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': "Sales/Sales",
    'version': '0.1',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/decimal_precision.xml',
        'views/inherit_sale_order.xml',
        'views/inherit_account_move.xml',
    ],
    'installable': True,
    'auto_install': False
}
