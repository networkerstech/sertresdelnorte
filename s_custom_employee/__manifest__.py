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
        # 'data/ir_cron_data.xml',
        # 'data/s_custom_employee_data.xml',
        'security/ir.model.access.csv',
        'views/inherit_hr_employee_views.xml',
        'views/inherit_res_config_settings_views.xml',
        # 'wizard/employee_resequence.xml',
    ],
    'installable': True,
    'auto_install': False
}
