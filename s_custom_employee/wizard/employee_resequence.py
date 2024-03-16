# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import AccessError

# id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# access_employee_resequence_wizard,access.employee.resequence.wizard,model_employee_resequence_wizard,hr.group_hr_manager,1,1,1,1

class EmployeeReSequenceWizard(models.TransientModel):
    _name = 'employee.resequence.wizard'
    _description = 'Remake the sequence of employees.'

    def resequence(self):
        sequence = self.env.ref(
            's_custom_employee.hr_employee_employee_sequence_number')

        # Force sequence restart
        sequence.write({
            'implementation': sequence.implementation,
            'number_next': 1,
        })

        employees = self.env['hr.employee'].search([], order='id')
        for employee in employees:
            employee.number_employee = sequence._next()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
