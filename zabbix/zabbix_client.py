import requests
import json
import time
import subprocess
from config.config import config

class ZabbixClient:
    def __init__(self):
        self.api_url = config.zabbix_config['api_url']
        self.use_authentication = config.zabbix_config['use_authentication']
        self.auth_token = None

        if self.use_authentication:
            self.user = config.zabbix_config['user']
            self.password = config.zabbix_config['password']
            self.authenticate()
        else:
            self.auth_token = config.zabbix_config['api_token']
        
        self.host_name = config.zabbix_config['host_name']
        self.zabbix_server_ip = config.zabbix_config['zabbix_server_ip']
        self.zabbix_server_port = config.zabbix_config['zabbix_server_port']

    def authenticate(self):
        headers = {'Content-Type': 'application/json'}
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "username": self.user,
                "password": self.password
            },
            "id": 1
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        self.auth_token = response.json().get('result')

    def get_host_id(self):
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.auth_token}'}
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "filter": {
                    "host": [self.host_name]
                },
                "output": ["hostid", "name"]
            },
            "auth": self.auth_token,
            "id": 1
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json().get('result', [])
        return result[0]['hostid'] if result else None

    def get_items(self, host_id, category_name):
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.auth_token}'}
        data = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "hostids": host_id,
                "filter": {
                    "key_": f"{category_name.lower()}.metric"
                }
            },
            "auth": self.auth_token,
            "id": 1
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print('Si existe el ITEMs------------------------')
        return response.json().get('result', [])
    
    def create_item(self, host_id, category_name):
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.auth_token}'}
        data = {
            "jsonrpc": "2.0",
            "method": "item.create",
            "params": {
                "hostid": host_id,
                "key_": f"{category_name.lower()}.metric",
                "value_type": 4,  # JSON
                "type": 2,        # Zabbix trapper
                "name": f"{category_name} Metric",
                "description": f"Metrics for {category_name} devices"
            },
            "auth": self.auth_token,
            "id": 1
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        print ('respuesta de creacion de datos',response.json())
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()

    def send_data(self, json_value, category_name):
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.auth_token}'}
        try:
            host_id = self.get_host_id()
            items = self.get_items(host_id, category_name)

            # Verificar si el item existe, si no, crearlo
            if not items:
                self.create_item(host_id, category_name)
                items = self.get_items(host_id, category_name)

            if not items:
                raise Exception(f"Failed to retrieve or create Zabbix item for category {category_name}")

            """
            Envía los datos a Zabbix usando zabbix_sender.
            """
            # Convertir el JSON en una cadena para enviar a Zabbix
            value = json.dumps(json_value)
            
            # Comando para enviar los datos usando zabbix_sender
            command = [
                'zabbix_sender',
                '-z', self.zabbix_server_ip,
                '-p', self.zabbix_server_port,
                '-s', self.host_name,
                '-k', f'{category_name.lower()}.metric',
                '-o', value
            ]
            print('Comandos de zabix', command)

            # Ejecutar el comando y capturar la salida
            
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error al enviar datos a Zabbix: {result.stderr}")
            else:
                print(f"Datos enviados a Zabbix: {result.stdout}")
        except Exception as e:
            print(f"Exception al ejecutar zabbix_sender: {str(e)}")