from sanic import json
import jwt
from config import SECRET_KEY, ALGORITHM
from db.models import User
from sqlalchemy import select

async def authenticate(request):
    print("Requset path: ", request.path)
    path = request.path.rstrip('/')
    if path in ["/auth/login", "/auth/register", "/auth/refresh", "/auth/logout", "/ping"]:
        return 
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return json({"detail": "Missing token"}, status=401)
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        if payload.get("type") != "access":
            raise jwt.InvalidTokenError
        
        session = request.ctx.session
        stmt = select(User).where(User.id == payload["user_id"], User.is_active == True)
        result = await session.execute(stmt)
        usr = result.scalar_one_or_none()
        if not usr:
            raise jwt.InvalidTokenError
        request.ctx.user = usr
    except Exception:
        return json({"details": "Invalid or expired token"}, status=401)