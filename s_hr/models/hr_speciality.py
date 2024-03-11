# -*- coding: utf-8 -*-

from odoo import fields, models

class HrSpeciality(models.Model):
    _name = 'hr.speciality'
    _description = 'Employee Speciality'
    
    name = fields.Char('Name')