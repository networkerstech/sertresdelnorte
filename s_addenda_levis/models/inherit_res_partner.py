# -*- encoding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_use_addenda_levis = fields.Boolean(
        compute='checking_addenda_levis',
        string="Use Coppel Levi's",
    )

    @api.depends('l10n_mx_edi_addenda')
    def checking_addenda_levis(self):
        addenda_levis_id = self.env.ref(
            's_addenda_levis.addenda_levis').id
        for partner in self:
            if partner.l10n_mx_edi_addenda.id == addenda_levis_id:
                partner.partner_use_addenda_levis = True
            else:
                partner.partner_use_addenda_levis = False