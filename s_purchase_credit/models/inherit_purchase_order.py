# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    provider_credit_limit_exceeded = fields.Boolean(
        compute='_compute_provider_credit_limit_exceeded',
        string='Provider Credit Limit Exceeded'
    )

    provider_credit_limit_exceeded_msg = fields.Char(
        compute='_compute_provider_credit_limit_exceeded',
        string='Message for Provider Credit Limit Exceeded'
    )

    @api.depends('partner_id', 'order_line')
    def _compute_provider_credit_limit_exceeded(self):
        """
        Mensaje que se muestra cuando la orden excede el límite de crédito del proveedor
        """
        for order in self:
            if order.partner_id.provider_credit_control and order.state != 'done':
                partner_currency = order.partner_id.property_purchase_currency_id or self.env.company.currency_id
                order_amount = order.currency_id._convert(
                    from_amount=order.amount_total,
                    to_currency=partner_currency,
                    company=self.env.company,
                    date=fields.Date.today(),
                )
                if order.partner_id.provider_amount_to_pay + order_amount > order.partner_id.provider_credit_max_amount:
                    order.provider_credit_limit_exceeded = True
                    order.provider_credit_limit_exceeded_msg = _("%(provider)s reached its credit limit of %(credit_limit).2f. The available amount is %(available_amount).2f. If you wish to continue the order, it will be considered as a cash purchase.") % {
                        'provider': order.partner_id.name,
                        'credit_limit': order.partner_id.provider_credit_max_amount,
                        'available_amount': order.partner_id.provider_credit_max_amount - order.partner_id.provider_amount_to_pay
                    }
                    continue

            order.provider_credit_limit_exceeded = False
            order.provider_credit_limit_exceeded_msg = ""
