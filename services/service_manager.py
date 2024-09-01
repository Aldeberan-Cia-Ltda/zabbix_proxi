from threading import Thread
from .dynamic_services import HubService, DeviceService, GenericDeviceService
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
        # Añadir más servicios base según sea necesario

    def create_continuous_service(self, service_name, service_config):
        return GenericDeviceService(service_config, self.ajax_service, self.zabbix_client)


    def run_services(self):
        dependency_data = {}

        for service_name, service_data in self.services.items():
            service = service_data['instance']
            service_config = service_data['config']
            dependency = None
            if "interval_readsend" not in service_config:
                print(f"Ejecutando {service_name}...")
                
                if service_name == 'device_list':
                    dependency = dependency_data.get('hub_list')
                extracted_data = service.run(dependency)
                print(f"Resultado de {service_name}: {extracted_data}")
              
                dependency_data[service_name] = extracted_data
                
                print('Dependencias actualizadas:', dependency_data)
        
        print("Dependencias finales antes de servicios continuos:", dependency_data)

        threads = []
        for service_name, service_data in self.services.items():
            service = service_data['instance']
            service_config = service_data['config']
            if "interval_readsend" in service_config:
                if "service_base" in service_config:
                    service.dependency_data = {
                        base_service: dependency_data.get(base_service, []) for base_service in service_config["service_base"]
                    }
                else:
                    service.dependency_data = {}

                print(f"El servicio {service_name} tiene dependencias {service.dependency_data}")

                thread = Thread(target=service.run, args=(service.dependency_data,))
                threads.append(thread)
                thread.start()
        for thread in threads:
            thread.join()
