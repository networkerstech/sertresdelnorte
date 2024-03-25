# -*- coding: utf-8 -*-

from odoo import fields, models, api, Command, _
from odoo.exceptions import UserError

READONLY_FIELD_STATES = {state: [("readonly", True)] for state in {"posted", "cancel"}}


class AccountMove(models.Model):
    _inherit = "account.move"

    foreign_currency = fields.Boolean(
        compute="_compute_foreign_currency",
        string="Foreign Currency",
        help="Auxiliary field to handle the visualization of the elements of the view",
    )
    use_manual_rate = fields.Boolean(
        "Set Exchange Rate", default=False, states=READONLY_FIELD_STATES
    )
    manual_rate = fields.Float(
        "Exchange Rate",
        default=0,
        states=READONLY_FIELD_STATES,
        digits="Manual exchange rate for sales",
    )

    @api.depends("company_id", "currency_id")
    def _compute_foreign_currency(self):
        """
        Campo auxiliar para usar en los dominios en la vista si la divisa no es la de la compañía
        """
        for rec in self:
            rec.foreign_currency = rec.company_id.currency_id.id != rec.currency_id.id

    @api.constrains("currency_id", "invoice_line_ids")
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
                lambda so: so.foreign_currency and so.foreign_currency and so.use_manual_rate
            )

            if len(mr_orders):
                # Se valida que no se puedan crear facturas que incluyan al mismo tiempo
                # - órdenes de venta CON tipo de cambio manual y
                # - órdenes de venta SIN tipo de cambio manual
                if len(orders) != len(mr_orders):
                    raise UserError(
                        _(
                            "Can not invoice multiple sales orders with manual exchange rate and automatic exchange rate together."
                        )
                    )

                # Se valida que no se pueda cambiar la moneda de la facturas asociadas a órdenes de venta con tipo de cambio manual
                for so in mr_orders:
                    if so.manual_currency_id.id != rec.currency_id.id:
                        raise UserError(
                            _(
                                "Can not invoice orders with manual exchange rate in a different currency."
                            )
                        )

                # Se valida que no se puedan asociar facturas a múltiples órdenes de venta con tasa de cambio manual con:
                # - diferente divisa manual o
                # - de la misma divisa manual con distintas tasas de cambio
                if len(mr_orders) > 1:
                    if len(mr_orders.manual_currency_id) > 1:
                        raise UserError(
                            _("Can not invoice orders with different manual currency.")
                        )
                    if len(set(mr_orders.mapped("manual_rate"))) > 1:
                        raise UserError(
                            _(
                                "Can not invoice orders with different manual exchange rate."
                            )
                        )

    @api.constrains(
        "foreign_currency", "currency_id", "use_manual_rate", "manual_rate"
    )
    def _constrains_manual_currency_rate(self):
        """
        Garantizar la consistencia de los datos
        """
        for rec in self:
            if rec.foreign_currency and rec.use_manual_rate and rec.manual_rate <= 0:
                # Si la moneda es diferente a la moneda de la compañía y está indicado que
                # se va a utilizar tipo de cambio manual, validar que este se mayor que cero
                raise UserError(_("You must specify exchange rate."))



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_currency_rate(self):
        """
        Si la(s) factura(s) usa tipo de cambio manual, usarlo para las líneas
        """
        res = super()._compute_currency_rate()

        rates = {}
        for line in self:
            manual_rate_inv = False
            # En el caso de las facturas
            if line.move_id.foreign_currency and line.move_id.use_manual_rate and line.move_id.manual_rate:
                manual_rate_inv = line.move_id

            # En el caso de asientos de base de efectivo
            if (
                line.move_id.tax_cash_basis_origin_move_id
                and line.move_id.tax_cash_basis_origin_move_id.foreign_currency
                and line.move_id.tax_cash_basis_origin_move_id.use_manual_rate
                and line.move_id.tax_cash_basis_origin_move_id.manual_rate
            ):
                manual_rate_inv = line.move_id.tax_cash_basis_origin_move_id

            if manual_rate_inv:
                if line.move_id.id not in rates:
                    # Por si existen líneas de facturas distintas
                    rates[manual_rate_inv.id] = 1.0 / manual_rate_inv.manual_rate
                line.currency_rate = rates[manual_rate_inv.id]
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
