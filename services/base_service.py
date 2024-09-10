class BaseService:
    def __init__(self, config, ajax_service, zabbix_client):
        self.config = config
        self.ajax_service = ajax_service
        self.zabbix_client = zabbix_client
        self.endpoint = config.get("endpoint")
        self.output = config.get("output", {})
        self.output_filter = config.get("output_filter", {})
        self.list_filter = config.get("list_filter", [])
        self.category_name = config.get("category_name")
        self.dependency_data = {}

    def fetch_data(self):
        raise NotImplementedError("Each service must implement the fetch_data method.")

    def process_data(self, data):
        if data is None:
            raise ValueError("Los datos proporcionados son None. Verifique la solicitud al servicio.")
        
        filtered_data = []
        if self.output_filter:  # Si hay un filtro, aplicarlo
            filtered_data = self.ajax_service.apply_output_filter(data, self.output_filter)
        else:  # Si no hay filtro, procesar toda la lista
            filtered_data = data
        
        output_data = []
        for item in filtered_data:
            output_data.append({output_key: item.get(output_value) for output_key, output_value in self.output.items()})
        return output_data

    def run(self):
        data = self.fetch_data()
        if data is None:
            raise ValueError("fetch_data devolvió None. Asegúrese de que la solicitud al servicio fue exitosa.")
        
        processed_data = self.process_data(data)
        return processed_data
