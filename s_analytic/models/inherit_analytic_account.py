# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.osv import expression


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def init(self):
        """
        Es necesario incluir el id y el plan en los campos que admite el name_search
        """
        res = super().init()
        new_fields = ['id', 'plan_id.id', 'plan_id.name']
        for nf in new_fields:
            if nf not in self._rec_names_search:
                self._rec_names_search.append(nf)
        return res

    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id, "[%(p_id)s - %(a_id)s] [%(p_name)s - %(a_name)s]" % {
                    "p_id": record.plan_id.id,
                    "a_id": record.id,
                    "p_name": record.plan_id.name,
                    "a_name": record.name,
                })
            )
        return result

    def get_full_search_domain(self, name):
        if name:
            domains = [
                [('name', 'ilike', name)],
                [('plan_id.name', 'ilike', name)],
            ]
            for part in name.split(' '):
                try:
                    domains.append([('id', '=', int(part))])
                    domains.append([('plan_id.id', '=', int(part))])
                except:
                    pass
            return expression.OR(domains)
        return []

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Se busca en el nombre y el id de la cuenta y el plan
        """
        new_args = None
        if name:
            new_args = self.get_full_search_domain(name)
            if args:
                new_args = expression.OR(args, new_args)
        return super().name_search(name, args, operator, limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        """
        Desde el widget de compras se usa search_read en lugar de name_get, por lo tanto hay que reemplazar 
        la expresión del dominio asodiada al nombre para que se bueque por el nombre y el id de la cuenta y el plan
        """
        name_domain = None
        if domain:
            for leaf in domain:
                if leaf[0] == 'name' and leaf[2]:
                    name_domain = self.get_full_search_domain(leaf[2])
                    break

        if name_domain:
            new_domain = []
            for leaf in domain:
                if leaf[0] != 'name':
                    new_domain.append(leaf)
                else:
                    for name_leaf in name_domain:
                        new_domain.append(name_leaf)
            domain = new_domain

        return super().search_read(domain, fields, offset, limit, order, **read_kwargs)
