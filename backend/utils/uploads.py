from .constants import ALLOWED_EXTENSIONS

def allowed_file(filename): 
    return '.' in filename \
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess(location, is_link=False): 
    if is_link: 
        # TODO: google api stuff
        pass 
    else: 
        # TODO: pandas stuff 
        pass 
    
    return None
