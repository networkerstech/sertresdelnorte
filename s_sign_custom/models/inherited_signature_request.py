import logging
import base64

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class SignatureRequest(models.Model):
    _inherit = 'sign.request'

    res_id = fields.Integer('Current object ID', help='This field is used to update object attachment')

    @api.model
    def write(self, vals):
        record = super(SignatureRequest, self).write(vals)
        if 'state' in vals and self.state == 'signed':
            if self.template_id.template_id:
                self.write_or_create_model_attachment()
        return record

    def write_or_create_model_attachment(self):
        """
        This write or create object signer to attach a copy of signed document
        :return: {
            sender_obj_id: Associated object that send sign request.
            attachment_id: Signed document attachment.
        }
        """
        self.ensure_one()
        if not self.completed_document:
            self._generate_completed_document()
        config_id = self.template_id.template_id
        _logger.info("Looking for signer.")
        signer = self.env[config_id.model_name].search([('id', '=', self.res_id)])
        result = {}
        if signer:
            result.update({'sender_obj_id': signer.id})
            _logger.info("%s: Signer found!")
            attach_obj = self.env['ir.attachment']
            report_name_wo_ext = self.reference
            if report_name_wo_ext.endswith('.pdf'):
                report_name_wo_ext = report_name_wo_ext[0:-4]
            report_name_wo_ext = _('%s_Signed') % report_name_wo_ext
            report_name = '%s.pdf' % report_name_wo_ext
            attach_id = attach_obj.search([
                ('res_model', '=', config_id.model_name),
                ('res_id', '=', signer.id),
                ('name', '=', report_name)
            ])
            if attach_id:
                attach_obj.write({
                    'datas': self.completed_document,  # base64 string
                })
                _logger.info(
                    "%s: attachment successfully updated." % attach_id)
            else:
                attach_id = attach_obj.create({
                    'name': report_name,  # filename
                    'datas': self.completed_document,  # base64 string
                    'res_model': config_id.model_name,
                    'res_id': signer.id,
                })
                _logger.info("%s: attachment successfully created." %
                             attach_id.name)
            result.update({'attachment_id': attach_id.id})
        else:
            _logger.warning("Signer not found!")
            result.update({'sender_obj_id': False})
        return result

