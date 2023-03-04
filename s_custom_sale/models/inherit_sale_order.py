# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'sale', 'done', 'cancel'}
}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    document_type = fields.Selection(
        [("sale", "Sale"), ("requisitions", "Requisitions")],
        string="Document Type",
        default="sale",
    )

    requirements_date = fields.Datetime(
        string="Requirements date",
        required=True, readonly=False, copy=False,
        states=READONLY_FIELD_STATES,
        help="Delivery Need Date.",
        default=fields.Datetime.now
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            flag = False
            account_analytic = ""
            if vals.get('document_type') in "requisitions":
                for order in vals.get('order_line'):
                    analytic = self.env['account.analytic.account'].search([('id', '=', order[2].get('analytic_account_id'))])
                    if analytic.project_state not in 'running':
                        flag = True
                        account_analytic = analytic.name

        if flag:
            raise ValidationError(
                _(
                    "It cannot be processed because the project status of the analytical account %s is Finished" % account_analytic
                )
            )
        else:
            return super(SaleOrder, self).create(vals_list)
