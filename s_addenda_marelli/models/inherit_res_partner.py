# -*- encoding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_use_addenda_marelli = fields.Boolean(
        compute='checking_addenda_marelli',
        string="Use Coppel Marelli",
    )

    @api.depends('l10n_mx_edi_addenda')
    def checking_addenda_marelli(self):
        addenda_marelli_id = self.env.ref(
            's_addenda_marelli.addenda_marelli').id
        for partner in self:
            if partner.l10n_mx_edi_addenda.id == addenda_marelli_id:
                partner.partner_use_addenda_marelli = True
            else:
                partner.partner_use_addenda_marelli = False