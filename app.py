import sys
import traceback
from threading import Thread
from services.service_manager import ServiceManager
from services.sqs_event_service import SQSEventService
from zabbix.zabbix_client import ZabbixClient

def start_sqs_event_service(zabbix_client):
    try:
        print("----------------SQS Event Service is starting...")
        sqs_service = SQSEventService(zabbix_client)
        sqs_service.receive_messages()
    except Exception as e:
        print("An error occurred in the SQS Event Service:")
        traceback.print_exc()

def main():
    try:
        # Inicializar el cliente de Zabbix
        print("Iniciando el cliente de Zabbix...")
        zabbix_client = ZabbixClient()

        # Iniciar el servicio de eventos SQS en un hilo separado
        print("Iniciando el servicio de eventos SQS en un hilo separado...")
        event_service_thread = Thread(target=start_sqs_event_service, args=(zabbix_client,))
        event_service_thread.start()

        # Iniciar otros servicios utilizando el ServiceManager
        print("Iniciando otros servicios utilizando el ServiceManager...")
        service_manager = ServiceManager(zabbix_client)
        service_manager.run_services()

        # Esperar a que termine el hilo del servicio de eventos
        event_service_thread.join()

    except KeyboardInterrupt:
        print("\nAplicación interrumpida por el usuario. Cerrando...")
        sys.exit(0)

    except Exception as e:
        print("An unhandled exception occurred in the main thread:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
