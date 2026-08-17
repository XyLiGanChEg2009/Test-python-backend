import asyncio
from db.sessions import AsyncSessionsLocal
from db.models import User, Role, Resource
from services.auth import hash_password

async def seed():
    async with AsyncSessionsLocal() as session:
        admin_role = Role(name="Administrator", codename="admin")
        manager_role = Role(name="Manager", codename="manager")
        viewer_role = Role(name="Wiewer", codename="viewer")
        
        resources = []
        for codename, name in [("project", "Projects"), ("report", "Reports")]:
            for action in ["view", "create", "edit", "delete"]:
                resources.append(Resource(name=f"{name} {action}", codename=codename, action=action))
        
        admin_role.resources = resources
        manager_role.resources = [r for r in resources if r.action in ("view", "edit")]
        viewer_role.resources = [r for r in resources if r.action == "view"]
        
        users = [
            User(
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                patronymic="patronymic",
                password_hash=hash_password("admin123"),
                is_active=True,
                roles=[admin_role]
            ),
            User(
                email="manager@example.com",
                first_name="Manager",
                last_name="User",
                patronymic="patronymic",
                password_hash=hash_password("manager123"),
                is_active=True,
                roles=[manager_role]
            ),
            User(
                email="viewer@example.com",
                first_name="Viewer",
                last_name="User",
                patronymic="patronymic",
                password_hash=hash_password("viewer123"),
                is_active=True,
                roles=[viewer_role]
            ),
            User(
                email="inactive@example.com",
                first_name="Inactive",
                last_name="User",
                patronymic="patronymic",
                password_hash=hash_password("inactive123"),
                is_active=False,
                roles=[viewer_role]
            )
        ]
        session.add_all(users)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())
    print("Seed completed")
        