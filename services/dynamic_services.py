from .base_service import BaseService
import time
import logging

# Configurar el logger
logging.basicConfig(
    level=logging.INFO,  # Nivel de log mínimo (INFO y superior se guardarán)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Formato de los mensajes
    handlers=[
        logging.FileHandler("service_manager.log"),  # Guardar los logs en un archivo
        logging.StreamHandler()  # Mostrar los logs en la consola
    ]
)

# Crear un logger específico para este archivo
logger = logging.getLogger(__name__)

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

class RoomService(BaseService):
    def fetch_data(self):
        results = []
        print("Dependencia de data en RoomService: ", self.dependency_data)

        # Verificar que la dependencia sea un diccionario con 'hub_list'
        if isinstance(self.dependency_data, list):
                for hub_data in self.dependency_data:
                    hub_id = hub_data.get("hubId")
                    if hub_id:
                        response = self.ajax_service.make_request(self.config, hubId=hub_id)
                        if response:
                            results.extend(response)
                       
        else:
            print("Advertencia: No se encontró 'hub_list' en la dependencia de RoomService.")

        print('Rooms extraídas:', results)
        return results
    
class GenericDeviceService(BaseService):
    def fetch_data(self, dependency):
        hub_list = dependency.get("hub_list", [])
        device_list = dependency.get("device_list", [])

        filtered_devices = []

        # Aplicar el list_filter y output_filter en paralelo
        list_filters = self.config.get('list_filter', [])
        output_filters = self.config.get('output_filter', {})

        if list_filters and output_filters:
            # Aplicar el filtro de salida basado en el índice del filtro de lista
            for idx, filter_name in enumerate(list_filters):
                list_to_filter = dependency.get(filter_name, [])

                # Obtener el filtro correspondiente al índice actual en output_filters
                current_filter = {list(output_filters.keys())[idx]: list(output_filters.values())[idx]}

                # Aplicar el filtro a la lista de dispositivos
                filtered_subset = self.ajax_service.apply_output_filter(list_to_filter, current_filter)
                filtered_devices.extend(filtered_subset)
        else:
            # Si no hay filtros, usar todos los dispositivos
            filtered_devices = device_list

        print('Dispositivos filtrados:', filtered_devices)

        all_responses = []

        # Iterar sobre todos los hubs y dispositivos filtrados
        for hub_data in hub_list:
            hub_id = hub_data.get("hubId")
            if not hub_id:
                continue

            for device_data in filtered_devices:
                device_id = device_data.get("deviceId")
                if not device_id:
                    continue

                # Hacer una solicitud por cada dispositivo filtrado
                response = self.ajax_service.make_request(self.config, hubId=hub_id, deviceId=device_id)
                if response:
                    # Agregar hubId a la respuesta
                    response['hubId'] = hub_id
                    all_responses.append(response)

        if not all_responses:
            raise ValueError("No se pudo obtener datos válidos para hub_id o device_id.")
        
        # Devuelve todas las respuestas para ser procesadas
        return all_responses

    def process_data(self, data):
        all_processed_data = []
        
        # Procesar cada conjunto de datos recibido
        for individual_data in data:
            processed_data = super().process_data(individual_data)
            all_processed_data.append(processed_data)
            print('------------------Esta es la data enviada globalmente:', processed_data)

        category_name = self.config.get('category_name')

        # Enviar todos los datos procesados a Zabbix
        for processed in all_processed_data:
            self.zabbix_client.send_data(processed, category_name)

        return all_processed_data

    def run(self, dependency):
        while True:
       
                # Obtener los datos filtrados
                data = self.fetch_data(dependency)
                self.process_data(data)
                time.sleep(self.config.get('interval_readsend', 60))

class HubInfoService(BaseService):
    def fetch_data(self, dependency):
        hub_list = dependency.get("hub_list", [])
        print('El listado de hub_list en HubInfo', hub_list)
        if not hub_list:
            raise ValueError("No se encontraron hubs en las dependencias HubInfo.")

        results = []
        for hub_data in hub_list:
            hub_id = hub_data.get("hubId")
            if not hub_id:
                continue

            print(f"Obteniendo información para HubInfo hub_id: {hub_id}")
            print('Estoy inyenyodo')
            response = self.ajax_service.make_request(self.config, hubId=hub_id)
            if response:
                response['hubId'] = hub_id  # Incluir el hubId en la respuesta
                results.append(response)

        if not results:
            raise ValueError("No se obtuvieron datos válidos de los hubs.")

        return results

    def process_data(self, data):
        if not data:
            raise ValueError("Los datos proporcionados son None. Verifique la solicitud al servicio.")

        processed_data = super().process_data(data)

        # Enviar datos a Zabbix
        category_name = self.config.get('category_name', 'Hub')
        for hub_data in processed_data:
            print(f"Enviando datos a Zabbix para el hub {hub_data.get('hubId')}")
            self.zabbix_client.send_data(hub_data, category_name)

        return processed_data

    def run(self, dependency):
        while True:
            print(f"Ejecutando HubInfoService con dependencia: {dependency}")
            data = self.fetch_data(dependency)
            self.process_data(data)
            time.sleep(self.config.get('interval_readsend', 300))