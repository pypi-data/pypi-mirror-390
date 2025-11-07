from .xlxs_writer import XLSXWriter
from .openlineage_writer import OpenLineageWriter

def get_writer(fmt):
    if fmt == "excel":
        return XLSXWriter
    elif fmt.lower() == "openlineage":
        return OpenLineageWriter