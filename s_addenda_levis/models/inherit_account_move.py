# -*- coding: utf-8 -*-
from odoo import fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    partner_use_addenda_levis = fields.Boolean(
        string="Use Addenda Levi's",
        related='partner_id.partner_use_addenda_levis',
    )
