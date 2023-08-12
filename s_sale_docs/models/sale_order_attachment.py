# -*- coding: utf-8 -*-

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderAttachment(models.Model):
    _name = 'sale.order.attachment'
    _description = 'Sale Order Attachment'
    _rec_name = 'attachment_file_name'
    _order = 'attachment_required desc'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=False,
        ondelete='cascade'
    )
    name = fields.Char(compute='_compute_name', string='Name')
    attachment_required = fields.Boolean('Required')
    attachment_required_str = fields.Char(
        compute='_compute_attachment_required_str',
        string='Attachment required string'
    )
    attachment_file = fields.Binary(
        'Attachment file',
        attachment=True
    )
    attachment_file_name = fields.Char('Filename')
    document_type_id = fields.Many2one(
        'sale.project.attachment.type',
        'Type',
        required=True,
        ondelete='restrict'
    )

    @api.depends('attachment_required')
    def _compute_attachment_required_str(self):
        for rec in self:
            rec.attachment_required_str = "*" if rec.attachment_required else ""

    @api.depends('attachment_file_name', 'document_type_id')
    def _compute_name(self):
        for rec in self:
            rec.name = "% : %" % (
                rec.document_type_id.document_name, rec.attachment_file_name)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Modificar el adjunto del campo para establecer el nombre y tipo mime
        y así poder adjuntarlo a la orden
        """
        res = super().create(vals_list)
        i = 0
        for rec in res:
            rec.manage_attachment(vals_list[i])
            i += 1
        return res

    def write(self, vals):
        """
        Modificar el adjunto del campo para establecer el nombre y tipo mime
        y así poder adjuntarlo a la orden
        """
        res = super().write(vals)
        for rec in self:
            if vals.get('attachment_file', False):
                self.manage_attachment(vals)
        return res

    def manage_attachment(self, vals):
        """
        Modificar el adjunto del campo para establecer el nombre y tipo mime
        y así poder adjuntarlo a la orden
        """
        if vals.get('attachment_file', False):
            attachment_file_name = vals.get(
                'attachment_file_name', self.attachment_file_name)
            if not attachment_file_name:
                # Puede darse el caso de que se actualice el documento
                # con una versión mas reciente y como el nombre no cambia no viene el vals
                raise ValidationError(
                    _("You must provide file name for attachment."))
            mimetype = self.env['ir.attachment']._compute_mimetype({
                'name': attachment_file_name
            })
            attachment = self.env['ir.attachment'].search([
                ('res_model', '=', self._name),
                ('res_field', '=', 'attachment_file'),
                ('res_id', '=', self.id),
            ])
            if attachment:
                updates = {
                    'mimetype': mimetype
                }
                if attachment_file_name:
                    updates.update({'name': attachment_file_name})
                attachment.write(updates)

                attachment_for_sale = attachment.copy({
                    'res_model': 'sale.order',
                    'res_id': self.sale_order_id.id,
                })
                self.sale_order_id.with_context({'mail_create_nosubscribe': True}).message_post(**{
                    'attachment_ids': [attachment_for_sale.id],
                    'body': '',
                    'message_type': 'comment',
                    'partner_ids': [],
                    'subtype_xmlid': 'mail.mt_note'
                })
