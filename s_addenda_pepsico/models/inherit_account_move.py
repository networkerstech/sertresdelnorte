# -*- coding: utf-8 -*-


from odoo import _, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    addenda_pepsico = fields.Boolean(
        string='Addenda Pepsico',
        related='partner_id.addenda_pepsico',
        help='Technical field that helps us to identify if the partner '
             'uses the Addenda Pepsico.'
    )
    order_pepsico_id = fields.Char(
        string='Pepsico purchase order',
        help='Pepsico purchase order id',
        copy=False)
    request_pay_id = fields.Char(
        string='Pepsico payment request',
        help='Pepsico payment request id',
        copy=False)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    reception_id = fields.Char(
        string='Reception id',
        help='Reception id',
        copy=False)
