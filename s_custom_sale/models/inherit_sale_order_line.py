# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    type_document = fields.Char(
       default='requisitions'
    )
