import os
import json
from dotenv import load_dotenv

class Config:
    def __init__(self, config_file='config/config.json'):
        load_dotenv()

        self.zabbix_config = {
            'api_url': os.getenv('ZABBIX_API_URL'),
            'user': os.getenv('ZABBIX_USER'),
            'password': os.getenv('ZABBIX_PASSWORD'),
            'host_name': os.getenv('ZABBIX_HOST_NAME'),
            'use_authentication': os.getenv('USE_AUTHENTICATION', 'true').lower() == 'true',
            'api_token': os.getenv('ZABBIX_API_TOKEN'),
            'zabbix_server_port': os.getenv('ZABBIX_SERVER_PORT'),
            'zabbix_server_ip': os.getenv('ZABBIX_SERVER_IP')
        }

        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        self.services = config_data['services']
        self.ajax_config = config_data['ajax']

    def get_service_config(self, service_name):
        return self.services.get(service_name, {})

config = Config()
