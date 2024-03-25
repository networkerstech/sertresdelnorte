# -*- coding: utf-8 -*-

from odoo import Command, _, api, fields, models
from odoo.addons.sale.models.sale_order import READONLY_FIELD_STATES
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.move"

    sale_order_ids = fields.Many2many(
        "sale.order",
        string="Sale Order",
        help="Auxiliary field to link the sales orders with their payment",
    )

    manual_invoice_ids = fields.Many2many(
        "account.move",
        "account_move_pay_inv_rel",
        "payment_id",
        "invoice_id",
        string="Invoices",
        help="Auxiliary field to link the invoices with their payment",
    )


class AccountPayment(models.Model):
    _inherit = "account.payment"

    # foreign_currency = fields.Boolean(
    #     compute="_compute_foreign_currency",
    #     string="Foreign Currency",
    #     help="Auxiliary field to handle the visualization of the elements of the view",
    # )
    # use_manual_rate = fields.Boolean(
    #     "Set Exchange Rate", default=False, states=READONLY_FIELD_STATES
    # )
    # manual_rate = fields.Float(
    #     "Exchange Rate",
    #     default=0,
    #     states=READONLY_FIELD_STATES,
    #     digits="Manual exchange rate for sales",
    # )

    # @api.depends("company_id", "currency_id")
    # def _compute_foreign_currency(self):
    #     """
    #     Campo auxiliar para usar en los dominios en la vista si la divisa no es la de la compañía
    #     """
    #     for rec in self:
    #         rec.foreign_currency = rec.company_id.currency_id.id != rec.currency_id.id

    # @api.constrains(
    #     "foreign_currency", "manual_currency_id", "use_manual_rate", "manual_rate"
    # )
    # def _constrains_manual_currency_rate(self):
    #     """
    #     Garantizar la consistencia de los datos
    #     """
    #     for rec in self:
    #         if rec.foreign_currency and rec.use_manual_rate and rec.manual_rate <= 0:
    #             # Si la moneda es diferente a la moneda de la compañía y está indicado que
    #             # se va a utilizar tipo de cambio manual, validar que este se mayor que cero
    #             raise UserError(_("You must specify exchange rate."))

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        """
        Si el pago es para facturas con tipo de cambio manual usarlo para los apuntes contables
        """
        res = super()._prepare_move_line_default_vals(write_off_line_vals)

        mr_invs = self.manual_invoice_ids.filtered(
            lambda inv: inv.foreign_currency and inv.use_manual_rate
        )

        if len(mr_invs) > 0:
            manual_rate = mr_invs[0].manual_rate
            for line_vals in res:
                custom_amount = self.currency_id.round(self.amount * manual_rate)
                if line_vals["debit"] != 0:
                    if line_vals["debit"] < 0:
                        custom_amount = -custom_amount
                    line_vals["debit"] = custom_amount
                else:
                    if line_vals["credit"] < 0:
                        custom_amount = -custom_amount
                    line_vals["credit"] = custom_amount

        return res

    @api.constrains("currency_id")
    def _constrains_payment_currency(self):
        """
        Si el pago es de órdenes con tasa de cambio manual
        no se puede usar una moneda distinta a la de la orden

        Evitar que se paguen facturas con tipo de cambio manual con diferente tasa de cambio
        o facturas con tasa de cambio manual y automática simultáneamente
        """
        for payment in self.filtered(lambda x: x.payment_type == "inbound"):
            invoices = payment.manual_invoice_ids
            mr_invoices = invoices.filtered(
                lambda inv: inv.foreign_currency and inv.use_manual_rate
            )
            if len(mr_invoices) > 0:
                if len(mr_invoices) != len(invoices):
                    raise UserError(
                        _(
                            "Can not pay invoices with manual exchange rate and automatic exchange rate together."
                        )
                    )
                if payment.currency_id.id != mr_invoices[0].currency_id.id:
                    raise UserError(
                        _(
                            "Payments for invoices with a manual exchange rate cannot be made in a different currency."
                        )
                    )
                mr_set = set(
                    [(inv.currency_id.id, inv.manual_rate) for inv in mr_invoices]
                )
                if len(mr_set) > 1:
                    raise UserError(
                        _(
                            "Can not pay manual rate invoices with different exchange rate."
                        )
                    )


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _create_payments(self):
        """
        Validar que se puedan crear los pagos para las facturas selecionadas
        """
        return super()._create_payments()

    def _generate_manual_rate_payment_vals(self, batch_result):
        invoices = batch_result["lines"].move_id
        mr_invoices = invoices.filtered(
            lambda inv: inv.foreign_currency and inv.use_manual_rate
        )
        if mr_invoices:
            if len(mr_invoices) != len(invoices):
                raise UserError(
                    _(
                        "Can not pay invoices with manual exchange rate and automatic exchange rate together."
                    )
                )
            if len(mr_invoices.currency_id) > 1:
                raise UserError(
                    _(
                        "Payments for invoices with a manual exchange rate cannot be made in a different currency."
                    )
                )
            # Si llega hasta aquí todos tienen la misma moneda,
            # por tanto se verifica que la tasa de cambio sea distinta
            if len(set(mr_invoices.mapped("manual_rate"))) > 1:
                raise UserError(
                    _("Can not pay manual rate invoices with different exchange rate.")
                )

        return {
            "manual_invoice_ids": [Command.set(invoices.ids)],
            "use_manual_rate": True,
            "currency_id": invoices[0].currency_id.id,
            "manual_rate": invoices[0].manual_rate,
        }

    def _create_payment_vals_from_wizard(self, batch_result):
        """
        Si el pago se realiza para facturas generadas a partir de órdenes con tipo de cambio manual
        se establecen en el pago para tener forma de determinar luego que el es para esas órdenes
        """
        res = super()._create_payment_vals_from_wizard(batch_result)

        manual_currency_vals = self._generate_manual_rate_payment_vals(batch_result)
        if manual_currency_vals:
            res.update(manual_currency_vals)

        return res

    def _create_payment_vals_from_batch(self, batch_result):
        """
        Si el pago se realiza para facturas generadas a partir de órdenes con tipo de cambio manual
        se establecen en el pago para tener forma de determinar luego que el pago es para esas órdenes
        """
        res = super()._create_payment_vals_from_batch(batch_result)
        manual_currency_vals = self._generate_manual_rate_payment_vals(batch_result)
        if manual_currency_vals:
            res.update(manual_currency_vals)
        return res

    def _get_line_batch_key(self, line):
        """
        Si la línea pertenece a una factura con tasa de cambio manual
        Usar la modeda de la factura (la misma de la orden)
        """
        res = super()._get_line_batch_key(line)
        if line.move_id.foreign_currency and line.move_id.use_manual_rate:
            res["currency_id"] = line.move_id.currency_id.id
        return res

    def _compute_from_lines(self):
        """
        Si el pago es para facturas con tasa de cambio manual
        deshabilitar la edición para que no se cambie la moneda
        """
        res = super()._compute_from_lines()
        for wizard in self:
            if wizard.line_ids._origin.move_id.filtered(
                lambda inv: inv.foreign_currency and inv.use_manual_rate
            ):
                wizard.can_edit_wizard = False
        return res


class ResCurrency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        """
        Si la tasa de cambio fue establecida desde el asistente para registrar el pago, usar esta
        """
        if (
            "manual_payment_rate" in self.env.context
            and self.env.context["manual_payment_rate"]
        ):
            return self.env.context["manual_payment_rate"]
        return super()._get_conversion_rate(from_currency, to_currency, company, date)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_currency_rate(self):
        """
        Si la factura usa tipo de cambio manual, usarlo para las líneas del pago
        """
        res = super()._compute_currency_rate()
        for line in self:
            if line.move_id.foreign_currency and line.move_id.use_manual_rate:
                currency_rate = 1.0 / line.move_id.manual_rate
                line.currency_rate = currency_rate
        return res
