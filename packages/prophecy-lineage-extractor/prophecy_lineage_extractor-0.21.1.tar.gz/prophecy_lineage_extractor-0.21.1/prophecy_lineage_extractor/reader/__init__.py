from .websocket_reader import WebsocketPipelineProcessor
from .rest_reader import RestPipelineProcessor

def get_reader(reader):
    if reader == "lineage":
        return WebsocketPipelineProcessor
    elif reader.lower() == "knowledge-graph":
        return RestPipelineProcessor