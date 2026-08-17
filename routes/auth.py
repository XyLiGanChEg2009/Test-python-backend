from sanic import Blueprint, json
from db.models import User
from sqlalchemy import Select
from services.auth import hash_password, generate_access_token

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

    access_token = generate_access_token(user.id)
    return json({"access_token": access_token}, status=401)

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