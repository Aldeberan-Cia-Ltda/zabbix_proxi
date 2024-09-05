import boto3
import os
import time
import json
from zabbix.zabbix_manager import ZabbixManager

class SQSEventService:
    def __init__(self, zabbix_client):
        self.sqs = boto3.client(
            'sqs',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        queue_name = os.getenv('EVENTS_QUEUE_NAME')
        self.queue_url = self.sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
        self.visibility_timeout = 30  # seconds

        # Instancia de ZabbixManager para enviar eventos a Zabbix
        self.zabbix_manager = ZabbixManager(zabbix_client)

    def receive_messages(self):
        while True:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20,  # Long polling
                VisibilityTimeout=self.visibility_timeout
            )
            print('-------------------El servicio de SQS está activo, respuesta:', response)

            messages = response.get('Messages', [])
            if messages:
                for message in messages:
                    self.process_message(message)
                    
                    # Verificar si 'ReceiptHandle' está presente antes de eliminar el mensaje
                    receipt_handle = message.get('ReceiptHandle')
                    if receipt_handle:
                        self.delete_message(receipt_handle)
                    else:
                        print("No 'ReceiptHandle' found in the message")
            else:
                time.sleep(5)  # Pausa breve antes de realizar la próxima consulta

    def process_message(self, message):
        print('-----------------------------------Estoy en los eventos---------------------------')
        event = message.get('Body')
        print(f"Received event: {event}")

        # Enviar el evento a Zabbix
        event_key = "device.event"  # Clave para identificar el evento en Zabbix
        self.zabbix_manager.send_data(event, event_key)

    def delete_message(self, receipt_handle):
        self.sqs.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )
        print("Message deleted successfully.")
