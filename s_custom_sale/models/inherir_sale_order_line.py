# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        flag = False

        for vals in vals_list:
            if self.env['sale.order'].search([('id', '=', vals.get('order_id'))]).document_type in "requisitions":
                analytic = self.env['account.analytic.account'].search([('id', '=', vals.get('analytic_account_id'))])
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
            return super(SaleOrderLine, self).create(vals_list)




