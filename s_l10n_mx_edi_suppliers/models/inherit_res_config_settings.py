from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    vendor_bills_status_notification_user_ids = fields.Many2many(
        'res.users',
        'res_company_vendor_bills_status_user_rel',
        'company_id',
        'user_id',
        string='Users to notify',
        help='Users to notify when the status of supplier invoices changes in the SAT'
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vendor_bills_status_notification_user_ids = fields.Many2many(
        related='company_id.vendor_bills_status_notification_user_ids',
        readonly=False
    )

    @api.constrains('vendor_bills_status_notification_user_ids')
    def _contrains_vendor_bills_notification_users(self):
        """
        Cuando se modifican los usuarios a ser notificados desde
        la configuración de contabilidad validar que sean 2 o mas.
        """
        if self.env.context.get('module', '') == 'account' and self.vendor_bills_status_notification_user_ids:
            if len(self.vendor_bills_status_notification_user_ids) < 2:
                raise ValidationError(
                    _('You must specify at least 2 users to notify when vendors bill state change')
                )
