# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    provider_credit_control = fields.Boolean('Credit Control')
    provider_currency_id = fields.Many2one(
        'res.currency',
        compute='_compute_provider_currency_id',
        string='Provider Currency'
    )
    provider_credit_max_amount = fields.Monetary(
        'Maximum Credit Amount Allowed',
        currency_field='provider_currency_id'
    )
    provider_amount_to_pay = fields.Monetary(
        compute='_compute_credit_amount_to_pay',
        currency_field='provider_currency_id',
        string='Credit Amount To Pay',
        store=False
    )

    @api.constrains('provider_credit_control')
    def _constrains_provider_credit_control(self):
        for partner in self:
            if partner.provider_credit_control and not partner.provider_credit_max_amount:
                raise ValidationError(
                    _("You must provide maximum credit amount when credit control is enabled")
                )

    @api.depends('provider_credit_control', 'property_purchase_currency_id')
    def _compute_provider_currency_id(self):
        """
        Modeda auxiliar para determinar el currency_field de los importes del control de crédito
        """
        for partner in self:
            if partner.provider_credit_control:
                partner.provider_currency_id = partner.property_purchase_currency_id or self.env.company.currency_id
            else:
                partner.provider_currency_id = False

    @api.depends('property_purchase_currency_id', 'provider_credit_control', 'provider_credit_max_amount')
    def _compute_credit_amount_to_pay(self):
        for partner in self:
            if partner.provider_credit_control and partner.provider_credit_max_amount:
                partner_currency = partner.property_purchase_currency_id or self.env.company.currency_id

                # En el onchange el id del registro es una instancia de models.NewId
                partner_id = partner._origin.id if isinstance(
                    partner.id, models.NewId) else partner.id

                # Importe de las facturas en la modeda del proveedor
                invoices = self.env['account.move'].search([
                    ('move_type', '=', 'in_invoice'),
                    ('partner_id', '=', partner_id),
                    ('state', '=', 'posted')
                ])
                invoiced_amount = 0
                for invoice in invoices:
                    invoiced_amount += invoice.currency_id._convert(
                        from_amount=invoice.amount_total,
                        to_currency=partner_currency,
                        company=self.env.company,
                        date=invoice.date,
                    )

                # Importe de los pagos en la modeda del proveedor
                paids = self.env['account.payment'].search([
                    ('payment_type', '=', 'outbound'),
                    ('partner_id', '=', partner_id),
                    ('state', '=', 'posted')
                ])
                paid_amount = 0
                for paid in paids:
                    paid_amount += paid.currency_id._convert(
                        from_amount=paid.amount,
                        to_currency=partner_currency,
                        company=self.env.company,
                        date=paid.date,
                    )

                partner.provider_amount_to_pay = invoiced_amount - paid_amount
            else:
                partner.provider_amount_to_pay = 0
