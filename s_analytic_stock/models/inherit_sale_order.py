# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.osv import expression


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_procurement_values(self, group_id=False):
        """
        Establecer la cuenta analítica para poder recuperarla desde _get_stock_move_values
        """
        res = super()._prepare_procurement_values(group_id)
        if self.analytic_account_id:
            res['analytic_account_id'] = self.analytic_account_id.id
        return res

    def _purchase_service_prepare_line_values(self, purchase_order, quantity=False):
        """
        Establecer la cuenta analítica en la compra cuando es 
        generada desde una venta y esta posee cuenta analítica
        """
        res = super().method_name(purchase_order, quantity)
        if self.analytic_account_id:
            res.update({
                'analytic_distribution': {self.analytic_account_id: 100}
            })
        return res


class SaleOrder(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values):
        """
        Establecer la cuenta analítica que viene desde _prepare_procurement_values
        """
        res = super()._get_stock_move_values(product_id, product_qty, product_uom,
                                             location_dest_id, name, origin, company_id, values)
        if 'analytic_account_id' in values:
            res.update({'analytic_account_id': values['analytic_account_id']})
        return res
