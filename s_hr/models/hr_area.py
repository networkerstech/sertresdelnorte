# -*- coding: utf-8 -*-

from odoo import fields, models

class HrArea(models.Model):
    _name = 'hr.area'
    _description = 'Humar Resources Area'
    
    name = fields.Char('Name')