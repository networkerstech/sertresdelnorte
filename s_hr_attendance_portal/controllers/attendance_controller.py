# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


from odoo.addons.account.controllers.portal import CustomerPortal


class AttendanceController(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        """
        Se establece attendance_count = '' para que exista el valor
        y poder asignar el data al menú mediante:
            <t t-set="placeholder_count" t-value="'attendance_count'" />
        y que _getCountersAlwaysDisplayed encuentre el elemento en el
        DOM y que siempre se muestre aun cuando el contador no esté visible

        Args:
            counters (dict): Contadores para los elementos de menús

        """
        values = super()._prepare_home_portal_values(counters)
        values['attendance_count'] = ''
        return values

    @http.route(['/attendance/register'], type='http', auth="user", website=True)
    def attendance_register(self, **kw):
        """
        Muestra la página con el widget para el registro de asistencia desde el portal
        """
        employee = request.env['hr.employee'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        return request.render("s_hr_attendance_portal.portal_attendance_register", {
            'page_name': 'register_attendance',
            'employee': employee
        })
