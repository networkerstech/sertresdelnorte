# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons.sale.models.sale_order import READONLY_FIELD_STATES
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    foreign_currency = fields.Boolean(
        compute="_compute_foreign_currency",
        string="Foreign Currency",
        help="Auxiliary field to handle the visualization of the elements of the view",
    )

    use_manual_rate = fields.Boolean(
        "Set Exchange Rate", default=False, states=READONLY_FIELD_STATES
    )
    manual_currency_id = fields.Many2one(
        "res.currency",
        default=False,
        string="Manual Currency",
        states=READONLY_FIELD_STATES,
    )
    manual_rate = fields.Float(
        "Exchange Rate",
        default=0,
        states=READONLY_FIELD_STATES,
        digits="Manual exchange rate for sales",
    )

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    @api.onchange("pricelist_id")
    def _onchange_pricelist_id_update_manual_currency_id(self):
        """
        Establecer por defecto la divisa de la lista de precios
        """
        for rec in self:
            rec.manual_currency_id = (
                rec.pricelist_id.currency_id or rec.env.company.currency_id
            )

    @api.depends("company_id", "manual_currency_id")
    def _compute_foreign_currency(self):
        """
        Campo auxiliar para usar en los dominios en la vista si la divisa no es la de la compañía
        """
        for rec in self:
            rec.foreign_currency = (
                rec.company_id.currency_id.id != rec.manual_currency_id.id
            )

    def _prepare_invoice(self):
        """
        Si la moneda es diferente a la moneda de la compañía y está indicado que se va a utilizar
        tipo de cambio manual, crear la factura en la moneda indicada
        """
        res = super()._prepare_invoice()
        if self.foreign_currency and self.manual_currency_id:
            res.update(
                {
                    "use_manual_rate": True,
                    "currency_id": self.manual_currency_id.id,
                    "manual_rate": self.manual_rate,
                }
            )
        return res

    @api.constrains(
        "foreign_currency", "manual_currency_id", "use_manual_rate", "manual_rate"
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

            # Garantizar la consistencia de los datos para agrupar
            # las facturas por moneda manual y tasa de cambio manual
            # Se valida que el valor del parámetro que se quiere
            # modificar sea distinto al valor que se quiere establecer
            # para evitar error de recursion depth
            vals = {}
            if not rec.foreign_currency and rec.use_manual_rate != False:
                vals.update({"use_manual_rate": False})
            if not rec.use_manual_rate and rec.manual_rate != 0:
                vals.update({"manual_rate": 0})
            if vals:
                rec.write(vals)

    def _get_invoice_grouping_keys(self):
        """
        Agrupar las facturas por la divisa y la tasa de cambio para evitar inconsistencias
        en los datos introducidas por el tipo de cambio entre los diferentes tipos de tasa
        de cambio manuales de las facturas en la misma moneda
        original:
            ['company_id', 'partner_id', 'currency_id']
        se extiende 'currency_id' a:
            ['currency_id', 'manual_rate']
        """
        res = super()._get_invoice_grouping_keys()
        if self.filtered(lambda x: x.foreign_currency and x.use_manual_rate):
            res.extend(["manual_rate"])
        return res
