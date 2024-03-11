# -*- coding: utf-8 -*-

from odoo import fields, models


class ActivityType(models.Model):
    _name = 'hr.activity.type'
    _description = 'Activity type'

    name = fields.Char('Name')
