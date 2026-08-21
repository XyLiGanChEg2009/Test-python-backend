from sanic import Blueprint, json
from services.permissions import admin_only
from db.models import User, Role
from sqlalchemy import select
from sqlalchemy.orm import selectinload

bp = Blueprint("admin", url_prefix="/admin")

@bp.route("/users")
@admin_only
async def list_users(request):
    session = request.ctx.session
    stmt = select(User).options(selectinload(User.roles))
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    return json([{
        "id": u.id,
        "email": u.email,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "is_active": u.is_active,
        "roles": [{"id": r.id, "name": r.name, "codename": r.codename} for r in u.roles]
    } for u in users])

@bp.route("/users/<user_id:int>/roles", methods=["POST"])
@admin_only
async def assign_role(request, user_id):
    data = request.json
    role_codename = data.get("role_codename")
    if not role_codename:
        return json({"detail": "rolde_codename required"}, 400)
    
    session = request.ctx.session
    stmt = select(User).where(User.id == user_id). options(selectinload(User.roles))
    result = await session.execute(stmt)
    user: User = result.scalar_one_or_none()
    if not user:
        return json({"detail": "User not found"}, 404)
    
    role: Role = await session.execute(select(Role).where(Role.codename == role_codename))
    role = role.scalar_one_or_none()
    if not role:
        return json({"detail": "Role not found"}, status=404)
    
    if role not in user.roles:
        user.roles.append(role)
        await session.commit()
    
    return json({"detail": "Role assigned"})

@bp.route("/user/<user_id:int>/roles/<role_id:int>", methods=["DELETE"])
@admin_only
async def remove_role(request, user_id, role_id):
    session = request.ctx.session
    stmt = select(User).where(User.id == user_id). options(selectinload(User.roles))
    result = await session.execute(stmt)
    user: User = result.scalar_one_or_none()
    if not user:
        return json({"detail": "User not found"}, status=404)
    
    role: Role = await session.get(Role, role_id)
    if not role:
        return json({"detail": "Role not found"}, status=404)
    
    if role in user.roles:
        user.roles.remove(role)
        await session.commit()
    
    return json({"detail": "Role removed"})