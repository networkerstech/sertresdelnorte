# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrExpense(models.Model):
    _inherit = 'hr.expense'



class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    expense_request_id = fields.Many2one(
        'hr.expense.request',
        string='Expense Request',
        readonly=True,
        states={
            'draft': [('readonly', False)],
        },
        domain='[("state", "=", "approved"), ("employee_id.id", "=", employee_id)]',
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
