# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.osv import expression


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model_create_multi
    def create(self, vals):
        return super().create(vals)

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
                cost = self.product_id.standard_price * self.quantity_done
                # Cuando la entrega pertenece a una venta que generó una compra
                if self.picking_id.picking_type_id.code == 'outgoing' and self.move_orig_ids:
                    move_origin = self.move_orig_ids
                    if move_origin:
                        purchase_line = move_origin[0].purchase_line_id
                        if purchase_line:
                            invoice_lines = purchase_line[0].invoice_lines
                            if invoice_lines:
                                cost = invoice_lines[0].price_unit * \
                                    invoice_lines[0].quantity
                # Cuando la entrega pertenece a una devolución
                elif self.picking_id.picking_type_id.code == 'incoming' and self.origin_returned_move_id:
                    if self.origin_returned_move_id.analytic_account_line_id:
                        cost = self.origin_returned_move_id.analytic_account_line_id.cost
                unit_amount = self.product_uom._compute_quantity(
                    self.product_qty, self.product_id.uom_id)
                amount = unit_amount * self.product_id.standard_price

                vals = {
                    'picking_type': self.picking_id.picking_type_id.code,
                    'cost': cost,
                    'unit_amount': -unit_amount if self.picking_id.picking_type_id.code == 'incoming' else unit_amount,
                    'amount':  amount if self.picking_id.picking_type_id.code == 'incoming' else -amount
                }
                if res:
                    # Si no existe se actualizan los valores para que se cree
                    res.update(vals)
                else:
                    if self.analytic_account_line_id:
                        # Si ya existe la línea analítica se actualiza
                        self.analytic_account_line_id.write(vals)
                    elif self.picking_id.picking_type_id.code == 'incoming':
                        # En el caso de las revoluciones devuelve false y no existe la línea analítica
                        res = self._generate_analytic_lines_data(
                            unit_amount, amount)
                        res.update(vals)
        return res
