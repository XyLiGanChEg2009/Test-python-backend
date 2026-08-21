from sanic import json
from db.models import User, Role, Resource
from sqlalchemy import select
from functools import wraps

def require_permission(resource_codename: str, action: str):
    def decorator(func):
        async def wrapper(request, *args, **kwargs):
            user = request.ctx.user
            async with request.ctx.session as session:
                stmt = (
                    select(Role)
                    .join(Role.resources)
                    .join(Role.users)
                    .where(
                        User.id == user.id,
                        Resource.codename == resource_codename,
                        Resource.action == action
                    )
                )
                result = await session.execute(stmt)
                role = result.scalar_one_or_none()
                if not role:
                    return json({"detail": "Forbidden"}, status=403)
                
                return await func(request, *args, **kwargs)
        return wrapper
    return decorator

def admin_only(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        user = request.ctx.user
        session = request.ctx.session
        stmt = (select(Role).join(Role.users).where(User.id == user.id, Role.codename == "admin"))
        result = await session.execute(stmt)
        admin_role = result.scalar_one_or_none()
        if not admin_role:
            return json({"detail": "Admin privileges required"}, status=403)
        
        return await func(request, *args, **kwargs)
    
    return wrapper
            