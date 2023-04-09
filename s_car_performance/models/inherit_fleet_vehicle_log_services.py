from odoo import fields, models, api


class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    qty_liters_fuel = fields.Float(string="number of liters fuel")

    def _set_odometer(self):
        for record in self:

            last_odometer = self.search([('vehicle_id', '=', self.vehicle_id.id), ('qty_liters_fuel', '>', 0)], order="id desc", limit=1)
            # self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', self.vehicle_id.id)], order="id desc", limit=1).value

            super(FleetVehicleLogServices, self)._set_odometer()

            performance_car = (self.odometer - last_odometer) / self.qty_liters_fuel

            odometer = self.env['fleet.vehicle.odometer'].search([('id', '=', self.odometer_id.id)])

            odometer.write({
                'performance': performance_car,
            })


