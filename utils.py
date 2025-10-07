import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from database import *
from models import *

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRES = 60*24*7


oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/sign-in")

# ===== Password hashing and verify ===== #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash password
def hash_password(password: str):
    return pwd_context.hash(password)

# function to verify hashed password
def verify_password(user_password, db_password):
    return pwd_context.verify(user_password, db_password)


# ===== DB operations ===== #
# function to get user from DB
async def get_user(email: str):
    user_data = await Users.find_one({"email": email})

    # check_user exist with email
    if user_data:
        return user_data
    else:
        return False
    
# function to add user
async def add_user(user_data: register_user):
    # user_data = user_data.model_dump()                # convert pydantic model to python dict

    # hashing user's password before storing to DB
    user_data["password"] = hash_password(user_data.get("password", ""))

    result = await Users.insert_one(user_data)

    if result:
        return "success"
    else:
        return "failed"
    

# ===== jwt Token ===== #
# jwt Token creation 
def create_token(data: dict):
    payload = data.copy()

    expire = datetime.now() + timedelta(minutes=TOKEN_EXPIRES)    # token expiry time
    payload.update({"exp": expire})

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)    # create token

    return encoded_jwt

# verify jwt 
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])    # decode token

        # access email from decoded token
        email = payload.get("sub")

        # if no email found 
        if not email:
            return False
        else:
            return True

    except JWTError:
        print("JWT Error occured!")
        return None

# dependancy to check for token validation
def get_access(token: str = Depends(oauth2_schema)):
    token_valid = verify_token(token)

    if token_valid:
        return True
    else:
        return False