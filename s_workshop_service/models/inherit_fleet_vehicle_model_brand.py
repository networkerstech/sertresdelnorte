from odoo import fields, models, api


class FleetVehicleModelBrand(models.Model):
    _inherit = 'fleet.vehicle.model.brand'

    mileage_for_services = fields.Float(string="Mileage for services")
    kilometers_allowed = fields.Float(string="Kilometers allowed")




