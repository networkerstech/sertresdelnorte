# -*- coding: utf-8 -*-
{
    'name': "Activity car",
    'summary': """The person responsible for the pending activities changes if the driver of the vehicle changes""",
    'description': """
       It is necessary that the system changes the scheduled activities 
       of that vehicle automatically and these are assigned to the new assigned manager.
    """,
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'fleet',
        's_criteria_expiration'
    ],
    'data': [],
    'installable': True,
    'auto_install': False
}
