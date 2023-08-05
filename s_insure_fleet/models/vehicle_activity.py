# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from odoo.tools import format_date
from datetime import datetime


class VehicleActivity(models.Model):
    _name = 'vehicle.activity'
    _description = 'Description'

    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle", string="Vehicle")
    activity_ids = fields.Many2one(comodel_name="activity.parameters", string="Activity")
    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    scheduled_activity = fields.Boolean(string="scheduled activity", default=False)

    def write(self, vals):
        if "end_date" in vals and self.end_date < datetime.strptime(vals.get("end_date"), '%Y-%m-%d').date():
            vals.update({
                'scheduled_activity': False
            })

        res = super(VehicleActivity, self).write(vals)

    @api.model
    def _cron_check_activity_validity(self):

        for act in self.env["activity.parameters"].search([]):
            out_dated = fields.Date.today() + relativedelta(days=+act.criteria_days)
            responsible = act.responsible_id

            expired_activity = self.search(
                [
                    ('scheduled_activity', '=', False),
                    ('end_date', '<=', out_dated)
                ]
            ).filtered(lambda x: x.activity_ids == act)

            for rec in expired_activity:
                if responsible:
                    lang = responsible.lang
                    formated_date = format_date(rec.env, rec.end_date, date_format="dd MMMM y", lang_code=lang)

                    vehicle = self.env["fleet.vehicle"].search([]).filtered(lambda x: x.id == rec.vehicle_id.id)

                    vehicle.activity_schedule(
                        'mail.mail_activity_data_todo',
                        note=_('%(activity)s expires on date %(date)s for the vehicle with registration %(vehicle)s.',
                               activity=act.parameter,
                               date=formated_date,
                               vehicle=vehicle.license_plate),
                        user_id=responsible.id
                    )

                rec.write({
                    'scheduled_activity': True,
                })
