from odoo import fields, models, api, _
from odoo.exceptions import UserError

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    qty_liters_fuel = fields.Float(string="number of liters fuel")
    mail_activity = fields.Many2one('mail.activity', 'Mail Activity')

    def _set_odometer(self):
        '''
        Solo se redefine para cuando el servicio es desde la aplicacion no por la accion planificada, cuando 
        viene desde accion planificada no se puede crear odometer por que no se registra valores para el ultimo
        odometer ni la cantidad de combustible.or self._context:
        
        :param self:
        '''
        for record in self:
            if not record.odometer:
                raise UserError(_('Emptying the odometer value of a vehicle is not allowed.'))
            if (record.odometer - record.vehicle_id.odometer)< 0:
                raise UserError(_('The odometer value is minor than the last vehicule odometer.'))
            elif record.qty_liters_fuel > 0 and (record.odometer - record.vehicle_id.odometer)>0:
                #TODO: Solo se crea odometer si los valores son correctos.
                performance_car = (record.odometer - record.vehicle_id.odometer) / record.qty_liters_fuel
                odometer = self.env['fleet.vehicle.odometer'].create({
                    'value': record.odometer,
                    'date': record.date or fields.Date.context_today(record),
                    'vehicle_id': record.vehicle_id.id,
                    'performance': performance_car,
                    'driver_id' : record.purchaser_id,
                })
            else:
                odometer = self.env['fleet.vehicle.odometer'].create({
                    'value': record.odometer,
                    'date': record.date or fields.Date.context_today(record),
                    'vehicle_id': record.vehicle_id.id,
                    'performance': 0.0,
                    'driver_id' : record.purchaser_id,
                })
            self.odometer_id = odometer
            
    @api.onchange('state')
    def _onchange_state(self):
        '''
        Se ejecuta cuando se modifica el state del log service, si se marca como done  la actividad se pasa a hecho, 
        si se cancela se elimina la actividad
        :param self:
        '''
        if self.state == 'done':
            #TODO: Se marca como hecho la actividad relacioanda
            self.mail_activity.action_done()
        elif self.state == 'cancelled':
            #TODO: Se elimina la actividad relacioanda
            self.mail_activity.unlink()


