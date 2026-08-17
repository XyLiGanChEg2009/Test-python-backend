from sanic import Sanic, json
from sqlalchemy import text

from db import Base 
from db.sessions import AsyncSessionsLocal, engine
from middlewares.sessions import add_session, close_session
from middlewares.auth import authenticate

from routes.auth import bp as auth_bp
from routes.protected import bp as protected_bp

app = Sanic("AuthTestApp")

app.register_middleware(add_session, "request")
app.register_middleware(authenticate, "request")
app.register_middleware(close_session, "response")

app.blueprint(auth_bp)
app.blueprint(protected_bp)

@app.before_server_start
async def init_db(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    

@app.route("/")
async def hello(request):
    return json({"message": "Sanic is work"})

@app.route("/ping")
async def ping(request):
    try:
        async with AsyncSessionsLocal() as session:
            await session.execute(text("SELECT 1"))
        return json({"status": "ok"})
    except Exception as e:
        return json({"status": "error", "detail": str(e)}, status=500)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)