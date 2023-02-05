# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import fields, models, api

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Vehicle"
    )
    odometer = fields.Float(string='Last Odometer')
    fuel_type = fields.Char(string='Fuel Type')
    loaded_liters = fields.Float(string="Loaded liters")
    cost_liter = fields.Float(string="Cost liter")
    total_cost = fields.Float(string="Total cost", compute="_compute_total_cost", store=True)


    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        for item in self:
            self.odometer = item.vehicle_id.odometer
            self.fuel_type = item.vehicle_id.fuel_type

    @api.depends('cost_liter', 'loaded_liters')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.loaded_liters * rec.cost_liter

