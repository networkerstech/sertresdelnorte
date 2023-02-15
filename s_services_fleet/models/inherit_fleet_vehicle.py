# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from odoo.tools import format_date


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    creation_scheduled_activity = fields.Boolean(default=False)

    @api.model
    def _cron_check_vehicle_service_validity(self):
        list_services = self.env['vehicle.service'].search([("active", "=", True)])
        list_vehicles = self.search([])
        flag = False

        for s in list_services:
            outdated_days = fields.Date.today() + relativedelta(days=-s.criteria_days)
            out_kms = s.criteria_km
            employee = s.responsible_id

            for v in list_vehicles:
                if len(v.log_services.filtered(lambda x: x.service_type_id == s.services_id)) > 0:
                    for service in v.log_services.filtered(lambda x: x.service_type_id == s.services_id):
                        # si existe un servicio en etapa de nuevo
                        item = len(v.log_services.filtered(lambda x: x.service_type_id == s.services_id and x.state in ("new", "running")))
                        # Si ya tiene el servicio en su log y el estado es hecho chequeo la fecha o el odómetro para ver si se cumple
                        if service and service.state in "done" and item == 0:
                            if (fields.Date.today() - service.date).days >= s.criteria_days or (v.odometer - service.odometer) >= out_kms:
                                flag = True
                else:
                    if v.odometer >= out_kms:
                        flag = True

                if flag:
                    vals = ({
                        "vehicle_id": v.id,
                        "description": _("Automatic creation of service"),
                        "date": fields.Date.today(),
                        "service_type_id": s.services_id.id,
                        "purchaser_id": v.driver_id.id,
                        "odometer": v.odometer
                    })
                    self.env["fleet.vehicle.log.services"].create(vals)

                    if employee:
                        v.activity_schedule(
                            'mail.mail_activity_data_todo',
                            note=_('The vehicle with license plate %(vehicle)s is responsible for carrying out the service %(service)s',
                                   vehicle=v.license_plate,
                                   service=s.display_name),
                            user_id=employee.id)

                    flag = False
