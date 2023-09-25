from fastapi import FastAPI, Response, status
from pydantic import BaseModel

import os
import hashlib


users = {"aaa": {"hash": "3e744b9dc39389baf0c5a0660589b8402f3dbb49b89b3e75f2c9355852a3c677", "error_counter" : 0, "status": "ACTIVE"},
         "bbb": {"hash": "3e744b9dc39389baf0c5a0660589b8402f3dbb49b89b3e75f2c9355852a3c677", "error_counter" : 0, "status": "ACTIVE"},
         "ccc": {"hash": "3e744b9dc39389baf0c5a0660589b8402f3dbb49b89b3e75f2c9355852a3c677", "error_counter" : 0, "status": "ACTIVE"},
         "ddd": {"hash": "3e744b9dc39389baf0c5a0660589b8402f3dbb49b89b3e75f2c9355852a3c677", "error_counter" : 0, "status": "ACTIVE"},} 


class Credential(BaseModel):
    user: str
    secret: str

    def get_hashed_secret(self):
        h = hashlib.sha256()
        h.update(bytes(self.secret, 'utf-8'))
        return h.hexdigest()


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World", "os_name": os.name}


@app.post("/login")
async def validate_user(credential: Credential, response: Response):

    resp = {}
    if valid_credential(credential):
        resp = {"status": "FOUND"} #crea JWT
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        resp = {"msg": "wrong user or password"}

    return resp

def valid_credential(cred: Credential) -> bool:
    # cerca in archivio con user
    if cred.user not in users: # user not found
        print("1")
        return False
    
    user_rec = users[cred.user]

    if user_rec['status'] != 'ACTIVE': # user not active
        print("2")
        return False
    
    if user_rec['hash'] != cred.get_hashed_secret(): # wrong password
        print("3")
        user_rec['error_counter'] += 1
        if user_rec['error_counter'] > 3: # block user
            user_rec['status'] = 'BLOCKED'

        return False


    if user_rec['error_counter'] != 0: # reset counter
        user_rec['error_counter'] = 0

    return True
    

    

