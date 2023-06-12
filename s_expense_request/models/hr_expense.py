# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrExpens(models.Model):
    _inherit = 'hr.expense'

    aux_employee_id = fields.Many2one(
        'hr.employee',
        compute='_compute_aux_employee_id',
        string='Employee',
        help='Dummy field to bypass access rights'
    )

    expense_request_id = fields.Many2one(
        'hr.expense.request',
        string='Expense Request',
        states={
            'approved': [('readonly', True)],
            'done': [('readonly', True)]
        },
        domain='[("state", "=", "approved"), ("employee_id.id", "=", aux_employee_id)]',
        ondelete="restrict"
    )


    @api.onchange('expense_request_id')
    def _onchange_expense_request_id(self):
        self.total_amount = self.expense_request_id.amount if self.expense_request_id else 0

    @api.depends('employee_id')
    def _compute_aux_employee_id(self):
        for rec in self:
            rec.aux_employee_id = rec.sudo().employee_id
