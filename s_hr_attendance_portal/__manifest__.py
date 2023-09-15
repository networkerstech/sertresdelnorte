# -*- coding: utf-8 -*-
{
    'name': "Hr Attendance Portal",
    'summary': """
        Allow to portal users register attendances""",
    'description': """
        Allow to portal users register attendances
    """,
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': 'Human Resources/Attendances',
    'version': '0.1',
    'depends': ['portal', 'hr_attendance'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/attendance_portal_templates.xml',
        'views/inherit_hr_employee.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            's_hr_attendance_portal/static/src/js/home_counters.js',
            's_hr_attendance_portal/static/src/js/attendance_portal.js'
        ]
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False
}
