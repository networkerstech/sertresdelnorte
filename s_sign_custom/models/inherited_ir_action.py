from odoo import models


class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    def create_action_report(self):
        """ Create a contextual action for each server action. """
        for action in self:
            action.write({'binding_model_id': action.model_id.id,
                          'binding_type': 'report'})
        return True
