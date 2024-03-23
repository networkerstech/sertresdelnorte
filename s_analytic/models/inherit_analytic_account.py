# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.osv import expression


class AccountAnalyticPlan(models.Model):
    _inherit = "account.analytic.plan"

    accounts_sequence_id = fields.Many2one("ir.sequence", string="Accounts Sequence")

    @api.model
    def add_accounts_sequence(self):
        self.env["account.analytic.plan"].search(
            [("accounts_sequence_id", "=", False)]
        ).create_accounts_sequence()

    def get_or_create_accounts_sequence(self):
        self.ensure_one()
        if not self.accounts_sequence_id:
            self.create_accounts_sequence()
        return self.accounts_sequence_id

    def create_accounts_sequence(self):
        for plan in self:
            if not plan.accounts_sequence_id:
                plan.accounts_sequence_id = self.env["ir.sequence"].create(
                    {
                        "name": _("Analitic Plan Sequence - %d") % (plan.id),
                        "code": "ANALYTICP-%s" % (plan.id),
                        "implementation": "standard",
                        "prefix": "",
                        "suffix": "",
                        "padding": 0,
                        "company_id": self.company_id.id,
                    }
                )

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.create_accounts_sequence()
        return res

    def unlink(self):
        sequences = self.accounts_sequence_id
        res = super().unlink()
        sequences.unlink()
        return res

class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    order_number = fields.Char("Identification", default="0")

    def update_rec_names_search(self):
        """
        Es necesario incluir el id y el plan en los campos que admite el name_search
        """
        res = super().init()
        new_fields = ["order_number", "company_id", "plan_id.id", "plan_id.name"]
        for nf in new_fields:
            if nf not in self._rec_names_search:
                self._rec_names_search.append(nf)

    def name_get(self):
        result = []
        plan_ids = self.plan_id.ids
        for p_id in plan_ids:
            for record in self.filtered(lambda x: x.plan_id.id == p_id).sorted(
                "order_number"
            ):
                result.append(
                    (
                        record.id,
                        "[%(p_id)s - %(a_id)s] [%(p_name)s - %(a_name)s]"
                        % {
                            "p_id": record.plan_id.id,
                            "a_id": record.order_number,
                            "p_name": record.plan_id.name,
                            "a_name": record.name,
                        },
                    )
                )
        return result

    def get_full_search_domain(self, name):
        if name:
            domains = [
                [("name", "ilike", name)],
                [("plan_id.name", "ilike", name)],
            ]
            for part in name.split(" "):
                try:
                    domains.append([("order_number", "=", part)])
                    domains.append([("plan_id.id", "=", int(part))])
                except:
                    pass
            return expression.OR(domains)
        return []

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """
        Se busca en el nombre y el id de la cuenta y el plan
        """
        self.update_rec_names_search()
        new_args = None
        if name:
            new_args = self.get_full_search_domain(name)
            if args:
                new_args = expression.AND([args, new_args])
        return super(AccountAnalyticAccount, self).name_search(
            name, new_args, operator, limit
        )

    @api.model
    def search_read(
        self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs
    ):
        """
        Desde el widget de compras se usa search_read en lugar de name_get, por lo tanto hay que reemplazar
        la expresión del dominio asociada al nombre para que se bueque por el nombre y el id de la cuenta y el plan
        """
        name_domain = None
        if domain:
            for leaf in domain:
                if leaf[0] == "name" and leaf[2]:
                    name_domain = self.get_full_search_domain(leaf[2])
                    break

        if name_domain:
            new_domain = []
            for leaf in domain:
                if leaf[0] != "name":
                    new_domain.append(leaf)
                else:
                    for name_leaf in name_domain:
                        new_domain.append(name_leaf)
            domain = new_domain

        if not order:
            order = "plan_id,order_number"

        return super().search_read(domain, fields, offset, limit, order, **read_kwargs)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            plan_id = vals.get("plan_id", 0)
            if plan_id and vals.get("order_number", "0") == "0":
                plan = self.env["account.analytic.plan"].browse([plan_id])
                if plan:
                    sequece = plan.get_or_create_accounts_sequence()
                    seq_date = fields.Datetime.context_timestamp(
                        self, fields.Datetime.now()
                    )
                    vals["order_number"] = sequece._next(sequence_date=seq_date) or "0"
            else:
                vals["order_number"] = "0"

        return super().create(vals_list)
