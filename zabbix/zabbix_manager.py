from zabbix.zabbix_client import ZabbixClient

class ZabbixManager:
    def __init__(self, zabbix_client):
        self.zabbix_client = zabbix_client
        self.host_id = self.zabbix_client.get_host_id()

    def ensure_item_exists(self, key, category):
        items = self.zabbix_client.get_items(self.host_id, key, category)
        if not items:
            self.zabbix_client.create_item(self.host_id, key, category)

    def send_data(self, key, data, category):
        self.ensure_item_exists(key, category)
        self.zabbix_client.send_data(key, data, category)
