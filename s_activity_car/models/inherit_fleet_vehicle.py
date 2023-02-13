from odoo import fields, models, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def write(self, vals):

        old_driver = self.driver_id

        res = super(FleetVehicle, self).write(vals)

        if res:
            activity_list = self.env["mail.activity"].search([]).filtered(lambda x: x.user_id == old_driver.user_id and x.res_model == 'fleet.vehicle')

            if activity_list:
                value = ({
                    'user_id': vals['driver_id']
                })
                for a in activity_list:
                    a.write(value)



