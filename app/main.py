import os
from datetime import datetime, timedelta

from credential import Credential
from user_status import UserStatus

from fastapi import FastAPI, Response, status
from pydantic import BaseModel
import couchdb
import jwt


DB_USER = 'admin'
DB_PASSWORD = 'pwd'
DB_ADDRESS = "localhost:5984"

JWT_SECRET = 'my_dirty_secret'


class CredentialWrapper(BaseModel):
    user: str
    secret: str


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World", "os_name": os.name}


@app.post("/login")
def validate_user(credential_wrap: CredentialWrapper, response: Response):

    credential = Credential(credential_wrap.user, credential_wrap.secret)
    del credential_wrap # remove plain password instance

    resp = {}
    if valid_credential(credential):
        jwt_payload = {'iat' : datetime.now(),
                       'exp' : datetime.now() + timedelta(minutes=15),
                       'user' : credential.user}
        resp = jwt.encode(jwt_payload, JWT_SECRET, "HS256")
        
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        resp = {"msg": "wrong user or password"}

    return resp


def valid_credential(cred: Credential) -> bool:
    
    couch = couchdb.Server("http://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_ADDRESS)
    db = couch['users']

    mango_query = {'selector' : {'user' : {'$eq' : cred.user} }}
    
    doc_counter = 0
    for doc in db.find(mango_query):
        doc_counter += 1

        if doc['status'] != UserStatus.ACTIVE: # user not active
            print('not active')
            return False
        
        if doc['hash'] != cred.secret: # wrong password
            print('worng password')
            doc['error_counter'] += 1
            if doc['error_counter'] > 3:
                doc['status'] = UserStatus.BLOCKED
            db.save(doc)
            
            return False

    if doc_counter == 0: # user not found
        return False
    
    # all correct
    if doc['error_counter'] > 0:
        doc['error_counter'] = 0
        db.save(doc)

    return True
