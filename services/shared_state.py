class SharedState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedState, cls).__new__(cls)
            cls._instance.data = {}
        return cls._instance

    def set_data(self, key, value):
        self._instance.data[key] = value

    def get_data(self, key, default=None):
        return self._instance.data.get(key, default)
