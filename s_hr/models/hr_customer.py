# -*- coding: utf-8 -*-

from odoo import fields, models

class HrCustomer(models.Model):
    _name = 'hr.customer'
    _description = 'Customer'
    
    name = fields.Char('Name')