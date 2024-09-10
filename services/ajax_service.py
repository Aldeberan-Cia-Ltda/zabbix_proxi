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
        """Autenticar y obtener un nuevo token de sesión"""
        if not self.base_url:
            raise ValueError("Base URL is not configured in config.json")
        
        data = {
            "login": self.login,
            "passwordHash": self.password_hash,
            "userRole": "USER"
        }
        print(f"Autenticando con las credenciales: {data}")

        response = requests.post(f"{self.base_url}{self.auth_endpoint}", headers=self.headers, json=data)
        response_data = response.json()

        if response.status_code == 200 and 'sessionToken' in response_data:
            self.session_token = response_data['sessionToken']
            print(f"Nuevo token de sesión: {self.session_token}")
            self.headers['X-Session-Token'] = self.session_token
            self.user_id = response_data.get('userId', self.user_id)
        else:
            raise Exception(f"Error al autenticarse con la API de Ajax: {response_data}")

    def make_request(self, service_config, **path_params):
        """Realiza una solicitud HTTP con el token de sesión. Renueva el token si es necesario."""
        if 'userId' not in path_params:
            path_params['userId'] = self.user_id
        print(f"Parámetros de la ruta: {path_params}")

        method = service_config.get('method', 'GET').upper()
        endpoint = service_config['endpoint']
        print(f"Endpoint antes de formatear: {endpoint}")

        try:
            endpoint = endpoint.format(**path_params)
        except KeyError as e:
            raise ValueError(f"Falta un parámetro de la ruta: {e}")

        url = f"{self.base_url}{endpoint}"
        print(f"Haciendo solicitud a: {url}")
        
        response = requests.request(method, url, headers=self.headers)
        print(f"Respuesta del servicio: {response.status_code}")

        # Manejo de errores por token expirado
        if response.status_code == 401:
            print("Token expirado o no autorizado. Intentando renovar el token...")
            self.authenticate()  # Renovar el token
            self.headers['X-Session-Token'] = self.session_token
            print("Reintentando la solicitud con un nuevo token...")
            response = requests.request(method, url, headers=self.headers)  # Reintentar la solicitud

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:  # No Content
            return []
        else:
            raise Exception(f"Fallo en la solicitud a {url}: {response.status_code} - {response.text}")

    def apply_output_filter(self, data, output_filter):
        """Aplica el filtro de salida si está presente y si el elemento es un diccionario."""
        if not data:
            return []

        if not output_filter:
            return data

        filtered_data = []
        for item in data:
            if isinstance(item, dict):
                if all(item.get(key) == value for key, value in output_filter.items()):
                    filtered_data.append(item)
            else:
                print(f"Advertencia: Se esperaba un diccionario, pero se encontró: {type(item)}. Item: {item}")
        return filtered_data
