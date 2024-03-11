# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _prepare_move_default_values(self, return_line, new_picking):
        """
        Asociar la misma cuenta analíca de la entrega a las devoluviones para que se
        creen las líneas anlíticas para las devoluciones
        """
        res = super()._prepare_move_default_values(return_line, new_picking)
        if return_line.move_id.analytic_account_id:
            res.update(
                {'analytic_account_id': return_line.move_id.analytic_account_id.id})
        return res

    def _create_returns(self):
        """
        Crear líneas analíticas para las devoluciones
        """
        if any([line.analytic_account_id and line.quantity_shipped < line.quantity for line in self.product_return_moves]):
            raise UserError(
                _('Quantities of a product that have not been shipped cannot be returned'))
        new_picking_id, pick_type_id = super()._create_returns()
        for move in self.env['stock.picking'].browse([new_picking_id]).move_ids_without_package:
            move._account_analytic_entry_move()
        return new_picking_id, pick_type_id

    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        res = super()._prepare_stock_return_picking_line_vals_from_move(stock_move)

        if stock_move.analytic_account_id:
            out_qty = 0
            out_lines = self.env['account.analytic.line'].search([
                ('picking_type', '=', 'outgoing'),
                ('product_id', '=', stock_move.product_id.id)])
            if out_lines:
                out_qty = sum(out_lines.mapped('unit_amount'))
            ret_qty = 0
            ret_lines = self.env['account.analytic.line'].search([
                ('picking_type', '=', 'incoming'),
                ('product_id', '=', stock_move.product_id.id)])
            if ret_lines:
                ret_qty = sum([abs(val)
                              for val in ret_lines.mapped('unit_amount')])

            res.update({
                'analytic_account_id': stock_move.analytic_account_id.id,
                'quantity_shipped': out_qty - ret_qty
            })
        else:
            res.update({
                'analytic_account_id': False,
                'quantity_shipped': 0
            })
        return res


class ReturnPickingLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    quantity_shipped = fields.Float(
        string='Quantity Shipped'
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic Account',
        company_dependent=True,
        default=False
    )
