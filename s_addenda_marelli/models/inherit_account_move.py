# -*- coding: utf-8 -*-
from odoo import fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_sale_order_mirelli(self):
        sale_order = self.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
        if sale_order:
            return sale_order[0].name
        return ''
    
    def _get_sale_order_line_mirelli(self):
        sale_order = self.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
        if sale_order:
            return sale_order[0].order_line
        return []