from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_repr
import re


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "l10n.mx.edi.uuid.verification.tools"]

    # campo auxiliar para poder usar en la vista dado que el original es compute
    l10n_mx_edi_cfdi_uuid_supplier = fields.Char(
        string='Providers Auxiliar Fiscal Folio',
        copy=False,
        default='',
        help='Folio in electronic invoice, is returned by SAT when send to stamp.',
    )
    l10n_mx_edi_status_change_date_supplier = fields.Date(
        'Status change date'
    )
    # Campo auxiliar para mostrar en la vista
    l10n_mx_edi_sat_status_supplier = fields.Selection(
        related='l10n_mx_edi_sat_status',
        readonly=True,
        help="Refers to the status of the journal entry inside the SAT system."
    )

    has_cfdi = fields.Boolean(compute='_compute_has_cfdi', string='Has Cfdi')

    @api.model_create_multi
    def create(self, vals_list):
        """
        Si se establece el uuid el estado SAT en no definido
        hasta tanto no se verifique contra el SAT
        """
        for vals in vals_list:
            if 'l10n_mx_edi_cfdi_uuid_supplier' in vals and vals.get('l10n_mx_edi_cfdi_uuid_supplier', False):
                vals.update({
                    'l10n_mx_edi_sat_status': 'undefined',
                    'l10n_mx_edi_status_change_date_supplier': False,
                })
        return super().create(vals)

    def write(self, vals):
        """
        Si se establece el uuid el estado SAT en no definido
        hasta tanto no se verifique contra el SAT
        """
        if 'l10n_mx_edi_cfdi_uuid_supplier' in vals and vals.get('l10n_mx_edi_cfdi_uuid_supplier', False):
            vals.update({
                'l10n_mx_edi_sat_status': 'undefined',
                'l10n_mx_edi_status_change_date_supplier': False,
            })
        return super().write(vals)

    @api.constrains('l10n_mx_edi_cfdi_uuid_supplier')
    def _constrains_l10n_mx_edi_cfdi_uuid_supplier(self):
        """
        Validaciones asociadas al cfdi de las facturas de proveedor
        """

        for move in self:
            # Si es una factura de proveedor, no tiene un cfdi asociado
            #  y está establecido el l10n_mx_edi_cfdi_uuid_supplier
            if move.l10n_mx_edi_cfdi_uuid_supplier and not move._get_l10n_mx_edi_signed_edi_document() and move.move_type == 'in_invoice':
                self.check_l10n_mx_edi_cfdi_uuid()

                def on_error(ex):
                    raise ValidationError(
                        _("Failure during update of the SAT status: %(msg)s") % {
                            "msg": str(ex)
                        }
                    )
                status = move.get_l10n_mx_edi_uuid_sat_status(on_error)
                if status != 'Vigente':
                    raise ValidationError(
                        _('Invoice SAT status is: "%(msg)s"') % {
                            "msg": status
                        }
                    )
                move.write({
                    'l10n_mx_edi_cfdi_uuid': move.l10n_mx_edi_cfdi_uuid_supplier
                })

    def _post(self, soft=True):
        self._constrains_l10n_mx_edi_cfdi_uuid_supplier()
        return super()._post(soft)

    def _compute_cfdi_values(self):
        res = super()._compute_cfdi_values()
        for move in self:
            if not move._get_l10n_mx_edi_signed_edi_document() and move.move_type == 'in_invoice' and move.l10n_mx_edi_cfdi_uuid_supplier:
                move.l10n_mx_edi_cfdi_supplier_rfc = move.partner_id.vat
                move.l10n_mx_edi_cfdi_customer_rfc = self.env.company.vat
                move.l10n_mx_edi_cfdi_amount = move.amount_total
        return res

    @api.depends('edi_document_ids')
    def _compute_has_cfdi(self):
        for move in self:
            move.has_cfdi = len(
                move._get_l10n_mx_edi_signed_edi_document()) > 0

    def action_update_vendor_sat_status(self):
        self.ensure_one()
        self.l10n_mx_edi_update_vendor_sat_status()

    def l10n_mx_edi_update_vendor_sat_status_notified(self):
        """
        Método auxiliar para ejecutar el que actualiza el estado del SAT
        pasando los usurios configurados a los que se debe notificar
        """
        users_to_notify = self.env.company.vendor_bills_status_notification_user_ids
        if not users_to_notify:
            users_to_notify = self.env.ref('base.user_admin')
        self.l10n_mx_edi_update_vendor_sat_status(
            users_to_notify=users_to_notify)

    def l10n_mx_edi_update_vendor_sat_status(self, users_to_notify=None):
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
                    self.env['account.move']._fields['l10n_mx_edi_sat_status']._description_selection(self.with_context(lang=self.env.user.lang).env))
                if new_status != old_status:
                    move.l10n_mx_edi_sat_status = new_status
                    move.l10n_mx_edi_status_change_date_supplier = fields.Date.today()

                    if old_status == 'undefined' and new_status == 'valid':
                        # Si el estdo aún no se ha verificado y al
                        # hacerlo resulta que este es válido no notificar
                        continue
                    elif users_to_notify:

                        for user in users_to_notify:
                            move.activity_schedule(
                                'mail.mail_activity_data_todo',
                                fields.Date.today(),
                                note=_('Status for this invoice change in SAT from "%s" to "%s"') % (
                                    _(description_selection_dict[old_status]),
                                    _(description_selection_dict[new_status])
                                ),
                                user_id=user.id)
                elif not users_to_notify:
                    # Si no se definen los usuarios a notificar no se está haciendo desde el cron
                    move.message_post(
                        body=_(
                            'Update of the SAT status has no changes: "%(msg)s"') % {
                            "msg": description_selection_dict[new_status]

                        }
                    )

    @api.model
    def _l10n_mx_edi_cron_update_vendor_sat_status(self):
        '''
        Validar que los uuids de las facturas de proveedores con válidos.
        TODO: la validación se va a hacer para todas las facturas de proveedores
        que tienen el uuid establecido el el caso de muchas facturas esto puede afectar
        el rendimiento, buscar alguna forma de optimizarlo
        '''
        to_process = self.env['account.move'].search([
            ('l10n_mx_edi_cfdi_uuid_supplier', '!=', ''),
            ('move_type', '=', 'in_invoice')
        ])
        for move in to_process:
            move.l10n_mx_edi_update_vendor_sat_status_notified()

    def get_l10n_mx_edi_cfdi_supplier_rfc(self):
        return self.l10n_mx_edi_cfdi_supplier_rfc

    def get_l10n_mx_edi_cfdi_customer_rfc(self):
        return self.l10n_mx_edi_cfdi_customer_rfc

    def get_l10n_mx_edi_cfdi_amount(self):
        return float_repr(self.l10n_mx_edi_cfdi_amount,
                          precision_digits=self.currency_id.decimal_places)

    def get_l10n_mx_edi_cfdi_uuid(self):
        if self.move_type == 'in_invoice' and not self.has_cfdi:
            return self.l10n_mx_edi_cfdi_uuid_supplier
        return self.l10n_mx_edi_cfdi_uuid

    def get_l10n_mx_edi_cfdi_unique_uuid_domain(self):
        return [('move_type', '=', 'in_invoice'), ('id', '!=', self.id), ('l10n_mx_edi_cfdi_uuid_supplier', '=', self.l10n_mx_edi_cfdi_uuid_supplier)]
