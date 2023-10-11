# -*- coding: utf-8 -*-
{
    'name': "EDI for Mexico suppliers features",
    'summary': """Electronic invoice suppliers features""",
    'description': """
       Electronic invoice suppliers features.
    """,
    'author': "SUITEDOO",
    'website': "https://www.suitedoo.com",
    'category': 'Accounting/Localizations/EDI',
    'version': '0.1',
    'depends': ['l10n_mx_edi'],
    'data': [
        'data/ir_cron.xml',
        'views/inherit_account_move.xml',
        'views/inherit_res_config_settings.xml',
        'views/inherit_hr_expense.xml',
    ],
    'installable': True,
    'auto_install': False
}
