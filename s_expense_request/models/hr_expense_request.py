# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from datetime import timedelta

DAYS_AGO_TO_CHECK_REQUESTS = 15
DAYS_INTERVAL_TO_CHECK_REQUESTS = 365


class HrExpenseRequest(models.Model):
    _name = 'hr.expense.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'analytic.mixin']
    _description = 'Expense Request'

    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company)

    name = fields.Char(
        'Name',
        required=True,
        readonly=True,
        tracking=True,
        states={'draft': [('readonly', False)]},
    )
    expense_reason = fields.Char(
        'Expense Reason',
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    description = fields.Text(
        'Description',
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    request_date = fields.Date(
        'Request Date',
        tracking=True,
        default=lambda self: fields.Date.context_today(self),
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_start = fields.Date(
        'Date Start',
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_end = fields.Date(
        'Date End',
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    amount = fields.Float('Amount', compute='_set_amount', store=True)
    checked_amount = fields.Float(
        compute='_set_checked_state', string='Checked Amount', store=True)
    product_id = fields.Many2one(
        'product.product',
        string='Category',
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('can_be_expensed', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        ondelete='restrict'
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=_default_employee_id,
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    payment_mode = fields.Selection(
        [
            ("own_account", "Employee (to reimburse)"),
            ("company_account", "Company")
        ],
        default='own_account',
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        string="Paid By")

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('requested', 'Requested'),
            ('approved', 'Approved'),
            ('cancel', 'Cancel')
        ],
        'State',
        default='draft',
        tracking=True
    )
    checked_state = fields.Selection(
        [
            ('not_checked', 'Not checked'),
            ('partial', 'Partial'),
            ('checked', 'Checked'),
        ],
        string='Checked',
        default='not_checked',
        compute='_set_checked_state',
        store=True
    )
    time_state = fields.Selection(
        [
            ('in_time', 'In time'),
            ('expire', 'Expired')
        ],
        string='Current state',
        default='in_time',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    line_ids = fields.One2many(
        'hr.expense.request.line',
        'request_id',
        'Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    expense_sheet_ids = fields.One2many(
        'hr.expense.sheet',
        'expense_request_id',
        'Expense Reports',
        domain=[('state', 'in', ('approve', 'post', 'done'))]
    )
    product_has_cost = fields.Boolean(
        "Is product with non zero cost selected", compute='_set_product_has_cost')

    @api.constrains('line_ids')
    def _constrains_line_ids(self):
        for request in self:
            for line in request.line_ids:
                if not line.quantity or not line.price_unit:
                    raise ValidationError(
                        _('You must provide quantity and price'))

    @api.constrains('date_start', 'date_end')
    def _constrains_dates(self):
        for request in self:
            if request.date_start > request.date_end:
                raise ValidationError(
                    _('The end date must be later than the initial date'))

    @api.depends('line_ids')
    def _set_amount(self):
        for rec in self:
            rec.amount = sum([l.amount for l in rec.line_ids])

    @api.depends('product_id')
    def _set_product_has_cost(self):
        for expense_req in self:
            expense_req.product_has_cost = expense_req.product_id and (float_compare(
                expense_req.product_id.standard_price, 0.0, precision_digits=2) != 0)

    @api.depends('expense_sheet_ids')
    def _set_checked_state(self):
        for rec in self:
            if rec.expense_sheet_ids:
                ck_amount = sum(
                    [es.total_amount for es in rec.expense_sheet_ids])
                if rec.checked_amount != ck_amount:
                    if ck_amount > rec.amount:
                        rec.checked_amount = rec.amount
                    else:
                        rec.checked_amount = ck_amount

                    if ck_amount == 0 and rec.checked_state != 'not_checked':
                        rec.checked_state = 'not_checked'
                    elif ck_amount < rec.amount and rec.checked_state != 'partial':
                        rec.checked_state = 'partial'
                    elif ck_amount >= rec.amount and rec.checked_state != 'checked':
                        rec.checked_state = 'checked'

    def unlink(self):
        for rec in self:
            if rec.state == 'approved':
                raise ValidationError(_('Can not delete a approved record.'))
        return super().unlink()

    def action_check_expense_state(self):
        """
        Actualzar el estado de la comprobación del gasto y si la tarea 
        está en tiempo, por si por algún motivo no se actualizara con 
        los campos compute o el cron 
        """
        self._set_checked_state()
        interval_date = fields.Date.today() + timedelta(days=-DAYS_AGO_TO_CHECK_REQUESTS)
        if self.date_end < interval_date:
            if self.checked_state == 'not_checked' and self.time_state != 'expire':
                self.time_state = 'expire'

    def action_request(self):
        self.state = 'requested'

    def action_approved(self):
        self.state = 'approved'

    def action_cancel(self):
        self.state = 'cancel'

    def action_draft(self):
        self.state = 'draft'

    def action_draft(self):
        self.state = 'draft'

    @api.model
    def update_expense_request_time_state_cron(self, days=DAYS_AGO_TO_CHECK_REQUESTS):
        today = fields.Date.today()
        # Chequear un año de solicitudes anteriores a los últimos 15 días
        # para evitar que se chequeen todas las tareas y que se queden
        # tareas sin verificar, por que se desactivó la tarea programada por ejemplo
        # TODO: mejorar esto

        expired_requests = self.search([
            ('date_end', '<', today + timedelta(days=-days)),
            ('date_start', '>', today +
             timedelta(days=-(DAYS_INTERVAL_TO_CHECK_REQUESTS))),
        ])
        for req in expired_requests:
            if req.checked_state == 'not_checked' and req.time_state != 'expire':
                req.time_state = 'expire'


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
