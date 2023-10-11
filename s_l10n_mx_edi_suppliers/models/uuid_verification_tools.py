from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_repr
import re
import logging

_logger = logging.getLogger(__name__)


class UIIDVerificationMixin(models.AbstractModel):
    _name = 'l10n.mx.edi.uuid.verification.tools'
    _description = 'UUID verification mixin'

    def check_l10n_mx_edi_cfdi_uuid(self):
        """
        Validaciones locales asociadas al cfdi es necesario adicionar el constrains en los modelos que heredan de este
        """
        for rec in self:
            # Si es una factura de proveedor, no tiene un cfdi asociado
            #  y está establecido el l10n_mx_edi_cfdi_uuid_supplier
            rec_uuid = rec.get_l10n_mx_edi_cfdi_uuid()
            if rec_uuid:
                # El uuid solo debe contener números del 0-9 y letas mayúsculas
                # de la A-F en el formato "12A3BCD-4EFA-56B7-C891-23D4E56F7ABC"
                regex = r"^[ABCDEF0-9]{7}[-]{1}([ABCDEF0-9]{4}[-]{1}){3}[ABCDEF0-9]{12}$"
                if not re.match(regex, rec_uuid):
                    raise ValidationError(
                        _('Invoice UUID structure is invalid, must contain uppercase letters A through F and numbers 0 through 9 in the format "12A3BCD-4EFA-56B7-C891-23D4E56F7ABC"')
                    )

                # Validar que el cfdi no esté asociado a otro registro
                unique_uuid_domain = rec.get_l10n_mx_edi_cfdi_unique_uuid_domain()
                if self.search_count(unique_uuid_domain):
                    raise ValidationError(_("Invoice UUID already registered"))

    # Métodos auxiliares, para un solo registro

    def get_l10n_mx_edi_uuid_sat_status(self, on_get_sat_status_error=None):
        """
        Obtener el estado de un registro en el sat
        """
        self.ensure_one()
        supplier_rfc = self.get_l10n_mx_edi_cfdi_supplier_rfc()
        customer_rfc = self.get_l10n_mx_edi_cfdi_customer_rfc()
        total = self.get_l10n_mx_edi_cfdi_amount()
        uuid = self.get_l10n_mx_edi_cfdi_uuid()

        try:
            status = self.env['account.edi.format']._l10n_mx_edi_get_sat_status(
                supplier_rfc, customer_rfc, total, uuid)
        except Exception as e:
            if on_get_sat_status_error:
                on_get_sat_status_error(e)
            else:
                _logger.error(_("Failure during update of the SAT status: %(msg)s") % {
                    "msg": str(e)
                })

            return None
        return status

    def get_l10n_mx_edi_status_from_sat_status(self, sat_status):
        """
        Obtener l10n_mx_edi_status a partir del estado del SAT
        """
        sat_l10n_mx_edi_status_dict = {
            'Vigente': 'valid',
            'Cancelado': 'cancelled',
            'No Encontrado': 'not_found'
        }
        if sat_status in sat_l10n_mx_edi_status_dict:
            return sat_l10n_mx_edi_status_dict[sat_status]
        return 'none'

    def get_l10n_mx_edi_cfdi_supplier_rfc(self):
        # To override
        pass

    def get_l10n_mx_edi_cfdi_customer_rfc(self):
        # To override
        pass

    def get_l10n_mx_edi_cfdi_amount(self):
        # To override
        pass

    def get_l10n_mx_edi_cfdi_uuid(self):
        # To override
        pass

    def get_l10n_mx_edi_cfdi_unique_uuid_domain(self):
        # To override
        pass
