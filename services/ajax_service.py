import requests
import os
from config.config import config


class AjaxService:
    def __init__(self):
        self.base_url = config.ajax_config['base_url']
        self.auth_endpoint = config.ajax_config['auth_endpoint']
        self.user_id = config.ajax_config['user_id']
        self.login = os.getenv('AJAX_LOGIN')
        self.password_hash = os.getenv('AJAX_PASSWORD_HASH')
        self.headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': os.getenv('X_API_KEY'),
          
        }
        self.session_token = None
        self.authenticate()

    def authenticate(self):
        if not self.base_url:
            raise ValueError("Base URL is not configured in config.json")
        
        data = {
            "login": self.login,
            "passwordHash": self.password_hash,
            "userRole": "USER"
        }
        print(data)

        response = requests.post(f"{self.base_url}{self.auth_endpoint}", headers=self.headers, json=data)
        response_data = response.json()

        if response.status_code == 200 and 'sessionToken' in response_data:
            self.session_token = response_data['sessionToken']
            print( response_data['sessionToken'])
            self.headers['X-Session-Token'] = self.session_token
            self.user_id = response_data.get('userId', self.user_id)
        else:
            raise Exception(f"Error al autenticarse con la API de Ajax: {response_data}")

    def make_request(self, service_config, **path_params):
        if 'userId' not in path_params:
            path_params['userId'] = self.user_id
        print(path_params)
        method = service_config.get('method', 'GET').upper()
        endpoint = service_config['endpoint']
        print(f"Endpoint before format: {endpoint}")
        print(f"Path parameters: {path_params}")

        try:
            endpoint = endpoint.format(**path_params)
        except KeyError as e:
            raise ValueError(f"Missing path parameter for URL: {e}")

        url = f"{self.base_url}{endpoint}"
        print(url, self.headers)
        response = requests.request(method, url, headers=self.headers)
        print('El servicio responde ',response.json())
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:  # No Content
            return []
        else:
            raise Exception(f"Failed to make request to {url}: {response.status_code} - {response.text}")

    def apply_output_filter(self, data, output_filter):
            """Aplica el filtro de salida si está presente y si el elemento es un diccionario."""
            if not data:
                return []

            if not output_filter:
                return data

            filtered_data = []
            for item in data:
                if isinstance(item, dict):
                    # Aplica el filtro solo a los elementos que son diccionarios
                    if all(item.get(key) == value for key, value in output_filter.items()):
                        filtered_data.append(item)
                else:
                    print(f"Advertencia: Se esperaba un diccionario, pero se encontró: {type(item)}. Item: {item}")
            return filtered_data
