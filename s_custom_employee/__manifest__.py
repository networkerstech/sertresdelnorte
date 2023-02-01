# -*- coding: utf-8 -*-
{
    'name': "Custom employee",
    'summary': """
    Custom employee
    """,
    'description': """
      Custom employee
    """,
    'author': "SUITEDOO",
    'website': "https://suitedoo.com",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['base', 'hr', ],
    'data': [
        'data/s_custom_employee_data.xml',
        'views/inherit_hr_employee_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
