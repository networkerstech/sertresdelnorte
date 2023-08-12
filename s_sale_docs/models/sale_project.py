# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleProjectDocumentType(models.Model):
    _name = 'sale.project.attachment.type'
    _description = 'Attachment type'

    name = fields.Char(
        compute='_compute_name',
        string='Name',
        store=False
    )
    document_name = fields.Char('Name', required=True)
    document_type = fields.Char('Type (extension)', required=True)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """
        Cuando se busque por el nombre, buscar en los elementos que lo componen
        para que el campo siempre se calcule y salga en el idioma del usuario
        evitando la traducción del campo por el usuario
        """
        new_args = []
        for arg in args:
            if len(arg) and arg[0] == 'name':
                new_args.append('|')
                new_args.append(('document_name', arg[1], arg[2]))
                new_args.append(('document_type', arg[1], arg[2]))
            else:
                new_args.append(arg)
        return super()._search(new_args, offset, limit, order, count, access_rights_uid)

    @api.depends('document_name', 'document_type')
    def _compute_name(self):
        """
        Calcular el nombre del tipo de adjunto en el formato:
        "Planos (archivo .dwg)"
        """
        for rec in self:
            doc_type = rec.document_type
            if not doc_type.startswith('.'):
                doc_type = '.' + doc_type
            rec.name = _("%(name)s (archive %(extension)s)") % {
                'name': rec.document_name,
                'extension': doc_type
            }


class SaleOrderAttachmentConfig(models.Model):
    _name = 'sale.project.attachment.config'
    _description = 'Configuration for Types of Sales Order Attachment'
    _rec_name = 'document_type_id'
    _order = 'attachment_required desc'

    _sql_constraints = [
        (
            'unique_attachment_type_by_project_type',
            'UNIQUE(project_type_id, document_type_id)',
            'Attachment type can not be repeated by project type',
        ),
    ]

    project_type_id = fields.Many2one(
        'sale.project.type',
        required=True,
        ondelete='restrict'
    )
    document_type_id = fields.Many2one(
        'sale.project.attachment.type',
        'Type',
        required=True,
        ondelete='restrict'
    )
    attachment_required = fields.Boolean(
        'Required',
        default=True
    )


class ProjectType(models.Model):
    _name = 'sale.project.type'
    _description = 'Type of Sales Project'

    name = fields.Char('Name')
    attachment_config_ids = fields.One2many(
        'sale.project.attachment.config',
        'project_type_id',
        string='Attachments documents',
        help='Configuration for documents that will be attachet to a sale orders of this type'
    )
