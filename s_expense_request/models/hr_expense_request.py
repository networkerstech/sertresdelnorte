# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrExpenseRequest(models.Model):
    _name = 'hr.expense.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Expense Request'

    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id

    name = fields.Char(
        'Name',
        required=True,
        readonly=True,
        states={
            'draft': [('readonly', False)]
        }
    )
    description = fields.Text(
        'Description',
        states={
            'draft': [('readonly', False)]
        }
    )
    amount = fields.Float('Amount', compute='_set_amount', store=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=_default_employee_id,
        readonly=True,
        tracking=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('to_approve', 'To approve'),
            ('approved', 'Approved'),
            ('cancel', 'Cancel')
        ],
        'State',
        default='draft'
    )
    line_ids = fields.One2many(
        'hr.expense.request.line',
        'request_id',
        'Lines',
        readonly=True,
        states={
            'draft': [('readonly', False)]
        }
    )

    @api.constrains('line_ids')
    def _constrains_line_ids(self):
        for line in self.line_ids:
            if not line.quantity or not line.price_unit:
                raise ValidationError(_('You must provide quantity and price'))

    @api.depends('line_ids')
    def _set_amount(self):
        for rec in self:
            rec.amount = sum([l.amount for l in rec.line_ids])

    def unlink(self):
        for rec in self:
            if rec.state == 'approved':
                raise ValidationError(_('Can not delete a approved record.'))
        return super().unlink()

    def action_to_approve(self):
        self.state = 'to_approve'

    def action_approved(self):
        self.state = 'approved'

    def action_cancel(self):
        self.state = 'cancel'

    def action_draft(self):
        self.state = 'draft'


class HrExpenseRequest(models.Model):
    _name = 'hr.expense.request.line'

    request_id = fields.Many2one('hr.expense.request', 'Request')
    name = fields.Char('Detail', required=True)
    quantity = fields.Float('Quantity')
    price_unit = fields.Float('Price')
    amount = fields.Float('Amount', compute='_set_amount', store=True)

    @api.depends('quantity', 'price_unit')
    def _set_amount(self):
        for rec in self:
            rec.amount = rec.price_unit * rec.quantity
