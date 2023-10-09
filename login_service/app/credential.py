import hashlib


class Credential:
    def __init__(self, user : str, secret : str):
        self.user = user
        self.secret = hash_256(secret)  



def hash_256(str_in : str) -> str:
    h = hashlib.sha256()
    h.update(bytes(str_in, 'utf-8'))
    
    return h.hexdigest()
