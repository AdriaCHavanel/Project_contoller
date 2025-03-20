import pandas as pd
import numpy as np
import mimetypes
def Read_XML(file_name):
    namespaces = {"ns": "http://eop-cfi.esa.int/CFI"}

    # Read XML and extract <Event> elements
    df = pd.read_xml(file_name, xpath=".//ns:Event", namespaces=namespaces)
    return(df)

