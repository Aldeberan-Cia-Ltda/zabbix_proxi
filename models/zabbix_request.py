from pydantic import BaseModel

class ZabbixRequest(BaseModel):
    key: str
    value: dict
