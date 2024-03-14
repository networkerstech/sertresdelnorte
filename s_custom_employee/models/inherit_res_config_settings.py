# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    employee_names_order = fields.Selection(
        [("first_first", "First name first"), ("last_first", "Last name first")],
        string="Employee names order",
        default="last_first",
    )

    def write(self, vals):
        if "employee_names_order" in vals:
            self.env.ref(
                "s_custom_employee.ir_cron_recompute_employee_names"
            )._trigger()
        return super().write(vals)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    employee_names_order = fields.Selection(
        related="company_id.employee_names_order", string="Employee names order", readonly=False
    )
