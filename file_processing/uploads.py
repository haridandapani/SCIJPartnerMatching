import pandas as pd

from file_processing.constants import ALLOWED_EXTENSIONS

def is_allowed_file(filename): 
    return '.' in filename \
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename): 
    return filename.rsplit('.', 1)[1].lower()

def file_to_dataframe(file, chop_header=False): 
    ext = get_file_type(file.filename)

    if ext == 'csv': 
        if chop_header: 
            return pd.read_csv(file)
        else: 
            return pd.read_csv(file, header=None)
    elif ext == 'xlsx': 
        if chop_header: 
            return pd.read_excel(file, engine='openpyxl')
        else: 
            return pd.read_excel(file, engine='openpyxl', header=None)
    else: 
        return None  
