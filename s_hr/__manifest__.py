# -*- coding: utf-8 -*-
{
    'name': "Employee Custom Features",
    'summary': """Employee Custom Features""",
    'description': """Employee Custom Features""",
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': 'Human Resources/Employees',
    'version': '0.1',
    'depends': ['stock_account', 'purchase', 'sale', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'views/inherit_hr_employee.xml',
        'views/inherit_res_partner.xml',
        'views/inherit_res_country.xml',
        'views/hr_area.xml',
        'views/hr_speciality.xml',
        'views/hr_management_area.xml',
        'views/hr_activity_type.xml',
    ],
    'installable': True,
    'auto_install': False
}
