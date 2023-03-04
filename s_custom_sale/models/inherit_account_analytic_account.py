from odoo import fields, models, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    project_state = fields.Selection(
        [("running", "Running"), ("finished", "Finished")],
        string="Project State",
        default="running",
    )
