# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    name = fields.Char(compute="_compute_name", store=True, readonly=False)
    order_name = fields.Char(
        "Order of Name", compute="_compute_name", store=True, readonly=False
    )
    number_employee = fields.Char(
        string="Employee Number",
        readonly=True,
        required=True,
        default=lambda self: "01-01-00000",
        groups="hr.group_hr_user",
    )
    firstname = fields.Char(string="Firstname", groups="hr.group_hr_user")
    lastname = fields.Char(string="Lastname", groups="hr.group_hr_user")
    second_lastname = fields.Char(string="Second lastname", groups="hr.group_hr_user")

    @api.model
    def _get_computed_name(self, firstname, lastname, second_lastname):
        order = self.company_id.employee_names_order or "first_first"
        if order == "first_first":
            return " ".join(p for p in (firstname, lastname, second_lastname) if p)
        else:
            return " ".join(p for p in (lastname, second_lastname, firstname) if p)

    @api.depends("firstname", "lastname", "second_lastname")
    @api.onchange("firstname", "lastname", "second_lastname")
    def _compute_name(self):
        for rec in self:
            order = rec.company_id.employee_names_order or "first_first"
            if order == "first_first":
                rec.name = " ".join(
                    filter(
                        lambda x: x, [rec.firstname, rec.lastname, rec.second_lastname]
                    )
                )
            else:
                rec.name = " ".join(
                    filter(
                        lambda x: x, [rec.lastname, rec.second_lastname, rec.firstname]
                    )
                )
            rec.order_name = order

    @api.model_create_multi
    def create(self, values):
        for vals in values:
            vals["number_employee"] = self._format_sequence()

        res = super(HrEmployee, self).create(values)

        return res

    def write(self, vals):
        """
        Para el caso de la resecuencia
        """
        if "number_employee" in vals:
            vals["number_employee"] = self._format_sequence(vals["number_employee"])
        return super().write(vals)

    def _format_sequence(self):

        # Fomato de 9 de dígitos
        # sequence = (
        #         self.env["ir.sequence"].next_by_code(
        #             "hr.employee.employee.sequence.number"
        #         )
        #         or "/"
        #     )
        # first = sequence[0:3]
        # second = sequence[3:6]
        # thirth = sequence[6:]

        # return "%s-%s-%s" % (first, second, thirth)

        # Formato de 5 dígitos
        sequence = (
            self.env["ir.sequence"].next_by_code("hr.employee.employee.number") or "/"
        )
        return "01-01-%s" % sequence

    # CRON
    def _recompute_employee_names_cron(self):
        self.env.cr.execute(
            """select emp.id
            from hr_employee emp inner join res_company comp on emp.company_id = comp.id
            where emp.order_name != comp.employee_names_order
            limit 500;"""
        )
        self.env.cr.flush()
        ids = self.env.cr.fetchall()
        if ids:
            employees = self.env["hr.employee"].browse([id[0] for id in ids])
            employees._compute_name()
            if len(employees) == 500:
                # assumes there are more whenever search hits limit
                self.env.ref(
                    "s_custom_employee.ir_cron_recompute_employee_names"
                )._trigger()

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    order_name = fields.Char(readonly=True, groups="base.group_user")
    number_employee = fields.Char(readonly=True, groups="base.group_user")
    firstname = fields.Char(readonly=True, groups="base.group_user")
    lastname = fields.Char(readonly=True, groups="base.group_user")
    second_lastname = fields.Char(readonly=True, groups="base.group_user")
