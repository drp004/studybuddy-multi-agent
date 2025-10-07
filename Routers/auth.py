from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from database import *
from models import *
from utils import *

# ===== Auth Router ===== # 
auth = APIRouter(
        prefix="/auth",
        tags=["Authentication"]
    )


# ===== Routes ===== #
@auth.post("/sign-up")
async def register(user_data: register_user):
    user_data = user_data.model_dump()          # convert pydantic model to python dict

    # check user exist with same email
    db_user = await get_user(user_data.get("email"))
    if db_user:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User exist with {user_data.get('email')}")

    # create user 
    result = await add_user(user_data)

    # return status
    if result.lower() == "failed":
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not created!")
    
    # if user created then create & return access token
    access_token = create_token({"sub": user_data.get("email")})

    return {"access_token": access_token, "token_type": "bearer"}


@auth.post("/sign-in")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data.username will contain the email
    user_data = {
        "email": form_data.username,
        "password": form_data.password
    }
    
    db_user = await get_user(user_data.get("email"))

    if not db_user or not verify_password(user_data.get("password"), db_user.get("password")):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    
    access_token = create_token({"sub": user_data.get("email")})

    return {"access_token": access_token, "token_type": "bearer"}