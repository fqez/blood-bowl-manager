from fastapi import APIRouter, Body, Depends, HTTPException
from passlib.context import CryptContext

from auth.jwt_handler import sign_jwt
from database.database_dependencies import get_admin_database
from database.mongo_database import MongoDatabase
from models.user.admin import Admin
from schemas.admin import AdminData, AdminSignIn
from services import user_operations

router = APIRouter()

hash_helper = CryptContext(schemes=["bcrypt"])


@router.post("/login")
async def admin_login(
    admin_credentials: AdminSignIn = Body(...),
):
    admin_exists = await Admin.find_one(Admin.email == admin_credentials.username)
    if admin_exists:
        password = hash_helper.verify(admin_credentials.password, admin_exists.password)
        if password:
            return sign_jwt(admin_credentials.username)

        raise HTTPException(status_code=403, detail="Incorrect email or password")

    raise HTTPException(status_code=403, detail="Incorrect email or password")


@router.post("", response_model=AdminData)
async def admin_signup(
    admin: Admin = Body(...), db: MongoDatabase = Depends(get_admin_database)
):
    admin_exists = await Admin.find_one(Admin.email == admin.email)
    if admin_exists:
        raise HTTPException(
            status_code=409, detail="Admin with email supplied already exists"
        )

    admin.password = hash_helper.encrypt(admin.password)
    new_admin = await user_operations.add_admin(admin, db)
    return new_admin
