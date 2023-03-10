# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    name = fields.Char(compute="_compute_name", store=True, readonly=False)
    number_employee = fields.Char(string="Employee Number", readonly=True, required=True, default=lambda self: '01-01-00000')
    firstname = fields.Char(string="Firstname")
    lastname = fields.Char(string="Lastname")
    second_lastname = fields.Char(string="Second lastname")

    @api.model
    def _get_names_order(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("partner_names_order", "first_last")
        )

    @api.model
    def _get_computed_name(self, firstname, lastname, second_lastname):
        order = self._get_names_order()
        if order == "first_last":
            return " ".join(p for p in (firstname, lastname, second_lastname) if p)
        else:
            return " ".join(p for p in (lastname, firstname, second_lastname) if p)

    @api.depends("firstname", "lastname", "second_lastname")
    @api.onchange("firstname", "lastname", "second_lastname")
    def _compute_name(self):
        for rec in self:
            rec.name = rec._get_computed_name(rec.firstname, rec.lastname, rec.second_lastname)

    @api.model_create_multi
    def create(self, values):
        for vals in values:
            sequence = self.env['ir.sequence'].next_by_code('hr.employee.employee.number') or '/'

            vals['number_employee'] = "01-01-%s" % sequence

        res = super(HrEmployee, self).create(values)

        return res










