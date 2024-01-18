# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from odoo.tools import format_date


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    creation_scheduled_activity = fields.Boolean(default=False)

    @api.model
    def _cron_check_vehicle_service_validity(self):
        '''
        Se modifica el cron para que recorra todo los vehiculos y busque los log service que se pueden aplicar segun los criterios
        de km desde el ultimo servicio, los day desde el ultimo sericio, y si tiene contrato los sericios relacioandos al contrato
        :param self:
        '''
        list_vehicles = self.search([])

        count = 0
        for v in list_vehicles:
            #TODO: Buscar la fecha y el domometro del ultimo Servicio
            last_service = v.log_services.filtered(lambda x: x.state in ("new", "running","done")).sorted('date')
            #TODO Si existe al menos un servicio para el vehiculo
            if len(last_service) > 0:
                last_date_service = last_service[-1].date
                last_odometer_service = last_service[-1].odometer
            else:
                #TODO: se toma los dias desde el dia de aquicision y el odometro del ultimo
                #servicio lo ponemos a 0
                last_date_service = v.acquisition_date if v.acquisition_date else fields.Date.today()
                last_odometer_service = 0

            #TODO: Buscar los valores del odometro a dia de hoy
            odometer_today = v.odometer - last_odometer_service
            # odometer_today = 10000
            #TODO: Buscar los dias desde el ultimo Servicio
            day_from_last_service = (fields.Date.today() - last_date_service).days

            # day_from_last_service= 179

            #TODO: Buscamos los tipos de servicios relacionados al contrato vigente del vehiculo,
            #si tiene mas de uno tomamos el primero en comenzar
            contrat_active = v.log_contracts.filtered(lambda x: x.state in ("open")).sorted('start_date')

            #TODO: Buscamos que servicio por km ,tiempo, donde los km sean mayor que 0 y ademas que el
            #tipo de servicio este definido en el contrado relacionado al vehicule
                #TODO: si tiene definido un tipo de servicio dentro del contrato
            if contrat_active:
                #TODO: Si tiene un contrato, buscamos los servicios del primer contrato activo en inicar
                service_contrat_active = contrat_active[0].service_ids
                list_services = self.env['vehicle.service'].search(["|",("criteria_days", "<=", day_from_last_service),("criteria_km", "<=", odometer_today),("criteria_km", ">", 0),('services_id', 'in', service_contrat_active.ids)],order='criteria_km DESC')
                #TODO: Buscando el provedor del contrato
                vendor_id = contrat_active.insurer_id
            else:
                #TODO: Si no tiene un tipo de servicio en el contrato, el creiterio es que cumpla los dias y que sea el mas cercano segun los km desde el ultimo servicio, que es el mayo criteria_km tenga
                list_services = self.env['vehicle.service'].search(["|",("criteria_days", "<=", day_from_last_service),("criteria_km", "<=", odometer_today),("criteria_km", ">", 0)],order='criteria_km DESC')

            #TODO: Preparar al vals para crear el servicio
            if list_services:
                #TODO: Buscando el Responsable del servicio(responsible_id)
                mail_activity = v.activity_schedule('mail.mail_activity_data_todo',note=_('The vehicle with license plate %(vehicle)s is responsible for carrying out the service %(service)s',vehicle=v.license_plate,service=list_services[0].display_name),user_id=list_services[0].responsible_id.id)

                vals = ({
                    "vehicle_id": v.id,
                    "description": _("Automatic creation of service: %s",list_services[0].services_id.name),
                    "date": fields.Date.today(),
                    "service_type_id": list_services[0].services_id.id,
                    "purchaser_id": v.driver_id.id,
                    "odometer": v.odometer,
                    "mail_activity": mail_activity.id,
                    "vendor_id": vendor_id.id if vendor_id else False
                })

                log_service_new = self.env["fleet.vehicle.log.services"].with_context(cron_check_service=True).create(vals)
                count +=1