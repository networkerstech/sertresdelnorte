# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command, _
from odoo.exceptions import ValidationError
from odoo.addons.sale.models.sale_order import READONLY_FIELD_STATES


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_type_id = fields.Many2one(
        'sale.project.type',
        string='Project Type',
        ondelete='restrict',
        states=READONLY_FIELD_STATES
    )

    project_attachment_ids = fields.One2many(
        'sale.order.attachment',
        'sale_order_id',
        string='Attachments',
        states=READONLY_FIELD_STATES
    )

    @api.onchange('project_type_id')
    def _onchange_project_type_id(self):
        """
        Establecer los adjuntos del tipo de proyecto cuando este cambie
        """
        self.ensure_one()
        self.project_attachment_ids = [Command.clear()]
        att_commands = []
        for attachment_config in self.project_type_id.attachment_config_ids:
            att_commands.append(Command.create({
                'document_type_id': attachment_config.document_type_id.id,
                'attachment_required': attachment_config.attachment_required
            }))
        if att_commands:
            self.project_attachment_ids = att_commands

    def action_confirm(self):
        """
        Si existen adjuntos requeridos vacios no se puede confirmar la orden
        """
        if self.project_type_id:
            empty_required_attachments = self.project_attachment_ids.filtered(
                lambda x: x.attachment_required and not x.attachment_file)
            if empty_required_attachments:
                if len(empty_required_attachments) > 1:
                    error_msg = _("Attachments %s are required") % ','.join(
                        [att.document_type_id.name for att in empty_required_attachments]
                    )
                else:
                    error_msg = _(
                        "Attachment %s is required") % empty_required_attachments[0].document_type_id.name
                raise ValidationError(error_msg)
        return super().action_confirm()
