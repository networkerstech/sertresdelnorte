# -*- coding: utf-8 -*-
from odoo import _, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    supplier_id = fields.Char(
        string='idSupplier',
        help="This information is given by PEPSICO")
