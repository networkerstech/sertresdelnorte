# -*- coding: utf-8 -*-
{
    'name': "Sale Attachments",
    'summary': """Manage Attachments for Sale Orders""",
    'description': """
        Manage attachments for sales orders, document settings by type, optional and required documents
    """,
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': 'Sales/Sales',
    'version': '0.1',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_project_views.xml',
        'views/inherit_sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            's_sale_docs/static/src/js/relational_util.js',
        ]
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False
}
