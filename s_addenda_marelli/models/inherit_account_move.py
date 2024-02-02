# -*- coding: utf-8 -*-
from odoo import fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    mirelli_po_number = fields.Char(
        string='Number of PO',
        copy=False,
    )

    mirelli_line_number = fields.Char(
        string='Number of line',
        copy=False,
    )
    mirelli_item_number = fields.Char(
        string='Number of Item',
        copy=False,
    )
    
    partner_use_addenda_marelli = fields.Boolean(
        string="Use Addenda Marelli",
        related='partner_id.partner_use_addenda_marelli',
    )
    
    def w_get_cfdi_values(self):
        self.ensure_one()
        edi=self._get_l10n_mx_edi_signed_edi_document()
        values=edi.edi_format_id._l10n_mx_edi_get_serie_and_folio(self)
        if self._context.get('get_folio', False):
            folio = values.get('folio_number', False) or ''
            return folio
        elif self._context.get('get_serie', False):
            serie = values.get('serie_number', False) or ''
            return serie

