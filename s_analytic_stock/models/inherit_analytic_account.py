# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.osv import expression


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    picking_type = fields.Selection([
        ('incoming', 'Return'),
        ('outgoing', 'Shipment'),
    ], string='Picking Type')

    cost = fields.Float('Cost')