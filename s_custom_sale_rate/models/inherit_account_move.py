# -*- coding: utf-8 -*-

from odoo import fields, models, api, Command, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.constrains('currency_id', 'invoice_line_ids')
    def _constrains_currency(self):
        """
        Realizar validaciones asociadas al tipo de cambio manual
        """
        self._check_manual_currency_rate()

    def action_post(self):
        """
        Realizar validaciones asociadas al tipo de cambio manual
        """
        self._check_manual_currency_rate()
        res = super().action_post()
        return res

    def _check_manual_currency_rate(self):
        """
        Si la venta que generó la factura usa tipo de cambio manual restringir la divisa a la de esta
        """
        for rec in self:
            orders = rec.line_ids.sale_line_ids.order_id
            mr_orders = orders.filtered(
                lambda so: so.foreign_currency and so.use_manual_rate)

            if len(mr_orders):
                # Se valida que no se puedan asociar facturas a órdenes de venta con y sin tipo de cambio manual
                if len(orders) != len(mr_orders):
                    raise UserError(
                        _('Can not invoice multiple sales orders with manual exchange rate and automatic exchange rate together.'))

                # Se valida que no se pueda cambiar la moneda de la facturas asociadas a órdenes de venta con tipo de cambio manual
                for so in mr_orders:
                    if so.manual_currency_id.id != rec.currency_id.id:
                        raise UserError(
                            _('Can not invoice orders with manual exchange rate in a different currency.'))

                # Se valida que no se puedan asociar facturas a múltiples órdenes de venta
                # con diferente divisa manual o de la misma divisa manual con distintas tasas de cambio
                if len(mr_orders) > 1:
                    if len(mr_orders.manual_currency_id) == 1:
                        if len(set(mr_orders.mapped('manual_rate'))) > 1:
                            raise UserError(
                                _('Can not invoice orders with different manual exchange rate.'))
                    else:
                        raise UserError(
                            _('Can not invoice orders with different manual currency.'))


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    inverse_currency_rate = fields.Float(
        compute='_compute_inverse_currency_rate', string='Exchange Rate')

    @api.depends('currency_rate')
    def _compute_inverse_currency_rate(self):
        for line in self:
            if not line.currency_rate:
                line.inverse_currency_rate = 1.0
            else:
                line.inverse_currency_rate = 1.0 / line.currency_rate

    def _compute_currency_rate(self):
        """
        Si la(s) orden(es) de venta usa tipo de cambio manual, usarlo para las líneas de la factura
        """
        res = super()._compute_currency_rate()

        # En el caso de las facturas
        mr_orders = self.sale_line_ids.order_id.filtered(
            lambda so: so.foreign_currency and so.use_manual_rate)
        if mr_orders:
            currency_rate = 1.0/mr_orders[0].manual_rate
            for line in self:
                line.currency_rate = currency_rate
        else:
            for line in self:
                # En el caso de asientos de base de efectivo
                if line.move_id.tax_cash_basis_origin_move_id:
                    mr_orders = line.move_id.tax_cash_basis_origin_move_id.line_ids.sale_line_ids.order_id.filtered(
                        lambda so: so.foreign_currency and so.use_manual_rate)
                    if mr_orders:
                        currency_rate = 1.0/mr_orders[0].manual_rate
                        line.currency_rate = currency_rate
        return res

    # TODO:Mantener por si fuese necesario, actualmente no se usa las
    # facturas se agrupan por moneda y tasa de cambio manual
    # @api.model_create_multi
    # def create(self, vals_list):
    #     """
    #     Si existen órdenes con tipo de cambio manual y automático simultáneamente
    #     o existen órdenes en la misma moneda con diferente tipo de cambio manual
    #     se divide el impuesto por órdenes para evitar los descuadres introducidos
    #     por el tipo de cambio
    #     """
    #     new_vals_list = []
    #     for vals in vals_list:
    #         keep_val = True
    #         if vals.get('display_type', '') == 'tax' and vals.get('move_id', False):
    #             move = self.env['account.move'].browse([vals['move_id']])
    #             orders = move.invoice_line_ids.sale_line_ids.order_id
    #             mr_orders = orders.filtered(
    #                 lambda so: so.foreign_currency and so.use_manual_rate)
    #             if len(mr_orders):
    #                 rates_by_currency = {}
    #                 for mr_order in mr_orders:
    #                     rates_by_currency.setdefault(
    #                         mr_order.manual_currency_id.id, [])
    #                     if mr_order.manual_rate not in rates_by_currency[mr_order.manual_currency_id.id]:
    #                         rates_by_currency[mr_order.manual_currency_id.id].append(
    #                             mr_order.manual_rate)
    #                 if len(orders) != len(mr_orders) or len(mr_orders) > 1 and any([len(rates) > 1 for rates in rates_by_currency.values()]):
    #                     # Si existen órdenes con tipo de cambio manual y automático simultáneamente
    #                     # o existen órdenes en la misma moneda con diferente tipo de cambio manual
    #                     # dividir el impuesto por órdenes
    #                     keep_val = False
    #                     for order in orders:
    #                         new_val = vals.copy()
    #                         tax_base_amount = order.amount_untaxed
    #                         amount_currency = order.amount_tax
    #                         balance = order.amount_tax
    #                         if order.foreign_currency and order.use_manual_rate:
    #                             tax_base_amount = order.company_id.currency_id.round(
    #                                 order.amount_untaxed * order.manual_rate)
    #                             balance = order.company_id.currency_id.round(
    #                                 order.amount_tax * order.manual_rate)
    #                         new_val.update({
    #                             'currency_id': move.currency_id.id,
    #                             'tax_base_amount': tax_base_amount if vals['amount_currency'] > 0 else -tax_base_amount,
    #                             'amount_currency': amount_currency if vals['balance'] > 0 else -amount_currency,
    #                             'balance': balance if vals['balance'] > 0 else -balance,
    #                             'name': ' '.join([vals['name'], '-', order.name]),
    #                             'sale_line_ids': [Command.set(order.order_line.ids)]
    #                         })
    #                         new_vals_list.append(new_val)
    #         if keep_val:
    #             new_vals_list.append(vals)
    #     return super().create(new_vals_list)
