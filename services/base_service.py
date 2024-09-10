class BaseService:
    def __init__(self, config, ajax_service, zabbix_client):
        self.config = config
        self.ajax_service = ajax_service
        self.zabbix_client = zabbix_client
        self.endpoint = config.get("endpoint")
        self.output = config.get("output", {})
        self.output_filter = config.get("output_filter", {})
        self.category_name = config.get("category_name")
        self.list_filter = config.get("list_filter")
        self.embedded_data = config.get("embeddedData", [])  # Carga de configuración para embebido de datos
        self.dependency_data = {}  # Almacena los datos de dependencia que se pasan al ejecutar el servicio

    def fetch_data(self):
        """Este método debe ser implementado por cada servicio específico"""
        raise NotImplementedError("Cada servicio debe implementar el método fetch_data.")

    def apply_filters(self, data):
        """Aplica filtros de salida o lista si están presentes."""
        if not data:
            return []

        if self.list_filter is None:
            # Aplica output_filter si no se especifica list_filter
            filtered_data = self.ajax_service.apply_output_filter(data, self.output_filter)
        else:
            # Si hay list_filter, no se aplica el filtro normal
            print(f"Aplicando list_filter: {self.list_filter} con output_filter: {self.output_filter}")
            filtered_data = data

        return filtered_data

    def apply_embedded_data(self, data):
        """Aplica la lógica de embebido de datos heredados o comparados en los objetos basados en la configuración."""
        if not self.embedded_data:  # Si no hay datos embebidos configurados, devolvemos los datos originales
            return data

        print("--------------Aplicando embebido--------------")

        # Recorrer la lista de embebidos configurados
        for embed in self.embedded_data:
            hubid = ""
            print('Cada emebido', embed)
            service_base = embed.get("serviceBase")
            type_embedded = embed.get("typeEmbedded")
            properties_service = embed.get("propertiesService", {})

            # Verificar si los datos de dependencia del service_base existen
            print('Dependency ',self.dependency_data)
            base_data = self.dependency_data.get(service_base, [])

            if not base_data:
                print(f"Advertencia: No se encontraron datos para {service_base} en las dependencias.")
                continue

            
            if type_embedded == "heredado":
                # Para el tipo heredado, copiar directamente las propiedades de base_data a los datos del objeto
                print('------------Embeber datos heredados------------', data)
                hubid = data['hubId']
                filtrado = next((ejemplo for ejemplo in base_data if ejemplo['hubId'] == hubid), None)
                if isinstance(filtrado, dict):  # Asegurarse de que 'base_item' es un diccionario
                    for prop_key, base_key in properties_service.items():
                        data[prop_key] = filtrado.get(base_key, None)

            elif type_embedded == "comparado":
                # Para el tipo comparado, encontrar el objeto en base_data que coincide con keyCompared
                key_compared = embed.get("keyCompared", {})
                print(f"------------con keyCompared: {key_compared}")

                # Recorremos los datos del dispositivo y buscamAplicando comparado os la coincidencia en base_data
                if isinstance(data, dict):  # Asegurarse de que 'data' es un diccionario
                    room_id = data.get("roomId")  # Obtener roomId del dispositivo
                    print('romDevice', room_id, base_data)
                    if room_id:
                        filtrado = next((item for item in base_data if item.get('roomId') == (room_id)), None)
                        if filtrado:
                            print('Hay filtado de room', filtrado)
                            # Si hay una coincidencia en room_list, embebemos los datos de propertiesService
                            for prop_key, base_key in properties_service.items():
                                data[prop_key] = filtrado.get(base_key, None)

        return data

    def process_data(self, data):
        if data is None:
            raise ValueError("Los datos proporcionados son None. Verifique la solicitud al servicio.")

        # Aplicar filtros
        print("Datos antes de aplicar el filtro:", data)
        filtered_data = self.apply_filters(data)
        print("Datos después de aplicar el filtro:", filtered_data)

        # Aplicar datos embebidos si existen en la configuración
        if self.embedded_data:
          
            filtered_data = self.apply_embedded_data(filtered_data)

        # Mapeo de salida solo si no es list_filter
        output_data = []
        if self.list_filter is None:
            for item in filtered_data:
                if isinstance(item, dict):  # Asegurarse de que 'item' es un diccionario
                    output_data.append({output_key: item.get(output_value) for output_key, output_value in self.output.items()})
                else:
                    print(f"Advertencia: Se esperaba un diccionario, pero se encontró: {type(item)}. Item: {item}")
        else:
            output_data = filtered_data  # Si es list_filter, devuelve los datos directamente

        print("Datos procesados finales:", output_data)
        return output_data

    def run(self, dependency=None):
        if dependency:
            self.dependency_data = dependency
        print('Valor depende:', self.dependency_data)

        data = self.fetch_data()
        if data is None:
            raise ValueError("fetch_data devolvió None. Asegúrese de que la solicitud al servicio fue exitosa.")

        processed_data = self.process_data(data)
        print('Este es el valor del procesado:', processed_data)
        return processed_data
