from odoo import fields, models, api, _, registry
from odoo.tools import float_repr
import threading
from odoo.api import Environment
import odoo


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_mx_edi_vendor_cfdi_uuid = fields.Char(
        string='Providers Fiscal Folio',
        copy=False,
        default='',
        help='Folio in electronic invoice, is returned by SAT when send to stamp.',
    )
    l10n_mx_edi_vendor_status_change_date = fields.Date(
        'Status change date'
    )
    l10n_mx_edi_vendor_sat_status = fields.Selection(
        selection=[
            ('none', "State not defined"),
            ('undefined', "Not Synced Yet"),
            ('not_found', "Not Found"),
            ('cancelled', "Cancelled"),
            ('valid', "Valid"),
        ],
        string="SAT status",
        readonly=True,
        copy=False,
        required=True,
        tracking=True,
        default='undefined',
        help="Refers to the status of the journal entry inside the SAT system.")

    @api.model_create_multi
    def create(self, vals_list):
        """
        Si se establece el uuid el estado SAT en no definido
        hasta tanto no se verifique contra el SAT
        """
        for vals in vals_list:
            if 'l10n_mx_edi_vendor_cfdi_uuid' in vals and vals.get('l10n_mx_edi_vendor_cfdi_uuid', False):
                vals.update({
                    'l10n_mx_edi_vendor_sat_status': 'undefined',
                    'l10n_mx_edi_vendor_status_change_date': False,
                })
        return super().create(vals)

    def write(self, vals):
        """
        Si se establece el uuid el estado SAT en no definido
        hasta tanto no se verifique contra el SAT
        """
        if 'l10n_mx_edi_vendor_cfdi_uuid' in vals and vals.get('l10n_mx_edi_vendor_cfdi_uuid', False):
            vals.update({
                'l10n_mx_edi_vendor_sat_status': 'undefined',
                'l10n_mx_edi_vendor_status_change_date': False,
            })
        return super().write(vals)

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
            supplier_rfc = move.l10n_mx_edi_cfdi_supplier_rfc
            customer_rfc = move.l10n_mx_edi_cfdi_customer_rfc
            total = float_repr(move.l10n_mx_edi_cfdi_amount,
                               precision_digits=move.currency_id.decimal_places)
            uuid = move.l10n_mx_edi_cfdi_uuid

            try:
                status = self.env['account.edi.format']._l10n_mx_edi_get_sat_status(
                    supplier_rfc, customer_rfc, total, uuid)
            except Exception as e:
                move.message_post(
                    body=_("Failure during update of the SAT status: %(msg)s", msg=str(e)))
                continue

            new_status = ''
            if status == 'Vigente':
                new_status = 'valid'
            elif status == 'Cancelado':
                new_status = 'cancelled'
            elif status == 'No Encontrado':
                new_status = 'not_found'
            else:
                new_status = 'none'

            old_status = move.l10n_mx_edi_vendor_sat_status
            if new_status != old_status:
                move.l10n_mx_edi_vendor_sat_status = new_status
                move.l10n_mx_edi_vendor_status_change_date = fields.Date.today()

                if old_status == 'undefined' and new_status == 'valid':
                    # Si el estdo aún no se ha verificado y al
                    # hacerlo resulta que este es válido no notificar
                    continue
                elif users_to_notify:
                    description_selection_dict = dict(
                        self.env['account.move']._fields['l10n_mx_edi_vendor_sat_status']._description_selection(self.with_context(lang=self.env.user.lang).env))
                    for user in users_to_notify:
                        move.activity_schedule(
                            'mail.mail_activity_data_todo',
                            fields.Date.today(),
                            note=_('Status for this invoice change in SAT from "%s" to "%s"') % (
                                _(description_selection_dict[old_status]),
                                _(description_selection_dict[new_status])
                            ),
                            user_id=user.id)

    @ api.model
    def _l10n_mx_edi_cron_update_vendor_sat_status(self):
        '''
        Validar que los uuids de las facturas de proveedores con válidos.
        TODO: la validación se va a hacer para todas las facturas de proveedores
        que tienen el uuid establecido el el caso de muchas facturas esto puede afectar
        el rendimiento, buscar alguna forma de optimizarlo
        '''
        to_process = self.env['account.move'].search([
            ('l10n_mx_edi_vendor_cfdi_uuid', '!=', ''),
            ('move_type', '=', 'in_invoice')
        ])
        for move in to_process:
            move.l10n_mx_edi_update_vendor_sat_status_notified()
