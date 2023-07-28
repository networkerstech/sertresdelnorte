from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_repr
import re


class AccountMove(models.Model):
    _name = "hr.expense"
    _inherit = ["hr.expense", "l10n.mx.edi.uuid.verification.tools"]

    l10n_mx_edi_cfdi_uuid = fields.Char(
        string='Fiscal Folio', copy=False,
        help='Folio in electronic invoice, is returned by SAT when send to stamp.',
    )
    l10n_mx_edi_sat_status = fields.Selection(
        selection=lambda self: self.env['account.move']._fields['l10n_mx_edi_sat_status'].selection,
        string='Sat status',
        default='none'
    )
    l10n_mx_edi_status_change_date = fields.Date(
        'Status change date'
    )
    l10n_mx_edi_cfdi_supplier_rfc = fields.Char(
        string='Supplier RFC',
        copy=False,
        readonly=True,
        help='The supplier tax identification number.',
        compute='_compute_cfdi_values')
    l10n_mx_edi_cfdi_customer_rfc = fields.Char(
        string='Customer RFC',
        copy=False,
        readonly=True,
        help='The customer tax identification number.',
        compute='_compute_cfdi_values')

    l10n_mx_edi_status_change_date_supplier = fields.Date(
        'Status change date'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Si se establece el uuid el estado SAT en no definido
        hasta tanto no se verifique contra el SAT
        """
        for vals in vals_list:
            if 'l10n_mx_edi_cfdi_uuid' in vals and vals.get('l10n_mx_edi_cfdi_uuid', False):
                vals.update({
                    'l10n_mx_edi_sat_status': 'none',
                    'l10n_mx_edi_status_change_date_supplier': False,
                })
        return super().create(vals)

    def write(self, vals):
        """
        Si se establece el uuid el estado SAT en no definido
        hasta tanto no se verifique contra el SAT
        """
        if 'l10n_mx_edi_cfdi_uuid' in vals and vals.get('l10n_mx_edi_cfdi_uuid', False):
            vals.update({
                'l10n_mx_edi_sat_status': 'none',
                'l10n_mx_edi_status_change_date_supplier': False,
            })
        return super().write(vals)

    @api.constrains('l10n_mx_edi_cfdi_uuid')
    def constrains_l10n_mx_edi_cfdi_uuid_(self):
        """
        Validaciones asociadas al cfdi de las facturas de proveedor
        """
        self.check_l10n_mx_edi_cfdi_uuid()
        for rec in self:
            def on_error(ex):
                raise ValidationError(
                    _("Failure during update of the SAT status: %(msg)s") % {
                        "msg": str(ex)
                    }
                )
            status = rec.get_l10n_mx_edi_uuid_sat_status(on_error)
            if status != 'Vigente':
                raise ValidationError(
                    _('Invoice SAT status is: "%(msg)s"') % {
                        "msg": status
                    }
                )

    def _compute_cfdi_values(self):
        for rec in self:
            rec.l10n_mx_edi_cfdi_supplier_rfc = ''
            rec.l10n_mx_edi_cfdi_customer_rfc = self.env.company.vat

    def action_update_vendor_sat_status(self):
        self.l10n_mx_edi_update_vendor_sat_status()

    def l10n_mx_edi_update_vendor_sat_status(self):
        '''
        Validar que los uuids de las facturas de proveedores son válidos.
        Si cambia de estado y se indican usuarios, notificarlos
        '''

        for move in self:
            def on_error(ex):
                move.message_post(
                    body=_("Failure during update of the SAT status: %(msg)s", msg=str(ex)))

            status = move.get_l10n_mx_edi_uuid_sat_status(on_error)
            if status:
                new_status = move.get_l10n_mx_edi_status_from_sat_status(
                    status)
                old_status = move.l10n_mx_edi_sat_status
                description_selection_dict = dict(
                    self.env[self._name]._fields['l10n_mx_edi_sat_status']._description_selection(self.with_context(lang=self.env.user.lang).env))
                if new_status != old_status:
                    move.l10n_mx_edi_sat_status = new_status
                    move.l10n_mx_edi_status_change_date_supplier = fields.Date.today()
                    move.message_post(
                        body=_('Status for the invoice change from "%s" to "%s"') % (
                            _(description_selection_dict[old_status]),
                            _(description_selection_dict[new_status])
                        ),
                    )

    def get_l10n_mx_edi_cfdi_supplier_rfc(self):
        return self.l10n_mx_edi_cfdi_supplier_rfc

    def get_l10n_mx_edi_cfdi_customer_rfc(self):
        return self.l10n_mx_edi_cfdi_customer_rfc

    def get_l10n_mx_edi_cfdi_amount(self):
        return float_repr(self.total_amount,
                          precision_digits=self.currency_id.decimal_places)

    def get_l10n_mx_edi_cfdi_uuid(self):
        return self.l10n_mx_edi_cfdi_uuid

    def get_l10n_mx_edi_cfdi_unique_uuid_domain(self):
        return [('id', '!=', self.id), ('l10n_mx_edi_cfdi_uuid', '=', self.l10n_mx_edi_cfdi_uuid)]
