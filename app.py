import sys
import traceback
import time
from threading import Thread
from services.service_manager import ServiceManager
from services.sqs_event_service import SQSEventService
from zabbix.zabbix_client import ZabbixClient

def start_sqs_event_service(zabbix_client):
    """Función para manejar el servicio SQS."""
    try:
        print("----------------SQS Event Service is starting...")
        sqs_service = SQSEventService(zabbix_client)
        sqs_service.receive_messages()
    except Exception as e:
        print("An error occurred in the SQS Event Service:")
        traceback.print_exc()

def start_service_manager(zabbix_client):
    """Función para manejar el ServiceManager."""
    try:
        print("Iniciando otros servicios utilizando el ServiceManager...")
        service_manager = ServiceManager(zabbix_client)
        service_manager.run_services()
    except Exception as e:
        print("An unhandled exception occurred in the ServiceManager:")
        traceback.print_exc()

def main():
    try:
        # Inicializar el cliente de Zabbix
        print("Iniciando el cliente de Zabbix...")
        zabbix_client = ZabbixClient()

        # Iniciar el servicio de eventos SQS en un hilo separado
        print("Iniciando el servicio de eventos SQS en un hilo separado...")
        event_service_thread = Thread(target=start_sqs_event_service, args=(zabbix_client,), daemon=True)
        event_service_thread.start()

        # Iniciar el ServiceManager en un hilo separado
        service_manager_thread = Thread(target=start_service_manager, args=(zabbix_client,), daemon=True)
        service_manager_thread.start()

        # Mantener el contenedor corriendo
        while event_service_thread.is_alive() or service_manager_thread.is_alive():
            time.sleep(1)

    except Exception as e:
        print("An unhandled exception occurred in the main thread:")
        traceback.print_exc()

if __name__ == '__main__':
    main()
