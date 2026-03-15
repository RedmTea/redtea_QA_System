from flask import Blueprint, render_template, request

from app.blueprints.utils import handle_api_error, success_response
from app.services.knowledgegraph_service import knowledgegraph_service
from app.utils.auth import login_required

bp = Blueprint("knowledgegraph", __name__)


@bp.route("/knowledgegraph")
@login_required
def index():
    return render_template("knowledgegraph.html")


@bp.route("/api/v1/knowledgegraph", methods=["GET"])
@login_required
@handle_api_error
def api_graph():
    limit = request.args.get("limit", type=int)
    keyword = request.args.get("q", default="", type=str)
    label = request.args.get("label", default="", type=str)
    result = knowledgegraph_service.search(keyword=keyword, label=label, limit=limit)
    return success_response(result)
