from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
import uvicorn
import os

# MongoDB connection
client = MongoClient("mongodb+srv://swoyam:iiitdrive@drive.9oviyyw.mongodb.net/")
db = client.production

SECRET_KEY = "swoyamsiddharthnayak"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

class User(BaseModel):
    username: str
    email: str
    full_name: str
    phone: str

class UserInDB(User):
    hashed_password: str

class TokenData(BaseModel):
    username: Optional[str] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fake_hash_password(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = db["users"].find_one({"username": form_data.username})
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user_dict["_id"] = str(user_dict["_id"])  # Convert ObjectId to string
    user = UserInDB(**user_dict)
    password_ok = pwd_context.verify(form_data.password, user.hashed_password)
    if not password_ok:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    action = {
        "time" : datetime.now(),
        "action" : "Login",
        "event" : "Login action performed by user {user.username}"
    }
    db["actions"].insert_one(action)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup")
async def signup(user: User, password: str):
    hashed_password = fake_hash_password(password)
    user_in_db = UserInDB(**user.dict(), hashed_password=hashed_password)
    db["users"].insert_one(user_in_db.dict())
    import os
    #this will create a folder with username in uploaded folder
    os.makedirs(f"uploaded/{user.username}")
    action = {
        "time" : datetime.now(),
        "action" : "SignUp",
        "event" : "New user {user.username} signed up"
    }
    db["actions"].insert_one(action)
    return {"result": "User created"}

# for testing purpose, willbe deleted later
@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user_dict = db["users"].find_one({"username": token_data.username})
    if user_dict is None:
        raise credentials_exception
    user_dict["_id"] = str(user_dict["_id"])  # Convert ObjectId to string
    return user_dict

@app.get("/directories")
async def get_directories(token: str = Depends(oauth2_scheme), path: str = "/"):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        import os
        entries = os.listdir(f"./uploaded/{username}"+path)
        result_dict = {"directories": entries}
        action = {
            "time" : datetime.now(),
            "action" : "GetDirectories",
            "event" : "User {user.username} requested directories"
        }
        db["actions"].insert_one(action)
        return result_dict
    except JWTError:
        raise credentials_exception
    
@app.put("/create_directory")
async def create_directory(token: str = Depends(oauth2_scheme), path: str = "/", directory_name: str = "NewFolder"):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        import os
        os.makedirs(f"./uploaded/{username}{path}/{directory_name}")
        action = {
            "time" : datetime.now(),
            "action" : "CreateDirectory",
            "event" : "User {user.username} created a directory named {directory_name}"
        }
        db["actions"].insert_one(action)
        return {"result": "Directory created"}
    except JWTError:
        raise credentials_exception
    
@app.post("/upload")
async def upload_file(token: str = Depends(oauth2_scheme), file: UploadFile=File(...), path: str = "/"):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        from pathlib import Path
        os.makedirs(f"./uploaded/{username}", exist_ok=True)
        #this will save the file in the folder created above
        file_path = f"./uploaded/{username}{path}{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        #create a dictionary with details of the uploaded files in it
        file_details = {
            "filename": file.filename, 
            "content_type": file.content_type, 
            "path" : file_path, 
            "size": os.path.getsize(file_path), 
            "uploader": username, 
            "upload_time": datetime.now()
        }
        db["files"].insert_one(file_details)
        action = {
            "time" : datetime.now(),
            "action" : "Upload",
            "event" : "User {user.username} uploaded a file named {file.filename}"
        }
        db["actions"].insert_one(action)
        return {"result": "File uploaded"}
    except JWTError:
        raise credentials_exception
    
@app.get("/download")
async def download_file(token: str = Depends(oauth2_scheme), path: str = "/"):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        from pathlib import Path
        file_path = f"./uploaded/{username}{path}"
        action = {
            "time" : datetime.now(),
            "action" : "Download",
            "event" : "User {user.username} downloaded the file {file.filename}"
        }
        db["actions"].insert_one(action)
        return FileResponse(file_path, media_type='application/octet-stream', filename=file_path)
    except JWTError:
        raise credentials_exception
    
@app.delete("/delete")
async def delete_file(token: str = Depends(oauth2_scheme), path: str = "/"):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        from pathlib import Path
        file_path = f"./uploaded/{username}{path}"
        os.remove(file_path)
        db["files"].delete_one({"path": file_path})
        action = {
            "time" : datetime.now(),
            "action" : "Delete",
            "event" : "User {user.username} deleted the file {file.filename}"
        }
        db["actions"].insert_one(action)
        return {"result": "File deleted"}
    except JWTError:
        raise credentials_exception
    
@app.delete("/delete_directory")
async def delete_directory(token: str = Depends(oauth2_scheme), path: str = "/"):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        from pathlib import Path
        file_path = f"./uploaded/{username}{path}"
        import shutil
        shutil.rmtree(file_path)
        action = {
            "time" : datetime.now(),
            "action" : "DeleteDirectory",
            "event" : "User {user.username} deleted the directory {file.filename}"
        }
        db["actions"].insert_one(action)
        return {"result": "Directory deleted"}
    except JWTError:
        raise credentials_exception

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)