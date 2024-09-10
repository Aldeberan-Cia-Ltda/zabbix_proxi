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

        filtered_devices = []

        # Aplicar list_filter si está presente
        if 'list_filter' in self.config:
            list_filter_name = self.config['list_filter']
            list_to_filter = dependency.get(list_filter_name[0], [])

            # Aplicar el filtro de la lista
            filtered_devices = self.ajax_service.apply_output_filter(list_to_filter, self.config.get('output_filter', {}))
        else:
            filtered_devices = device_list
        
        print('Se aplica el filtro:', filtered_devices)

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
        processed_data = super().process_data(data)
        print('------------------Esta es la data enviada globalmente:', processed_data)
        category_name = self.config.get('category_name')
        self.zabbix_client.send_data(processed_data, category_name)
        return processed_data

    def run(self, dependency):
        while True:
            data = self.fetch_data(dependency)
            self.process_data(data)
            time.sleep(self.config.get('interval_readsend', 60))

class RoomService(BaseService):
 
    def fetch_data(self):
        results = []
        print("Dependencia de data en DeviceService: ", self.dependency_data)
        
        if isinstance(self.dependency_data, list):
            for hub in self.dependency_data["hub_list"]:
                hub_id = hub.get("hubId")
                response = self.ajax_service.make_request(self.config, hubId=hub_id)
                if response:
                    results.extend(response)

            self.dependency_data = results  # Guardar los resultados en dependencia
        print('Rooms extraídas:', results)
        return results