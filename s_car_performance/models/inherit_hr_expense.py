# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    def action_sheet_move_create(self):
        """
        Crear odómetro cuando se contabiliza el gasto

        """
        res = super().action_sheet_move_create()
        odometer_vals_list = []
        for sheet in self:
            for expense in sheet.expense_line_ids:
                if expense.vehicle_id and expense.odometer:
                    if (expense.odometer - expense.vehicle_id.odometer) < 0:
                        raise UserError(
                            _('The odometer value is minor than the last vehicule odometer.'))
                    if expense.loaded_liters:
                        performance = (
                            expense.odometer - expense.vehicle_id.odometer) / expense.loaded_liters
                    odometer_vals_list.append({
                        'date': expense.date,
                        'value': expense.odometer,
                        'vehicle_id': expense.vehicle_id.id,
                        'driver_id': expense.vehicle_id.driver_id.id,
                        'performance': performance
                    })
        if odometer_vals_list:
            self.env['fleet.vehicle.odometer'].sudo().create(
                odometer_vals_list
            )
        return res
