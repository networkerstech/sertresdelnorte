# -*- coding: utf-8 -*-
from odoo import fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    partner_use_addenda_levis = fields.Boolean(
        string="Use Addenda Levi's",
        related='partner_id.partner_use_addenda_levis',
    )

    def _get_sale_order_levi(self):
        sale_order = self.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
        if sale_order:
            return sale_order[0].name
        return ''
    
    def _get_efective_date_levi(self):
        sale_order = self.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
        if sale_order:
            return sale_order[0].effective_date.strftime('%Y-%m-%d')+'T'+sale_order[0].effective_date.strftime("%H:%M:%S")
        return ''
    
    def _get_sale_order_line_levi(self):
        sale_order = self.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
        if sale_order:
            return sale_order[0].order_line
        return []