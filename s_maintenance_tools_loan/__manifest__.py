# -*- coding: utf-8 -*-
{
    'name': "Tools loan of maintenance",
    'summary': """Features for tools loan of maintenance""",
    'description': """Features for tools loan of maintenance""",
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': 'Manufacturing/Maintenance',
    'version': '0.1',
    'depends': ['base', 'fleet'],
    'data': [
        'data/ir_cron.xml',
        'data/mail_template.xml',
        'views/inherit_maintenance_equipment_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
