# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ActivityParameters(models.Model):
    _name = 'activity.parameters'
    _description = 'Description'
    _rec_name = "parameter"

    parameter = fields.Char(string="Parameter", help="Name of activity")
    responsible_id = fields.Many2one('res.users', 'Responsible', store=True, readonly=False)
    criteria_days = fields.Integer(string='Criteria days', help="Quantity expressed in days")
    active = fields.Boolean(string='Active', default=True)

