# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_customer = fields.Boolean('Is customer')