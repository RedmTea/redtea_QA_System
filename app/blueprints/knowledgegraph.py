from collections import Counter, defaultdict

from flask import Blueprint, render_template

from app.models.document import Document as DocumentModel
from app.models.knowledgebase import Knowledgebase
from app.utils.auth import get_current_user, login_required
from app.utils.db import db_session

bp = Blueprint("knowledgegraph", __name__)

STATUS_META = {
    "completed": {"label": "已完成", "tone": "success"},
    "processing": {"label": "处理中", "tone": "warning"},
    "pending": {"label": "待处理", "tone": "secondary"},
    "failed": {"label": "失败", "tone": "danger"},
}


@bp.route("/knowledgegraph")
@login_required
def index():
    current_user = get_current_user()

    with db_session() as session:
        knowledgebases = (
            session.query(Knowledgebase)
            .filter(Knowledgebase.user_id == current_user["id"])
            .order_by(Knowledgebase.updated_at.desc())
            .all()
        )

        kb_items = [kb.to_dict() for kb in knowledgebases]
        kb_ids = [kb["id"] for kb in kb_items]

        document_items = []
        if kb_ids:
            documents = (
                session.query(DocumentModel)
                .filter(DocumentModel.kb_id.in_(kb_ids))
                .order_by(DocumentModel.updated_at.desc())
                .all()
            )
            document_items = [doc.to_dict() for doc in documents]

    kb_name_map = {kb["id"]: kb["name"] for kb in kb_items}
    docs_by_kb = defaultdict(list)
    for doc in document_items:
        docs_by_kb[doc["kb_id"]].append(doc)

    status_counts = Counter(doc["status"] for doc in document_items)
    total_documents = len(document_items)
    completed_documents = status_counts.get("completed", 0)
    total_chunks = sum(doc.get("chunk_count") or 0 for doc in document_items)
    completion_rate = (
        round(completed_documents * 100 / total_documents) if total_documents else 0
    )

    kb_cards = []
    for kb in kb_items:
        kb_docs = docs_by_kb.get(kb["id"], [])
        preview_docs = []
        for doc in kb_docs[:4]:
            preview_docs.append(
                {
                    "name": doc["name"],
                    "status": doc["status"],
                    "status_label": STATUS_META.get(doc["status"], {}).get(
                        "label", doc["status"]
                    ),
                }
            )

        kb_cards.append(
            {
                "id": kb["id"],
                "name": kb["name"],
                "description": kb.get("description") or "暂无知识库描述",
                "cover_image": kb.get("cover_image"),
                "document_count": len(kb_docs),
                "chunk_count": sum(doc.get("chunk_count") or 0 for doc in kb_docs),
                "completed_count": sum(
                    1 for doc in kb_docs if doc.get("status") == "completed"
                ),
                "processing_count": sum(
                    1 for doc in kb_docs if doc.get("status") == "processing"
                ),
                "documents_preview": preview_docs,
            }
        )

    recent_documents = []
    for doc in document_items[:8]:
        meta = STATUS_META.get(doc["status"], {"label": doc["status"], "tone": "light"})
        recent_documents.append(
            {
                "id": doc["id"],
                "name": doc["name"],
                "kb_id": doc["kb_id"],
                "kb_name": kb_name_map.get(doc["kb_id"], "未知知识库"),
                "status": doc["status"],
                "status_label": meta["label"],
                "status_tone": meta["tone"],
                "chunk_count": doc.get("chunk_count") or 0,
                "file_type": (doc.get("file_type") or "").upper(),
                "updated_at": doc.get("updated_at"),
            }
        )

    status_cards = []
    for key in ["completed", "processing", "pending", "failed"]:
        meta = STATUS_META[key]
        status_cards.append(
            {
                "key": key,
                "label": meta["label"],
                "tone": meta["tone"],
                "count": status_counts.get(key, 0),
            }
        )

    summary_stats = [
        {
            "label": "知识库",
            "value": len(kb_items),
            "icon": "bi-diagram-3",
            "tone": "primary",
        },
        {
            "label": "文档节点",
            "value": total_documents,
            "icon": "bi-file-earmark-text",
            "tone": "success",
        },
        {
            "label": "已生成分块",
            "value": total_chunks,
            "icon": "bi-grid-3x3-gap",
            "tone": "info",
        },
        {
            "label": "完成率",
            "value": f"{completion_rate}%",
            "icon": "bi-activity",
            "tone": "warning",
        },
    ]

    return render_template(
        "knowledgegraph.html",
        summary_stats=summary_stats,
        kb_cards=kb_cards,
        recent_documents=recent_documents,
        status_cards=status_cards,
        total_knowledgebases=len(kb_items),
        total_documents=total_documents,
    )
