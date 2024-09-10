from threading import Thread
from .dynamic_services import HubService, DeviceService, GenericDeviceService, RoomService
from config.config import config
from .ajax_service import AjaxService
from .shared_state import SharedState  # Importa la clase SharedState

class ServiceManager:
    def __init__(self, zabbix_client):
        self.zabbix_client = zabbix_client
        self.ajax_service = AjaxService()  # Crear una instancia de AjaxService
        self.services = self.create_services()

    def create_services(self):
        services = {}
        for service_name, service_config in config.services.items():
            if "interval_readsend" in service_config:
                service = self.create_continuous_service(service_name, service_config)
            else:
                service = self.create_base_service(service_name, service_config)
            services[service_name] = {
                "instance": service,
                "config": service_config
            }
        return services

    def create_base_service(self, service_name, service_config):
        if service_name == "hub_list":
            return HubService(service_config, self.ajax_service, self.zabbix_client)
        elif service_name == "device_list":
            return DeviceService(service_config, self.ajax_service, self.zabbix_client)
        elif service_name == "room_list":  # Nuevo servicio para obtener las habitaciones
            return RoomService(service_config, self.ajax_service, self.zabbix_client)

    def create_continuous_service(self, service_name, service_config):
        """Método para crear servicios continuos, es decir, servicios que deben ejecutarse repetidamente en intervalos."""
        return GenericDeviceService(service_config, self.ajax_service, self.zabbix_client)

    def run_services(self):
        dependency_data = {}

        # Ejecutar primero los servicios base (como hub_list)
        for service_name, service_data in self.services.items():
            service = service_data['instance']
            service_config = service_data['config']
            dependency = None

            if "interval_readsend" not in service_config:
                print(f"Ejecutando {service_name}...")

                if service_name == 'device_list' or service_name == 'room_list':
                    dependency = dependency_data.get('hub_list')
                
                # Si room_list depende de hub_list
                if service_name == 'room_list' and not dependency:
                    print(f"Advertencia: {service_name} requiere 'hub_list', pero no está disponible.")
                    continue

                # Ejecutar y almacenar las dependencias
                extracted_data = service.run(dependency)
                print(f"Resultado de {service_name}: {extracted_data}")
                dependency_data[service_name] = extracted_data
                print('Dependencias actualizadas:', dependency_data)

        # Asegurarse de que hub_list está disponible antes de room_list
        if 'hub_list' not in dependency_data:
            print("Advertencia: No se encontró 'hub_list' antes de ejecutar room_list.")
        else:
            print("Hub list cargado correctamente.")

        print("Dependencias finales antes de servicios continuos:", dependency_data)

        # Ejecutar servicios continuos
        threads = []
        for service_name, service_data in self.services.items():
            service = service_data['instance']
            service_config = service_data['config']

            if "interval_readsend" in service_config:
                # Proporcionar los datos de dependencia adecuados
                service.dependency_data = {
                    base_service: dependency_data.get(base_service, []) for base_service in service_config.get("service_base", [])
                }

                print(f"El servicio {service_name} tiene dependencias {service.dependency_data}")

                # Asegurar que service.dependency_data sea siempre un diccionario
                if not isinstance(service.dependency_data, dict):
                    raise ValueError(f"El servicio {service_name} recibió una dependencia que no es un diccionario: {type(service.dependency_data)}")

                thread = Thread(target=service.run, args=(service.dependency_data,))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()
