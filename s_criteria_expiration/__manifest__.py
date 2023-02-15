# -*- coding: utf-8 -*-

{
    'name': "Criteria Expiration",
    'summary': """
      Criteria Expiration
    """,
    'description': """
      Record the expiration criteria in the vehicle register including the expiration date
    """,
    'author': "SUITEDOO",
    'website': "https://suitedoo.com",
    'category': 'Fleet',
    'version': '0.1',
    'depends': ['base', 'fleet', ],
    'data': [
        'data/criteria_expiration_menu.xml',
        'security/ir.model.access.csv',
        'views/vehicle_service_views.xml',
        'views/activity_parameters_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
