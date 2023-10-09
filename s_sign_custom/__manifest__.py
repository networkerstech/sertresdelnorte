{
    'name': 'SUITEODOO | Document Sign',
    'author': 'SUITEDOO',
    'category': 'Extra Tools',
    'sequence': 50,
    'summary': "SUITEDOO Document Signature.",
    'website': "https://suitedoo.com",
    'version': '1.0',
    'description': """
SUITEODOO | Document Sign
=================================================

Allows you to configure signature requests for any model.
When the signature is requested, a document is sent via
email like the Odoo Sign Native app. When the signature
is made, the document is attached to the model.

Features:
    1. Customize any PDF document signature.
    2. Customize any PDF Odoo report document signature.
    3. Customize the signer template to the model "Print" menu.
    4. Add the document signer(s) for each template.
    5. Send customizable messages via email to notify the sign requests.
    6. Signed report is attach to signer model object.

License
=======

GNU General Public License as published by the Free Software Foundation, version 3
<https://www.gnu.org/licenses/gpl-3.0.en.html>

""",
    'depends': ['sign'],
    'data': [
        'security/ir.model.access.csv',
        'views/sign_template_views.xml',
        'views/menus.xml',
    ],
    'demo': [],
    'qweb': [],
    'application': False,
    'installable': True,
}
