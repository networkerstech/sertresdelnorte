# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', company_dependent=True)
