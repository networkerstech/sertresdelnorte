# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class VehicleService(models.Model):
    _inherit = "vehicle.service"

               
    @api.onchange('responsible_id')
    def _onchange_responsible(self):
        '''
        Cuando se modifica el responsable se actualizan todos los log service relacionados al service_id
        :param self:
        '''
        #TODO: Busncado los log service relacionados al service_id
        log_services = self.env['fleet.vehicle.log.services'].search([("service_type_id", "=", self.services_id.id),("state", "in", ['new','running'])])
        #TODO: Se recorre todo los log service se le modifica el responsable
        for ls in log_services:
            ls.mail_activity.user_id = self.responsible_id.id
