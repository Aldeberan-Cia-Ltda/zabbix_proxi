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
        raise NotImplementedError("Cada servicio debe implementar el método fetch_data.")

    def process_data(self, data):
        if data is None:
            raise ValueError("Los datos proporcionados a process_data son None. Verifique la solicitud al servicio.")

        # Verifica qué datos están entrando al filtro
        print("Datos antes de aplicar el filtro:", data)
        print("Filtro aplicado:", self.output_filter)
        
        print ( 'Este es lit filter',self.list_filter)
        if (self.list_filter==None):  
            filtered_data = self.ajax_service.apply_output_filter(data, self.output_filter)
        
            # Verifica qué datos quedan después de aplicar el filtro
            print("Datos después de aplicar el filtro:", filtered_data)

            output_data = []
        
            for item in filtered_data:
                output_data.append({output_key: item.get(output_value) for output_key, output_value in self.output.items()})
        else:
             
            output_data= data
        # Verifica los datos procesados finales
        print("Datos procesados finales:", output_data)
        return output_data

    def run(self, dependency=None):
        if dependency:
            self.dependency_data = dependency
        print('Valor depende',  self.dependency_data)
        data = self.fetch_data()
        if data is None:
            raise ValueError("fetch_data devolvió None. Asegúrese de que la solicitud al servicio fue exitosa.")
        
        processed_data = self.process_data(data)
        print('Este es el vlaor del proces',data, processed_data)
        return processed_data
