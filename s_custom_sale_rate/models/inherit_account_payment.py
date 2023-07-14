# -*- coding: utf-8 -*-

from odoo import Command, _, api, fields, models
from odoo.addons.sale.models.sale_order import READONLY_FIELD_STATES
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_ids = fields.Many2many(
        'sale.order',
        string='Sale Order',
        help="Auxiliary field to link the sales orders with their payment"
    )


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        """
        Si el pago es para órdenes con tipo de cambio manual usarlo para los pauntes contables
        """
        res = super()._prepare_move_line_default_vals(write_off_line_vals)

        mr_orders = self.sale_order_ids.filtered(
            lambda so: so.foreign_currency and so.use_manual_rate)
        if len(mr_orders) > 0:
            manual_rate = mr_orders[0].manual_rate
            for line_vals in res:
                custom_amount = self.currency_id.round(
                    self.amount*manual_rate)
                if line_vals['debit'] != 0:
                    if line_vals['debit'] < 0:
                        custom_amount = -custom_amount
                    line_vals['debit'] = custom_amount
                else:
                    if line_vals['credit'] < 0:
                        custom_amount = -custom_amount
                    line_vals['credit'] = custom_amount

        return res

    @api.constrains('currency_id')
    def _constrains_payment_currency(self):
        """
        Si el pago es de órdenes con tasa de cambio manual 
        no se puede usar una moneda distinta a la de la orden

        Evitar que se paguen facturas con tipo de cambio manual con diferente tasa de cambio 
        o facturas con tasa de cambio manual y automática simultáneamente
        """
        for payment in self.filtered(lambda x: x.payment_type == 'inbound'):
            orders = payment.sale_order_ids
            mr_orders = orders.filtered(
                lambda so: so.foreign_currency and so.use_manual_rate)
            if len(mr_orders) > 0:
                if len(mr_orders) != len(orders):
                    raise UserError(
                        _('Can not pay invoices with manual exchange rate and automatic exchange rate together.'))
                if payment.currency_id.id != mr_orders[0].manual_currency_id.id:
                    raise UserError(
                        _('Payments for orders with a manual exchange rate cannot be made in a different currency.'))
                if len(set([(so.manual_currency_id.id, so.manual_rate) for so in mr_orders])) > 1:
                    raise UserError(
                        _("Can not pay manual rate invoices with different exchange rate."))


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self):
        """
        Validar que se puedan crear los pagos para las facturas selecionadas
        """
        return super()._create_payments()

    def _create_payment_vals_from_wizard(self, batch_result):
        """
        Si el pago se realiza para facturas generadas a partir de órdenes con tipo de cambio manual
        se establecen en el pago para tener forma de determinar luego que el  es para esas órdenes 
        """
        res = super()._create_payment_vals_from_batch(batch_result)
        if batch_result['lines']:
            invoices = batch_result['lines'].move_id
            mr_orders = invoices.invoice_line_ids.sale_line_ids.order_id.filtered(
                lambda so: so.foreign_currency and so.use_manual_rate)
            if len(mr_orders) > 0:
                res.update({
                    'sale_order_ids': [Command.set(mr_orders.ids)]
                })
        return res

    def _create_payment_vals_from_batch(self, batch_result):
        """
        Si el pago se realiza para facturas generadas a partir de órdenes con tipo de cambio manual
        se establecen en el pago para tener forma de determinar luego que el pago es para esas órdenes 
        """
        res = super()._create_payment_vals_from_batch(batch_result)
        if batch_result['lines']:
            invoices = batch_result['lines'].move_id
            mr_orders = invoices.invoice_line_ids.sale_line_ids.order_id.filtered(
                lambda so: so.foreign_currency and so.use_manual_rate)
            if len(mr_orders) > 0:
                res.update({
                    'sale_order_ids': [Command.set(mr_orders.ids)]
                })
        return res

    def _get_line_batch_key(self, line):
        """
        Si la línea pertenece a una factura generada a partir de una ordern con tasa de cambio manual
        Usar la modeda de la factura (la misma de la orden)
        """
        res = super()._get_line_batch_key(line)
        mr_orders = line.move_id.invoice_line_ids.sale_line_ids.order_id.filtered(
            lambda so: so.foreign_currency and so.use_manual_rate)
        if len(mr_orders):
            res['currency_id'] = line.move_id.currency_id.id
        return res

    def _compute_from_lines(self):
        """
        Si el pago es para facturas que se generaron a partir de órdenes de venta con tasa 
        de cambio manual deshabilitar la edición para que no se cambie la moneda
        """
        res = super()._compute_from_lines()
        for wizard in self:
            if wizard.line_ids._origin.move_id.invoice_line_ids.sale_line_ids.order_id.filtered(
                    lambda so: so.foreign_currency and so.use_manual_rate):
                wizard.can_edit_wizard = False
        return res


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _get_convxersion_rate(self, from_currency, to_currency, company, date):
        """
        Si la tasa de cambio fue establecida desde el asistente para registrar el pago, usar esta
        """
        if 'manual_payment_rate' in self.env.context and self.env.context['manual_payment_rate']:
            return self.env.context['manual_payment_rate']
        return super()._get_conversion_rate(from_currency, to_currency, company, date)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _compute_currency_rate(self):
        """
        Si la orden de venta usa tipo de cambio manual, usarlo para las líneas del pago
        """
        res = super()._compute_currency_rate()
        for line in self:
            mr_orders = line.move_id.sale_order_ids.filtered(
                lambda so: so.foreign_currency and so.use_manual_rate)
            if mr_orders:
                currency_rate = 1.0/mr_orders[0].manual_rate
                line.currency_rate = currency_rate
        return res
