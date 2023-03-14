# -*- coding: utf-8 -*-
{
    'name': " s_workshop_service",
    'summary': """s_workshop_service""",
    'description': """ s_workshop_service""",
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'license': 'LGPL-3',
    'category': 'sale',
    'version': '0.1',
    'depends': ['base', 'fleet'],
    'data': [
        'views/inherit_fleet_vehicle_model_views.xml',
        'views/inherit_fleet_vehicle_views.xml'
    ],
    'installable': True,
    'auto_install': False
}
