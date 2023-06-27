# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.osv import expression


class StockMove(models.Model):
    _inherit = 'stock.move'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic Account',
        company_dependent=True
    )

    def _get_analytic_account(self):
        """
        Si el moviemiento es una entrega o devolución y la cuenta analítica está 
        establecida mediante el atributo self.analytic_account_id retornarla
        """
        if self.analytic_account_id and self.picking_id and self.picking_id.picking_type_id and self.picking_id.picking_type_id.code in ['incoming', 'outgoing']:
            return self.analytic_account_id
        return super()._get_analytic_account()

    def _prepare_analytic_lines(self):
        """
        Si la cuenta analítica está establecida mediante el atributo self.analytic_account_id
        y el moviemiento es una entrega o devolución actualizar los valores de la línea analítica
        que se crea o forzar la creación en caso de que no se haga
        """
        res = super()._prepare_analytic_lines()

        if self.analytic_account_id and self.state not in ['cancel', 'draft']:
            if self.picking_id and self.picking_id.picking_type_id and self.picking_id.picking_type_id.code in ['incoming', 'outgoing']:
                product_uom_qty = self.product_uom._compute_quantity(
                    self.quantity_done, self.product_id.uom_id)

                cost = self.product_id.standard_price

                vals = {
                    'picking_type': self.picking_id.picking_type_id.code,
                    'unit_amount': self.product_uom_qty,
                    'partner_id': self.partner_id.id if self.partner_id.id else False,
                    'so_line': self.sale_line_id.id if self.sale_line_id else False,
                    'cost': cost
                }

                if res:
                    res.update(vals)
                elif self.analytic_account_line_id:
                    self.analytic_account_line_id.write(vals)

        return res


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
        new_picking_id, pick_type_id = super()._create_returns()
        for move in self.env['stock.picking'].browse([new_picking_id]).move_ids_without_package:
            move._account_analytic_entry_move()
        return new_picking_id, pick_type_id
