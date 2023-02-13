# -*- coding: utf-8 -*-
{
    'name': "Car Expensive",
    'summary':
        """
        Registration of expenses associated with a vehicle
        """,
    'description': """
        Registration of expenses associated with a vehicle
    """,
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hr_expense', 'fleet'],
    'data': [
        'views/inherit_hr_expense_view.xml',
    ],
    'installable': True,
    'auto_install': False
}
