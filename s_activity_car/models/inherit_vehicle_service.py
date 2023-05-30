# -*- coding: utf-8 -*-

from odoo import fields, models, api


class VehicleService(models.Model):
    _inherit = "vehicle.service"

    def write(self, vals):

        old_resp = self.responsible_id
        res = super(VehicleService, self).write(vals)

        activity_list = self.env["mail.activity"].search([]).filtered(lambda x: x.user_id == old_resp and x.res_model == 'fleet.vehicle')

        if activity_list:
            value = ({
                'user_id': vals['responsible_id']
            })
            for a in activity_list:
                a.write(value)
