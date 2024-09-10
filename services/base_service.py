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

    def process_data(self, data):
        if data is None:
            raise ValueError("Los datos proporcionados son None. Verifique la solicitud al servicio.")
        
        print("Datos antes de aplicar el filtro:", data)
        filtered_data = self.apply_filters(data)
        print("Datos después de aplicar el filtro:", filtered_data)

        # Aplica el mapeo de salida solo si no es list_filter
        output_data = []
        if self.list_filter is None:
            output_data = [
                {output_key: item.get(output_value) for output_key, output_value in self.output.items()}
                for item in filtered_data
            ]
        else:
            output_data = filtered_data
        
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
        print('Este es el valor del proces:', processed_data)
        return processed_data
