# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    activity_line_id = fields.One2many(comodel_name="vehicle.activity", inverse_name="vehicle_id", string="Activity")

