from db.sessions import AsyncSessionsLocal

async def add_session(request):
    request.ctx.session = AsyncSessionsLocal()
    
async def close_session(request, response):
    await request.ctx.session.close()