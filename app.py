from services.service_manager import ServiceManager
from services.sqs_event_service import SQSEventService
from zabbix.zabbix_client import ZabbixClient
from threading import Thread
import sys
import traceback
import time

def start_sqs_event_service(zabbix_client):
    try:
        print("----------------SQS Event Service is starting...")
        sqs_service = SQSEventService(zabbix_client)

        # Suponer que receive_messages tiene un bucle dentro
        while True:
            sqs_service.receive_messages()
            time.sleep(1)  # Añadir un breve tiempo de espera entre iteraciones
    except Exception as e:
        print("An error occurred in the SQS Event Service:")
        traceback.print_exc()

def main():
    try:
        # Inicializar el cliente de Zabbix
        zabbix_client = ZabbixClient()

        # Iniciar el servicio de eventos SQS en un hilo separado
        event_service_thread = Thread(target=start_sqs_event_service, args=(zabbix_client,))
        event_service_thread.start()

        # Iniciar otros servicios utilizando el ServiceManager
        service_manager = ServiceManager(zabbix_client)

        # Suponer que run_services tiene un bucle dentro
        while True:
            service_manager.run_services()
            time.sleep(1)  # Añadir un breve tiempo de espera entre iteraciones

        # Esperar a que termine el hilo del servicio de eventos
        event_service_thread.join()

    except Exception as e:
        print("An unhandled exception occurred in the main thread:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
