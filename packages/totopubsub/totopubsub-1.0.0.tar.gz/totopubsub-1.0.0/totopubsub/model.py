


from typing import Literal
from totopubsub.logger import Logger


class TotoMessageData: 
    id: str
    event_name: str
    msg: str
    data: str
    
    def __init__(self, id: str, event_name: str, msg: str, data: str):
        self.id = id
        self.event_name = event_name
        self.msg = msg
        self.data = data

class TotoMessage: 
    def __init__(self, timestamp: str, cid: str, id: str, type: str, msg: str, data: dict):
        self.timestamp = timestamp
        self.cid = cid
        self.id = id
        self.type = type
        self.msg = msg
        self.data = data

class Context: 
    correlation_id: str 
    region: str 
    hyperscaler: Literal["aws", "gcp"] 

    def __init__(self, correlation_id: str, region: str, hyperscaler: Literal["aws", "gcp"]):
        self.correlation_id = correlation_id
        self.region = region
        self.hyperscaler = hyperscaler
