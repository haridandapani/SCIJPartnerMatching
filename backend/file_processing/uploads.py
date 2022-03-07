import pandas as pd

from ..utils.constants import ALLOWED_EXTENSIONS

def is_allowed_file(filename): 
    return '.' in filename \
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename): 
    return filename.rsplit('.', 1)[1].lower()

def file_to_dataframe(file): 
    ext = get_file_type(file.filename)

    if ext == 'csv': 
        return pd.read_csv(file)
    elif ext == 'xlsx': 
        return pd.read_excel(file, engine='openpyxl')
    else: 
        return None  