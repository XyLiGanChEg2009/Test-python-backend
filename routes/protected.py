from sanic import Blueprint, json
from services.permissions import require_permission

bp = Blueprint("protected", url_prefix="/api")

@bp.route("/projects")
@require_permission("project", "view")
async def list_projects(request):
    return json([{"id": 1, "name": "Project Alpha"}, {"id": 2, "name": "Project Beta"}])