# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from odoo.tools import format_date


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    creation_scheduled_activity = fields.Boolean(default=False)

    @api.model
    def _cron_check_vehicle_service_validity(self):
        list_services = self.env['vehicle.service'].search([])
        list_vehicles = self.search([])

        for s in list_services:
            outdated_days = fields.Date.today() + relativedelta(days=+s.criteria_days)
            out_kms = s.criteria_km
            employee = s.responsible_id

            for v in list_vehicles:
                last_date = v.log_services.filtered(lambda x: x.id == s.id).date
                if (last_date and (outdated_days - last_date).days >= s.criteria_days) or v.odometer >= out_kms:
                    if employee:
                        v.activity_schedule(
                            'mail.mail_activity_data_todo',
                            note=_('The vehicle with license plate %(vehicle) is responsible for carrying out the vehicle service %(service).',
                                   vehicle=v.license_plate,
                                   service=s.display_name),
                            user_id=employee.id)
