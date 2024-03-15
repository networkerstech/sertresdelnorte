# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    addenda_pepsico = fields.Boolean(
        string='Addenda Pepsico',
        compute='_use_addenda_pepsico',
        help='Technical field that helps us to identify if the partner '
             'uses the Addenda Pepsico.'
    )

    @api.depends('l10n_mx_edi_addenda')
    def _use_addenda_pepsico(self):
        """
            Validates if the partner uses the Addenda Pepsico.
        """
        addenda_pepsico = self.env.ref('s_addenda_pepsico.pepsico').id
        for partner in self:
            if partner.l10n_mx_edi_addenda.id == addenda_pepsico:
                partner.addenda_pepsico = True
            else:
                partner.addenda_pepsico = False