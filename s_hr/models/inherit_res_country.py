# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.osv import expression


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get('filter_current_company'):
            company_country_states_domain = [
                ('country_id', '=', self.env.company.country_id.id)]
            if not args:
                args = company_country_states_domain
            else:
                args = expression.AND([args, company_country_states_domain])
        return super().search(args, offset, limit, order, count)
