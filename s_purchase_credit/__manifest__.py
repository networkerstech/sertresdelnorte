# -*- coding: utf-8 -*-
{
    'name': "Credits limit for providers",
    'summary': """
        Manage credit limit for providers
    """,
    'description': """
        Manage credit limit for providers
    """,
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': 'Inventory/Purchase',
    'version': '0.1',
    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/inherit_res_partner.xml',
        'views/inherit_purchase_order.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False
}
