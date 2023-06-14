# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrExpense(models.Model):
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
        domain='[("state", "=", "approved"), ("checked_state", "=", "not_checked"), ("employee_id.id", "=", aux_employee_id)]',
        ondelete="restrict"
    )

    @api.onchange('expense_request_id')
    def _onchange_expense_request_id(self):
        self.total_amount = self.expense_request_id.amount if self.expense_request_id else 0

    @api.depends('employee_id')
    def _compute_aux_employee_id(self):
        for rec in self:
            rec.aux_employee_id = rec.sudo().employee_id


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    expense_request_id = fields.Many2one(
        'hr.expense.request',
        string='Expense Request',
        readonly=True,
        states={
            'draft': [('readonly', False)],
        },
        domain='[("state", "=", "approved"), ("checked_state", "=", "not_checked"), ("employee_id.id", "=", employee_id)]',
        ondelete="restrict"
    )

    amount_to_check = fields.Float(
        related='expense_request_id.amount', string='Amount to Check')
    un_checked_amount = fields.Float(
        compute='_set_un_checked_amount', string='Remaining Amount to Check')

    @api.depends('amount_to_check', 'total_amount')
    def _set_un_checked_amount(self):
        for rec in self:
            if rec.expense_request_id:
                rec.un_checked_amount = rec.amount_to_check - rec.total_amount
            else:
                rec.un_checked_amount = 0

    def write(self, vals):
        return super().write(vals)
