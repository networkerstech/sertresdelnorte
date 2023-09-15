# -*- coding: utf-8 -*-

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    def portal_attendance_action(self):
        """
        Se llama el método original de hr.employee ¨_attendance_action¨

        Raises:
            ValidationError: Si el usuario no tiene asociado un empleado

        Returns:
            action_dict: self.employee_id._attendance_action(False)
        """
        employee = self.sudo().employee_id
        if employee:
            return employee._attendance_action(False)['action']
        raise ValidationError(_('User has no employee.'))

    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     res = super().name_search(name, args, operator, limit)
    #     return res


class PortalWizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'

    def _create_user(self):
        """
        Si se está dando acceso al portal a un contacto que posee empleado
        vincular este empleado al usuario que se está creando, si no se hace
        esto no se pueden registrar las asistencias desde el portal y al crear
        el empleado para el usuario se crea uno nuevo que no se corresponde
        con el empleado original
        """
        res = super()._create_user()
        contact_employee = self.env['hr.employee'].search(
            [('work_contact_id', '=', self.partner_id.id)])
        if contact_employee:
            contact_employee.user_id = res.id
        return res
