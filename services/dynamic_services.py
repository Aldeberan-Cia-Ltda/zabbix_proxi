from .base_service import BaseService
import time
class HubService(BaseService):
    def fetch_data(self):
        response = self.ajax_service.make_request(self.config)
        
        if not response:
            raise ValueError("La respuesta del servidor es vacía o no válida.")

        # filtered_data = self.ajax_service.apply_output_filter(response, self.config.get('output_filter', {}))

        # extracted_data = []
        # for item in filtered_data:
        #     dynamic_data = {}
        #     for output_key, service_key in self.config['output'].items():
        #         dynamic_data[output_key] = item.get(service_key)
            
        #     extracted_data.append(dynamic_data)
        
        self.dependency_data = response
        print('Extrae data', response)
        return response


class DeviceService(BaseService):
    def fetch_data(self):
        results = []
        print("Dependencia de data en DeviceService: ", self.dependency_data)
        
        if isinstance(self.dependency_data, list):
            for hub_data in self.dependency_data:
                hub_id = hub_data.get("hubId")
                if hub_id:
                    response = self.ajax_service.make_request(self.config, hubId=hub_id)
                    if response:
                        results.extend(response)
        else:
            print("La dependencia de datos no está estructurada correctamente.")
        
        print('Dispositivos extraídos:', results)
        return results


class GenericDeviceService(BaseService):
    def fetch_data(self, dependency):
        hub_list = dependency.get("hub_list", [])
        device_list = dependency.get("device_list", [])
        
        # Si no hay output_filter, usar toda la lista
        filtered_devices = device_list
        
        # Si hay list_filter y output_filter, procesamos los dispositivos en base al filtro
        if self.list_filter and self.output_filter:
            list_filter_name = self.list_filter[0]  # Asumiendo que siempre queremos el primero de list_filter
            list_to_filter = dependency.get(list_filter_name, [])
            
            # Iteramos sobre el output_filter y list_filter en paralelo
            filtered_devices = []
            for idx, filter_key in enumerate(self.output_filter):
                if idx < len(list_to_filter):
                    current_filter = {filter_key: self.output_filter[filter_key]}
                    devices = self.ajax_service.apply_output_filter(list_to_filter[idx], current_filter)
                    filtered_devices.extend(devices)

        # Procesar la lista filtrada y realizar solicitudes
        for hub_data in hub_list:
            hub_id = hub_data.get("hubId")
            if not hub_id:
                continue
            
            for device_data in filtered_devices:
                device_id = device_data.get("deviceId")
                if not device_id:
                    continue

                response = self.ajax_service.make_request(self.config, hubId=hub_id, deviceId=device_id)
                if response:
                    return response
        
        raise ValueError("No se pudo obtener datos válidos para hub_id o device_id.")
    
    def process_data(self, data):
        # Modularizamos el envío de datos, comprobando que existan elementos a enviar
        if not data:
            print("No hay datos procesados para enviar a Zabbix.")
            return

        processed_data = super().process_data(data)
        category_name = self.config.get('category_name')
        self.zabbix_client.send_data(processed_data, category_name)
        
        return processed_data

    def run(self, dependency):
        while True:
            data = self.fetch_data(dependency)
            self.process_data(data)
            time.sleep(self.config.get('interval_readsend', 60))  # Por defecto, cada 60 segundos
