# -*- coding: utf-8 -*-

from odoo import fields, models

class HrBusinessManagementArea(models.Model):
    _name = 'hr.management.area'
    _description = 'Management Area'
    
    name = fields.Char('Name')