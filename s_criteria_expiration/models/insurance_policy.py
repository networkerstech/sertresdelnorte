# -*- coding: utf-8 -*-

from odoo import fields, models, api


class InsurancePolicy(models.Model):
    _name = 'insurance.policy'
    _description = 'Vehicle insurance policy'
    _rec_name = 'responsible_id'

    responsible_id = fields.Many2one('res.users', 'User', store=True, readonly=False)
    criteria_days = fields.Integer(string='Criteria days', help="Quantity expressed in days")
    active = fields.Boolean(string='Active', default=True)
