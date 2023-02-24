# -*- coding: utf-8 -*-

from odoo import fields, models, api


READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'sale', 'done', 'cancel'}
}

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    document_type = fields.Selection(
        [("sale", "Sale"), ("requisitions", "Requisitions")],
        string="Document Type",
        default="sale",
    )

    requirements_date = fields.Datetime(
        string="Requirements date",
        required=True, readonly=False, copy=False,
        states=READONLY_FIELD_STATES,
        help="Delivery Need Date.",
        default=fields.Datetime.now
    )
