# -*- coding: utf-8 -*-
from odoo import fields, models, _, api


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    addenda_marelli = fields.Boolean(
        string='Addenda Marelli',
        related='partner_id.partner_use_addenda_marelli',
        help='Technical field that helps us to identify if the partner '
             'uses the Addenda Marelli.'
    )
    
    order_marelli = fields.Char(
        string='PO',
        help='Marelli purchase order id',
        copy=False)
    
    currency_marelli_aux = fields.Char(
        string='Currency Marelli',
        compute='_compute_currency_marelli_aux',
        copy=False)
    
    currency_marelli = fields.Char(
        string='Currency',
        copy=False)
    
    @api.depends('currency_id')
    def _compute_currency_marelli_aux(self):
        for record in self:
            record.currency_marelli_aux = record.currency_id.name
            record.currency_marelli = record.currency_id.name
      
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    linea_marelli = fields.Char(
        string='Linea Marelli',
        copy=False
        )

    part_marelli = fields.Char(
        string='Part Marelli',
        copy=False
        )