import logging
import base64
from odoo import api, fields, models, SUPERUSER_ID, _, Command
from odoo.exceptions import ValidationError
from collections import defaultdict

_logger = logging.getLogger(__name__)


class SignItem(models.Model):
    _inherit = 'sign.item'

    item_config_id = fields.Many2one('sign.item', "Config Item",
                                     help='Used by s_sign_custom registry module. Fix object repetition and cloning bug')


class SignTemplate(models.Model):
    _name = 'sign.template'
    _inherit = ['sign.template', 'mail.thread']
    _order = 'use_config'

    def _domain_model_ids(self):
        report_models = self.env['ir.actions.report'].search(
            []).mapped('model')
        return [('model', 'in', report_models)]

    use_config = fields.Boolean('Dynamic configuration')
    template_type = fields.Selection(
        [('document', 'Document'),
         ('report', 'Report')],
        'Template Type', default='report')
    template_id = fields.Many2one('sign.template', string="Template Configuration",
                                  help='Used by w_sing_custom registry module. Fix object repetition and cloning bug')
    res_id = fields.Integer(
        'Current object ID', help='This field is used to update object attachment')
    model_id = fields.Many2one(
        'ir.model', string="Report Model", domain=_domain_model_ids)
    model_name = fields.Char(related='model_id.model')
    action_server_id = fields.Many2one('ir.actions.server', "Action Report")
    report_id = fields.Many2one('ir.actions.report', "Report")
    # Sign Messaging
    use_messaging = fields.Boolean("Use Messaging", default=True)
    message_subject = fields.Char("Subject", translate=True,
                                  default=_('@ReportName was sent'))
    message_body = fields.Text("Message", translate=True,
                               default=_("Please @PartnerName go to the link to sign the document."))
    # Configure partner field by role
    role_config_ids = fields.One2many(
        'sign.template.role.config',
        'sign_template_id',
        string='Signers',
        compute='_compute_role_config_ids',
        store=True,
        readonly=False,
        help='Select the field that refers to the contact who will sign the report.\n Select the "ID" field to indicate that the person who will sign the document is the record contact.',
        copy=True
    )

    @api.depends('use_config', 'sign_item_ids.responsible_id')
    def _compute_role_config_ids(self):
        """Genera la configuración de los firmantes en dependencia de
        los roles que tengan los campos de firma, una configuración por cada rol
        """
        for rec in self:
            if rec.use_config:
                configured_roles = [
                    role_conf.role_id.id for role_conf in rec.role_config_ids]
                checked_role_ids = []
                sequence = 0
                for sign_item in rec.sign_item_ids:
                    if sign_item.responsible_id.id not in checked_role_ids:
                        checked_role_ids.append(sign_item.responsible_id.id)
                        if sign_item.responsible_id.id not in configured_roles:
                            sequence += 1
                            self.env['sign.template.role.config'].create({
                                'sequence': sequence,
                                'sign_template_id': rec.id,
                                'role_id': sign_item.responsible_id.id
                            })

                for role_conf in rec.role_config_ids:
                    if role_conf.role_id.id not in checked_role_ids:
                        role_conf.unlink()
            else:
                rec.role_config_ids.unlink()

    # Inherit Helper
    request_count = fields.Integer(
        'Request Count', compute='_compute_request_count')

    def _compute_request_count(self):
        for i in self:
            i.request_count = len(i.sign_request_ids)

    @ api.constrains('model_id', 'report_id', 'template_type', 'use_config')
    def _constrains_all(self):
        for rec in self.filtered(lambda s: s.use_config):
            if rec.template_type == 'report':
                if self.search([('model_id', '=', rec.model_id.id),
                                ('template_type', '=', 'report'),
                                ('report_id', '=', rec.report_id.id),
                                ('id', '!=', rec.id)]):
                    raise ValidationError(
                        _("This report is already configured for this model (%s)! Please choose another one.") % rec.model_id.model)

            field_ids = []

        return True

    def get_signers_dict(self, obj):
        """Obtiene los partner firmantes a partir a partir de un objetpo a través de:
        - el valor de los campos si el campo es distinto del 'id' y el tipo del campo es ['res.partner', 'res.users', 'hr.employee']
        - o el objeto en si mismo, que debe ser de tipo ['res.partner', 'res.users', 'hr.employee']

        * si el campo es el id quiere decir que el partner asociado al registro es firmante del documento

        Args:
            obj (): Record a partir del cual se van a obtemer los partners firmantes

        Raises:
            ValidationError: Si se pasa un record vacío

        Returns:
            dict (res.partner): Un diccionario de los partners firmantes del documento en el
            formato {'role_id': res.partner } que indica a que partner corresponde cada rol
        """
        if obj:
            result = defaultdict(lambda: self.env['res.partner'])
            for signer in self.role_config_ids:
                if not signer.field_id:
                    raise ValidationError(
                        _('You must configure the signer for role "%(role)s" of document "%(template)s"') % {
                            'role': signer.role_id.name,
                            'template': signer.sign_template_id.name
                        })
                if signer.field_id.name != 'id':
                    # Obtener el partner a través del valor del campo de tipo ['res.partner', 'res.users', 'hr.employee']
                    if hasattr(obj, signer.field_id.name) and getattr(obj, signer.field_id.name):
                        result[signer.role_id.id] += self.get_signer_field_value(
                            getattr(obj, signer.field_id.name))
                elif getattr(obj, '_name') in ['res.partner', 'res.users', 'hr.employee']:
                    # Obtener el partner a través del objeto en si que debe ser de tipo ['res.partner', 'res.users', 'hr.employee']
                    result[signer.role_id.id] += self.get_signer_field_value(
                        obj)
            return result
        else:
            raise ValidationError(_('Invalid Report Item'))

    @ api.onchange('model_id')
    def _onchange_model_id(self):
        self.report_id = False

        # Si cambia el modelo volver a generar la configuración de la firma
        self.role_config_ids = False
        self._compute_role_config_ids()

    @ api.onchange('report_id', 'name', 'model_id')
    def _onchange_report_id(self):
        if self.use_config and self.model_id:
            if self.action_server_id:
                super_record = self.with_user(SUPERUSER_ID)
                if super_record.action_server_id.binding_model_id:
                    super_record.action_server_id.unlink_action()
                super_record.action_server_id.name = '%s (%s)' % (
                    self.name, _('Sign'))
                super_record.action_server_id.model_id = self.model_id
                if self.active:
                    super_record.action_server_id.create_action_report()

    def toggle_active(self):
        for rec in self:
            rec.active = not rec.active
            super_rec = rec.with_user(SUPERUSER_ID)
            if rec.active:
                super_rec.action_server_id.create_action_report()
            else:
                super_rec.action_server_id.unlink_action()

    def sign_report_function(self, record_ids, ctx={}):
        """

        :param record_ids: Selected records in tree or form view by user
        :param ctx: Context utilities used
        :return: {
            (........context values.......)
            sign_request_id: created or updated sign request object
        }
        """
        if not ctx:
            ctx = self.env.context
        ctx = dict(ctx)
        template_config_id = self.search(
            [('id', '=', ctx.get('config_id', 0))])
        if not template_config_id:
            raise ValidationError(
                _("The sign configuration not exist. Contact to Administrator or create one for this report"))
        elif not template_config_id.use_config:
            raise ValidationError(
                _("The sign configuration is disabled. Contact to Administrator or enable USE DYNAMIC CONFIGURATION in the Sign Template"))
        ir_attachment_obj = self.env['ir.attachment']
        sign_request_obj = self.env['sign.request']
        sign_template_obj = self.env['sign.template']

        all_signers = self.env['res.partner']
        for rec in record_ids:
            report_name_wo_ext = template_config_id.name
            rec_name = getattr(rec, 'display_name') if hasattr(
                rec, 'display_name') else ''
            if rec_name:
                report_name_wo_ext = '%s_%s' % (report_name_wo_ext, rec_name)
            report_name_wo_ext = report_name_wo_ext.replace(
                ' ', '_').replace('.pdf', '')
            report_attachment = ir_attachment_obj.search([
                ('res_model', '=', template_config_id.model_id.model),
                ('res_id', '=', rec.id),
                ('name', '=', '%s.pdf' % report_name_wo_ext)
            ])

            _logger.info(
                _("Search current sign template for existing attachment ..."))
            sign_template_id = template_config_id.search([
                ('template_id', '=', template_config_id.id),
                ('res_id', '=', rec.id)])

            _logger.info(_("Starting sign request build ..."))
            _logger.info(_("Creating report attachment ..."))
            if template_config_id.template_type == 'report':
                report_data = self.env['ir.actions.report']._render(
                    template_config_id.report_id, [rec.id])
                report_data = base64.encodebytes(report_data[0])
            else:
                report_data = template_config_id.datas

            _logger.info(_("Creating or writing report attachment ..."))

            if report_attachment:
                report_attachment.write({'datas': report_data})
                _logger.info(_("Successfully report attachment wrote ..."))
            else:
                report_attachment = ir_attachment_obj.create({
                    'datas': report_data,
                    'name': '%s.pdf' % report_name_wo_ext,
                    'res_model': template_config_id.model_id.model,
                    'res_id': rec.id,
                })
                _logger.info(_("Successfully report attachment created ..."))

            _logger.info(
                _("Creating or updating template for signature request ..."))
            if sign_template_id:
                sign_template_id.write({
                    'attachment_id': report_attachment.id,
                    'tag_ids': [(6, 0, template_config_id.tag_ids.ids)],
                    'redirect_url': template_config_id.redirect_url,
                    'redirect_url_text': template_config_id.redirect_url_text,
                    'favorited_ids': [(6, 0, template_config_id.favorited_ids.ids)],
                })
                _logger.info(_("Successfully template updated ..."))
            else:
                sign_template_id = sign_template_obj.create({
                    'template_id': template_config_id.id,
                    'res_id': rec.id,
                    'attachment_id': report_attachment.id,
                    'tag_ids': [(6, 0, template_config_id.tag_ids.ids)],
                    'redirect_url': template_config_id.redirect_url,
                    'redirect_url_text': template_config_id.redirect_url_text,
                    'favorited_ids': [(6, 0, template_config_id.favorited_ids.ids)],
                })
                _logger.info(_("Successfully template created ..."))

            _logger.info(
                _("Creating or updating the signature itself with selected parameters"))
            signers_dict = template_config_id.get_signers_dict(rec)
            signer_list = []
            sent_order = 0
            for sign_role_id in signers_dict:
                sent_order += 1
                signer_list.append({
                    'partner_id': signers_dict[sign_role_id][0].id,
                    'role_id': sign_role_id,
                    'mail_sent_order': sent_order
                })

            for sign_config_item in template_config_id.sign_item_ids:
                to_write_sign_item = sign_template_id.sign_item_ids.filtered(
                    lambda s: s.item_config_id == sign_config_item)

                if to_write_sign_item:
                    to_write_sign_item.sudo().write({
                        'template_id': sign_template_id.id,
                        'name': sign_config_item.name,
                        'required': sign_config_item.required,
                        'responsible_id': sign_config_item.responsible_id.id,
                        'type_id': sign_config_item.type_id.id,
                        'page': sign_config_item.page,
                        'height': sign_config_item.height,
                        'width': sign_config_item.width,
                        'posX': sign_config_item.posX,
                        'posY': sign_config_item.posY
                    })
                    _logger.info(_("Successfully signature updated ..."))
                else:
                    self.env['sign.item'].sudo().create({
                        'item_config_id': sign_config_item.id,
                        'template_id': sign_template_id.id,
                        'name': sign_config_item.name,
                        'required': sign_config_item.required,
                        'responsible_id': sign_config_item.responsible_id.id,
                        'type_id': sign_config_item.type_id.id,
                        'page': sign_config_item.page,
                        'height': sign_config_item.height,
                        'width': sign_config_item.width,
                        'posX': sign_config_item.posX,
                        'posY': sign_config_item.posY
                    })
                    _logger.info(_("Successfully signature created ..."))

            _logger.info(_("Creating signature request ..."))
            messaging = template_config_id.get_message_data(
                rec, signers_dict.values())

            sign_request = sign_request_obj.sudo().create({
                'template_id': sign_template_id.id,
                'request_item_ids': [Command.create(signer) for signer in signer_list],
                'reference': report_name_wo_ext,
                'subject': messaging.get('subject'),
                'message': messaging.get('message'),
                'attachment_ids': [Command.set([report_attachment.id])],
            })

            sign_request.sudo().res_id = rec.id
            ctx.update({'sign_request_id': sign_request.id})
            _logger.info(
                _("Successfully sign request build, sent it and waiting for signatures."))
            if template_config_id.use_messaging:
                template_config_id.message_post(body=_('%s: Signature request sent to %s.') % (report_name_wo_ext, self.get_signer_names(signers_dict.values())),
                                                message_type='comment', subtype_xmlid='mail.mt_comment')
            for signer in signers_dict.values():
                all_signers |= signer

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Signature request sent"),
                'message': _("Signature request sent to: %s") % self.get_signer_names(all_signers),
                'next': {
                    'type': 'ir.actions.act_window_close'
                },
            }
        }

    def get_message_data(self, record, partner_ids):
        unknown = _('<Unknown>')
        parameters = {
            '@PartnerName': self.get_signer_names(partner_ids),
            '@RecordName': record.name if hasattr(record, 'name') else unknown,
            '@ReportName': self.name or unknown,
        }
        subject = self.message_subject
        message = self.message_body
        for param in parameters:
            subject = subject.replace(param, parameters.get(param))
            message = message.replace(param, parameters.get(param))
        return {
            'subject': subject,
            'message': message,
        }

    # Utilities
    @ staticmethod
    def get_signer_names(partner_ids):
        """
        It return the partner names in string format
        :param partner_ids: partner list to get names
        :return: return names separated by , if has many or single name if is only one, otherwise return False
        """
        result = ', '.join([partner_id.name or _('<Unknown>')
                            for partner_id in partner_ids])
        return '(%s)' % result if len(partner_ids) > 1 else result

    def get_signer_field_value(self, record):
        """Toma un record de tipo ['res.partner', 'res.users', 'hr.employee'] y determina el firmante a partir de este

        Args:
            record (['res.partner', 'res.users', 'hr.employee']): Registro a patir del cual se va a determinar el partner firmante

        Returns:
            recordset (res.partner): Un recordset con un parter firmante o vacío
        """
        model_name = getattr(record, '_name')
        result = self.env['res.partner']
        if model_name == 'res.partner':
            result = record
        elif model_name == 'res.users' and record.partner_id:
            result = record.partner_id
        elif model_name == 'hr.employee':
            if record.user_id.partner_id:
                result += record.user_partner_id
            elif record.work_contact_id:
                result += record.work_contact_id
        return result

    def create_action_server(self):
        for record in self:
            sudo_record = record.with_user(SUPERUSER_ID)
            if sudo_record.active:
                if not record.action_server_id:
                    sudo_record.action_server_id = self.action_server_id.create({
                        'name': '%s (%s)' % (record.name, _('Sign')),
                        'model_id': record.model_id.id,
                        'state': 'code',
                        'code': "action = env['sign.template'].sign_report_function(records, ctx={'config_id': %d})" % record.id
                    })
                else:
                    sudo_record.action_server_id.write({
                        'name': '%s (%s)' % (record.name, _('Sign')),
                        'model_id': record.model_id.id,
                        'state': 'code',
                        'code': "action = env['sign.template'].sign_report_function(records, ctx={'config_id': %d})" % record.id
                    })
                sudo_record.action_server_id.create_action_report()
            elif sudo_record.action_server_id:
                sudo_record.action_server_id.unlink()

    def write(self, vals):
        sign_request_ids = vals.get('sign_request_ids', self.sign_request_ids)
        use_config = vals.get('use_config', self.use_config)
        if sign_request_ids and use_config:
            vals.update({'use_config': False})
        result = super(SignTemplate, self).write(vals)
        if use_config and 'action_server_id' not in vals or 'name' in vals:
            self.create_action_server()
        return result

    def unlink(self):
        for rec in self.with_user(SUPERUSER_ID).filtered(lambda c: c.action_server_id):
            rec.action_server_id.unlink()
        return super(SignTemplate, self).unlink()


class SignTemplateRoleConfig(models.Model):
    _name = 'sign.template.role.config'
    _description = 'Sign Template Role Config '
    _order = 'sequence'

    _sql_constraints = [
        ('role_partner_uniq', 'unique (sign_template_id,role_id)',
         'Signer role configuration must be unique by template')
    ]

    sign_template_id = fields.Many2one(
        'sign.template', string='Sign Template', ondelete='cascade')
    model_id = fields.Many2one(related='sign_template_id.model_id')
    model_name = fields.Char(related='sign_template_id.model_name')
    sequence = fields.Integer('Sequence')
    role_id = fields.Many2one(
        'sign.item.role',
        'Role',
        required=True
    )
    field_id = fields.Many2one(
        'ir.model.fields',
        string='Signer',
        help='Select the "ID" field to tell the registry contact to sign the document.'
    )
