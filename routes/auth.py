from sanic import Blueprint, json
from db.models import User
from sqlalchemy import Select
from services.auth import hash_password, generate_tokens, decode_token
from db.models.blacklisted_token import BlacklistedToken
import jwt
from datetime import datetime

bp = Blueprint("auth", url_prefix="/auth")

@bp.route("/register", methods=["POST"])
async def register(reqest):
    data = reqest.json
    
    if not data or not data.get("email") or not data.get("password") or not data.get("first_name") or not data.get("last_name"):
        return json({"detail": "missing required fields"}, status=400)
    
    if data.get("password") != data.get("password_confirm"):
        return json({"detail": "password do not match"}, status=400)
    
    session = reqest.ctx.session
    stmt = Select(User).where(User.email == data["email"])
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        return json({"detail": "Email already exists"}, status=400)
    
    hashed_password = hash_password(data["password"])
    user = User(
        email = data["email"], 
        first_name = data["first_name"], 
        last_name = data["last_name"], 
        patronymic = data["patronymic"], 
        password_hash = hashed_password, 
        is_active = True
    )
    
    session.add(user)
    
    await session.commit()
    
    return json({
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }, status=201)

@bp.route("/login", methods=["POST"])
async def login(request):
    data = request.json
    if not data or not data.get("email") or not data.get("password"):
        return json({"detail": "Email and password required"}, status=400)
    if not "@" in data.get("email"):
        return json({"detail": "incorrect email"}, status=400)
    print("Запрос пришел")
    
    session = request.ctx.session
    stmt = Select(User).where(User.email == data["email"], User.is_active == True)
    result = await session.execute(stmt)
    print("В базе обработался")
    user = result.scalar_one_or_none()
        
    if not user or not user.check_password(data["password"]):
        return json({"detail": "Invalid credentials"}, status=401)

    tokens = generate_tokens(user.id)
    return json({"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"]}, status=401)

@bp.route("/me")
async def me(request):
    usr = request.ctx.user
    return json({
        "id": usr.id,
        "email": usr.email,
        "first_name": usr.first_name,
        "last_name": usr.last_name,
        "patronymic": usr.patronymic,
        "is_active": usr.is_active
    })
    
@bp.route("/refresh", methods=["POST"])
async def refresh(request):
    data = request.json
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        return json({"detail": "Refresh token required"}, status=400)
    
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise jwt.InvalidTokenError
        
        session = request.ctx.session
        stmt = Select(BlacklistedToken).where(BlacklistedToken.token == refresh_token)
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            return json({"detail": "Token revoked"}, status=401)
        
        user_id = payload["user_id"]
        stmt = Select(User).where(User.id == user_id, User.is_active == True)
        user = await session.execute(stmt)
        if not user.scalar_one_or_none():
            return json({"detail": "User inactive"}, status=401)
        
        new_access = generate_tokens(user_id)["access_token"]
        return json({"access_token": new_access})
    
    except jwt.ExpiredSignatureError:
        return json({"detail": "Refresh token expired"}, status=401)
    except jwt.InvalidTokenError:
        return json({"detail": "Invalid refresh token"}, status=401)

@bp.route("/logout", methods=["POST"])
async def logout(request):
    data = request.json
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        return json({"detail": "Refresh token required"}, status=400)
    
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise jwt.InvalidTokenError
        
        expires_at = datetime.fromtimestamp(payload["exp"])
        session = request.ctx.session
        blacklisted = BlacklistedToken(token=refresh_token, expires_at=expires_at)
        session.add(blacklisted)
        await session.commit()
        return json({"detail": "Logged out"})
    
    except Exception:
        return json({"detail": "Invalid refresh token"}, status=400)