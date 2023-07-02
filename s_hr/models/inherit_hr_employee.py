# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    area_id = fields.Many2one('hr.area', string='Area')
    speciality_id = fields.Many2one('hr.speciality', string='Speciality')
    management_area_id = fields.Many2one(
        'hr.management.area', string='Management Area')

    is_regional = fields.Boolean('Regional')
    city = fields.Char('City')
