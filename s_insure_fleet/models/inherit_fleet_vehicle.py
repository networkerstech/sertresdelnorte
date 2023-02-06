# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from odoo.tools import format_date


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    insurance_start_date = fields.Date(string="Start date")
    insurance_end_date = fields.Date(string="End date")
    insurance_scheduled_activity = fields.Boolean(default=False)

    cargo_start_date = fields.Date(string="Start date")
    cargo_end_date = fields.Date(string="End date")
    cargo_scheduled_activity = fields.Boolean(default=False)


    @api.model
    def _cron_check_insurance_policy_validity(self):

        insurance = self.env['insurance.policy'].search([], limit=1)
        outdated_days = fields.Date.today() + relativedelta(days=+insurance.criteria_days)
        employee = insurance.responsible_id

        expired_insurance_policy = self.search([('insurance_scheduled_activity', '=', False), ('insurance_end_date', '<', outdated_days)])

        for vehicle in expired_insurance_policy:
            if employee:
                lang = self.env['res.partner'].browse(employee.id).lang
                formated_date = format_date(vehicle.env, vehicle.insurance_end_date, date_format="dd MMMM y", lang_code=lang)
                vehicle.activity_schedule(
                    'mail.mail_activity_data_todo',
                    note=_('The insurance policy for the vehicles with registration %(vehicle)s expires expires at %(date)s.',
                           vehicle=vehicle.license_plate,
                           date=formated_date),
                    user_id=employee.id)

            vehicle.write({'insurance_scheduled_activity': True})

    @api.model
    def _cron_check_cargo_permit_validity(self):

        cargo = self.env['cargo.permit'].search([], limit=1)
        outdated_days = fields.Date.today() + relativedelta(days=+cargo.criteria_days)
        employee = cargo.responsible_id

        expired_cargo_permit = self.search([('insurance_scheduled_activity', '=', False), ('cargo_end_date', '<', outdated_days)])

        for vehicle in expired_cargo_permit:
            if employee:
                lang = self.env['res.partner'].browse(employee.id).lang
                formated_date = format_date(vehicle.env, vehicle.cargo_end_date, date_format="dd MMMM y", lang_code=lang)
                vehicle.activity_schedule(
                    'mail.mail_activity_data_todo',
                    note=_('The cargo permit of %(vehicle)s expires at %(date)s.',
                           vehicle=vehicle.license_plate,
                           date=formated_date),
                    user_id=employee.id)

            vehicle.write({'cargo_scheduled_activity': True})
