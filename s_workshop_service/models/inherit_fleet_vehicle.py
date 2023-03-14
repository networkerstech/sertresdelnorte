from odoo import fields, models, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    service_in = fields.Selection(
        [("workshop", "Workshop"), ("agency", "Agency")],
        string="Service in",
        required=True,
        default="workshop",
    )
