from odoo import fields, models, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def write(self, vals):
        import pdb; pdb.set_trace()
        old_driver = self.env['res.users'].search([('partner_id', '=', self.driver_id.id)])
        res = super(FleetVehicle, self).write(vals)
        new_driver = self.env['res.users'].search([('partner_id', '=', vals.get("driver_id"))])

        if res and old_driver:
            activity_list = self.env["mail.activity"].search([('res_model', '=', 'fleet.vehicle')]).filtered(lambda x: x.user_id == old_driver)
            if activity_list:
                for rec in activity_list:
                    rec.write(
                        {
                            "user_id": new_driver
                        }
                    )
