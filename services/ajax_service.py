import requests
import os
import time
from config.config import config

class AjaxService:
    MAX_RETRIES = 3  # Número máximo de intentos de renovación de token
    RETRY_DELAY = 3  # Tiempo de espera entre intentos (en segundos)

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
            raise ValueError("Base URL no está configurada en config.json")
        
        data = {
            "login": self.login,
            "passwordHash": self.password_hash,
            "userRole": "USER"
        }
        print(f"Autenticando con las credenciales: {data}")

        try:
            response = requests.post(f"{self.base_url}{self.auth_endpoint}", headers=self.headers, json=data)
            response.raise_for_status()  # Lanza una excepción para códigos de estado 4xx o 5xx
            response_data = response.json()

            if 'sessionToken' in response_data:
                self.session_token = response_data['sessionToken']
                self.headers['X-Session-Token'] = self.session_token
                self.user_id = response_data.get('userId', self.user_id)
                print(f"Autenticación exitosa. Token de sesión: {self.session_token}")
            else:
                raise Exception("Respuesta inesperada al autenticarse, no se encontró 'sessionToken'.")
        
        except requests.exceptions.RequestException as e:
            print(f"Error en la autenticación: {e}")
            raise Exception(f"Error al autenticarse con la API de Ajax: {str(e)}")

    def make_request(self, service_config, **path_params):
        """Realiza una solicitud HTTP con el token de sesión. Renueva el token si es necesario."""
        if 'userId' not in path_params:
            path_params['userId'] = self.user_id
        
        method = service_config.get('method', 'GET').upper()
        endpoint = service_config['endpoint']
        print('Este el el END', path_params, endpoint)
        # Formatear el endpoint con los parámetros
        try:
            endpoint = endpoint.format(**path_params)
        except KeyError as e:
            raise ValueError(f"Falta un parámetro de la ruta: {e}")

        url = f"{self.base_url}{endpoint}"
        print(f"Haciendo solicitud a: {url} con método {method}")

        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.request(method, url, headers=self.headers)
                response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa

                if response.status_code == 200:
                    print(f"Respuesta exitosa (200) de {url}")
                    return response.json()
                elif response.status_code == 204:
                    print(f"Respuesta vacía (204) de {url}")
                    return []  # No Content

            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 401:  # Error de autenticación
                    print(f"Intento {attempt + 1}/{self.MAX_RETRIES}: Token expirado o no autorizado.")
                    self.authenticate()  # Renovar el token
                    self.headers['X-Session-Token'] = self.session_token
                    print("Reintentando la solicitud con un nuevo token...")
                    time.sleep(self.RETRY_DELAY)  # Espera antes de reintentar
                    continue  # Reintentar la solicitud
                else:
                    # Otros errores HTTP no relacionados con la autenticación
                    print(f"Error HTTP: {http_err} - Respuesta: {response.text}")
                    raise Exception(f"Fallo en la solicitud a {url}: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as req_err:
                print(f"Error en la solicitud: {req_err}")
                raise Exception(f"Error en la solicitud a {url}: {str(req_err)}")
        
        # Si se superan los intentos de reintento
        raise Exception(f"Fallo en la solicitud después de {self.MAX_RETRIES} intentos. No se pudo renovar el token.")

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
