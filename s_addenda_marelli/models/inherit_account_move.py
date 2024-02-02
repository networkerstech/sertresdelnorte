# -*- coding: utf-8 -*-
from odoo import fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    mirelli_po_number = fields.Char(
        string='Number of PO',
        copy=False,
    )

    mirelli_line_number = fields.Char(
        string='Number of line',
        copy=False,
    )
    mirelli_item_number = fields.Char(
        string='Number of Item',
        copy=False,
    )
    
    partner_use_addenda_marelli = fields.Boolean(
        string="Use Addenda Marelli",
        related='partner_id.partner_use_addenda_marelli',
    )