# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    assign_date = fields.Date('Assignment Date')
    return_date = fields.Date('Return Date')
    state = fields.Selection([
        ('assigned', 'Assigned'),
        ('borrowed', 'Borrowed'),
        ('expire', 'Expired'),
    ], string='State')

    @api.model
    def update_tools_loan_state_cron(self):
        today = fields.Date.today()
        # borrowed tools
        to_borrowed = self.search([
            ('assign_date', '<=', today),
            ('return_date', '>=', today),
            ('state', '!=', 'borrowed'),
        ])
        if to_borrowed:
            to_borrowed.write({
                'state': 'borrowed'
            })

        # assigned tools
        to_assigned = self.search([
            ('assign_date', '<=', today),
            ('return_date', '=', False),
            ('state', '!=', 'assigned'),
        ])
        if to_assigned:
            to_assigned.write({
                'state': 'assigned'
            })

        # expire tools
        to_expire = self.search([
            ('return_date', '<', today),
            ('state', '!=', 'expire'),
        ])
        if to_expire:
            to_expire.write({
                'state': 'expire'
            })
            for te in to_expire:
                self.env['mail.activity'].create({
                    'res_model_id': self.env.ref('maintenance.model_maintenance_equipment').id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'res_id': te.id,
                    'summary': _('The delivery date of the equipment / tool expired'),
                    'date_deadline': today,
                    'user_id': te.create_uid.id,
                })

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val.update({
                'state': self.determine_state(val.get('assign_date', False), val.get('return_date', False))
            })
        return super().create(vals)

    def write(self, vals):
        if 'assign_date' in vals and 'return_date' in vals:
            # Si se modifica la fecha de asignación Y la de devolución para todos
            # los registros el estado será el mismo para todos
            vals.update({
                'state': self.determine_state(vals.get('assign_date', False), vals.get('return_date', False))
            })
            return super().write(vals)
        elif 'assign_date' in vals or 'return_date' in vals:
            # Si solo se modifica uno de los dos valore la fecha de asignación O la
            # de devolución el estado depenederá del otro valor del registro
            for rec in self:
                single_vals = dict(vals)
                assign_date = vals.get(
                    'assign_date', False) if 'assign_date' in vals else rec.assign_date
                return_date = vals.get(
                    'return_date', False) if 'return_date' in vals else rec.return_date
                single_vals.update({
                    'state': self.determine_state(assign_date, return_date)
                })
                super(MaintenanceEquipment, rec).write(single_vals)
            return True
        return super().write(vals)

    def determine_state(self, assign_date, return_date):
        if type(assign_date) == type('str'):
            assign_date = fields.Date.from_string(assign_date)
        if type(return_date) == type('str'):
            return_date = fields.Date.from_string(return_date)

        today = fields.Date.today()
        if assign_date and return_date:
            if assign_date <= today and today <= return_date:
                return 'borrowed'
            elif today > return_date:
                return 'expire'

        if assign_date and today > assign_date:
            return 'assigned'

        return False
