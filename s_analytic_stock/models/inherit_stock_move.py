# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
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
                    'amount':  amount if self.picking_id.picking_type_id.code == 'incoming' else -amount,
                    'partner_id':  self.picking_id.partner_id.id,
                }
                if res:
                    # Si no existe se actualizan los valores para que se cree
                    res.update(vals)
                else:
                    if self.analytic_account_line_id:
                        # Si ya existe la línea analítica se actualiza
                        self.analytic_account_line_id.write(vals)
                    else:
                        res = self._generate_analytic_lines_data(
                            unit_amount, amount)
                        res.update(vals)
        return res

    def _prepare_move_split_vals(self, qty):
        """
        Adicionar la cuenta analítica a las entregas parciales si la entrega origen la tiene establecida
        """
        vals = super()._prepare_move_split_vals(qty)
        if self.analytic_account_id:
            vals.update({
                'analytic_account_id': self.analytic_account_id.id
            })
        return vals

    def _action_done(self, cancel_backorder=False):
        """Si tiene asociada una línde de cuenta analítica de envío o
        devolución de materiales marcarlos como hecho.

        Si el movimiento es una devolución y tiene cuenta analítica,
        verificar que la cantidad devuelta no sea mayor que las cantidades
        enviadas para ese cliente menos las cantidades que ya han sido
        devueltas
            cant_a_devolver <= (cant_enviada - cant_ya_devuelta)

        Tanto en las compras como en las devoluciones el picking_type_id.code
        es 'incoming' por que se usa el tipo de movimiento de devolución asociado
        a las compras (return_picking_type_id) puesto que las devoluciones no lo
        poseen porque no es necesario para estas.
        """
        for move in self:
            if move.picking_type_id.code == 'incoming' and not move.picking_type_id.return_picking_type_id and move.analytic_account_id and move.partner_id:
                sent_qty = sum([out_line.unit_amount for out_line in self.env['account.analytic.line'].search([
                    ('picking_type', '=', 'outgoing'),
                    ('picking_done', '=', True),
                    ('account_id', '=', move.analytic_account_id.id),
                    ('product_id', '=', move.product_id.id),
                    ('partner_id', '=', move.partner_id.id)
                ])])
                already_returned_qty = sum([abs(in_line.unit_amount) for in_line in self.env['account.analytic.line'].search([
                    ('id', '!=', move.id),
                    ('picking_type', '=', 'incoming'),
                    ('picking_done', '=', True),
                    ('account_id', '=', move.analytic_account_id.id),
                    ('product_id', '=', move.product_id.id),
                    ('partner_id', '=', move.partner_id.id)
                ])])
                if move.quantity_done > (sent_qty - already_returned_qty):
                    raise ValidationError(
                        _("You are trying to return a quantity of product greater than that sent:\n - Customer: %(customer)s\n - Analityc account: %(aaccount)s\n - Product: %(product)s\n - Returned quantity: %(returned_qty)s") % {
                            'customer': move.partner_id.name,
                            'aaccount': move.analytic_account_id.name,
                            'product': move.product_id.name,
                            'returned_qty': move.quantity_done,
                        })

        res = super()._action_done(cancel_backorder)

        for move in self:
            if move.analytic_account_line_id and move.analytic_account_line_id.picking_type:
                if not move.analytic_account_line_id.partner_id:
                    move.analytic_account_line_id.partner_id = move.partner_id
                if not move.analytic_account_line_id.picking_done:
                    move.analytic_account_line_id.picking_done = True
        return res
