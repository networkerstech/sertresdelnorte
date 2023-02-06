# -*- coding: utf-8 -*-

{
    'name': "Vehicle insurance policy",
    'summary': """
    Vehicle insurance policy
    """,
    'description': """
     This criterion will have a start date and an end date and the system must automatically 
     create a scheduled activity for a certain person in charge and based on a predefined criterion.
    """,
    'author': "SUITEDOO",
    'website': "https://suitedoo.com",
    'category': 'Fleet',
    'version': '0.1',
    'depends': ['base', 'fleet', ],
    'data': [
        'data/s_insure_fleet_data.xml',
        'security/ir.model.access.csv',
        'views/inherit_fleet_vehicle_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
