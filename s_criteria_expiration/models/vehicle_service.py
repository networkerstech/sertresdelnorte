from odoo import fields, models, api


class VehicleService(models.Model):
    _name = 'vehicle.service'
    _description = 'Vehicle service'
    _rec_name = 'services_id'

    services_id = fields.Many2one('fleet.service.type', store=True)
    responsible_id = fields.Many2one('res.users', string='Responsible', store=True, readonly=False)
    criteria_days = fields.Integer(string='Criteria Days', help="Quantity expressed in days")
    criteria_km = fields.Integer(string='Criteria KMs', help="Quantity expressed in KM")
    active = fields.Boolean(string='Active', default=True)
        
