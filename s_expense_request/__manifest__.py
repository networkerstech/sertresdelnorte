# -*- coding: utf-8 -*-
{
    'name': "Expense Request",
    'summary': """Create request for hr expenses""",
    'description': """Create request for hr expenses""",
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': 'Human Resources/Expenses',
    'version': '0.1',
    'depends': ['hr_expense'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_expense_request.xml',
        'views/inherit_hr_expense.xml',
    ],
    'installable': True,
    'auto_install': False
}
