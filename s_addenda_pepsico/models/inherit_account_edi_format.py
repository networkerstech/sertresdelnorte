# -*- coding: utf-8 -*-
from odoo import fields, models, api
from lxml.objectify import fromstring
from lxml import etree


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'


    @api.model
    def _l10n_mx_edi_cfdi_append_addenda(self, move, cfdi, addenda):
        ''' Append an additional block to the signed CFDI passed as parameter.
        :param move:    The account.move record.
        :param cfdi:    The invoice's CFDI as a string.
        :param addenda: (ir.ui.view) The addenda to add as a string.
        :return cfdi:   The cfdi including the addenda.
        '''
        # checking if the addenda is of walmart and then sending some params
        # requiere for it.
        if not addenda:
            return cfdi
        if addenda.id == self.env.ref('s_addenda_pepsico.pepsico').id:
            cfdi_node = fromstring(cfdi)
            cfdi_info = move._l10n_mx_edi_decode_cfdi_etree(cfdi_node)
            version = cfdi_node.get('Version')
            folio_fiscal = cfdi_info.get('uuid')
            addenda_values = {'record': move, 'cfdi': cfdi, 'folio_fiscal': folio_fiscal}
            addenda = self.env['ir.qweb']._render(addenda.id, values=addenda_values).strip()
            addenda_node = fromstring(addenda)
            # Add a root node Addenda if not specified explicitly by the user.
            if addenda_node.tag != '{http://www.sat.gob.mx/cfd/%s}Addenda' % version[0]:
                node = etree.Element(etree.QName('http://www.sat.gob.mx/cfd/%s' % version[0], 'Addenda'))
                node.append(addenda_node)
                addenda_node = node
            cfdi_node.append(addenda_node)
            return etree.tostring(cfdi_node, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        return super(AccountEdiFormat, self)._l10n_mx_edi_cfdi_append_addenda(move, cfdi, addenda)