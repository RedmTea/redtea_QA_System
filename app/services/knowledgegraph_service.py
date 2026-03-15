from __future__ import annotations

from typing import Any

from app.config import Config

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover
    GraphDatabase = None


class KnowledgeGraphService:
    SEARCH_QUERY = """
    MATCH (n)
    WHERE ($label = '' OR $label IN labels(n))
      AND (
        $keyword = ''
        OR any(prop_key IN keys(n) WHERE toLower(toString(n[prop_key])) CONTAINS $keyword)
        OR any(node_label IN labels(n) WHERE toLower(node_label) CONTAINS $keyword)
      )
    OPTIONAL MATCH (n)-[r]-(m)
    WITH n,
         count(DISTINCT r) AS relation_count,
         collect(DISTINCT CASE
           WHEN r IS NULL OR m IS NULL THEN NULL
           ELSE {
             id: id(r),
             type: type(r),
             direction: CASE
               WHEN id(startNode(r)) = id(n) THEN 'OUT'
               ELSE 'IN'
             END,
             other_id: id(m),
             other_labels: labels(m),
             other_properties: properties(m)
           }
         END)[0..8] AS raw_relations
    RETURN {
      id: id(n),
      labels: labels(n),
      properties: properties(n)
    } AS raw_node,
    relation_count,
    raw_relations
    ORDER BY relation_count DESC, id(n) DESC
    LIMIT $limit
    """

    COUNT_QUERY = """
    MATCH (n)
    WHERE ($label = '' OR $label IN labels(n))
      AND (
        $keyword = ''
        OR any(prop_key IN keys(n) WHERE toLower(toString(n[prop_key])) CONTAINS $keyword)
        OR any(node_label IN labels(n) WHERE toLower(node_label) CONTAINS $keyword)
      )
    RETURN count(n) AS total
    """

    LABEL_FACETS_QUERY = """
    MATCH (n)
    WHERE (
      $keyword = ''
      OR any(prop_key IN keys(n) WHERE toLower(toString(n[prop_key])) CONTAINS $keyword)
      OR any(node_label IN labels(n) WHERE toLower(node_label) CONTAINS $keyword)
    )
    UNWIND CASE
      WHEN size(labels(n)) = 0 THEN ['Node']
      ELSE labels(n)
    END AS label
    RETURN label, count(*) AS count
    ORDER BY count DESC, label ASC
    LIMIT 16
    """

    DISPLAY_KEYS = (
        "name",
        "title",
        "label",
        "display_name",
        "displayName",
        "caption",
        "code",
        "id",
    )

    PREVIEW_KEYS = (
        "description",
        "content",
        "summary",
        "text",
        "remark",
        "notes",
        "value",
        "type",
        "category",
        "status",
    )

    def _get_connection_config(self) -> dict[str, Any]:
        uri = Config.NEO4J_URI
        user = Config.NEO4J_USER
        password = Config.NEO4J_PASSWORD
        database = Config.NEO4J_DATABASE
        limit = Config.KNOWLEDGE_GRAPH_LIMIT

        if not uri or not user or not password:
            raise ValueError("Neo4j connection is not configured.")

        return {
            "uri": uri,
            "user": user,
            "password": password,
            "database": database,
            "limit": max(1, min(int(limit), 100)),
        }

    def _run_query(
        self,
        driver: Any,
        query: str,
        parameters: dict[str, Any],
        database: str,
    ) -> list[Any]:
        with driver.session(database=database or None) as session:
            return list(session.run(query, parameters))

    def _pick_display_name(
        self,
        properties: dict[str, Any],
        labels: list[str] | None,
        fallback_id: str,
    ) -> tuple[str, str]:
        labels = labels or []
        label = labels[0] if labels else "Node"

        for key in self.DISPLAY_KEYS:
            value = properties.get(key)
            if value not in (None, ""):
                return str(value), label

        return f"{label}:{fallback_id}", label

    def _build_preview(self, properties: dict[str, Any], display_name: str) -> str:
        for key in self.PREVIEW_KEYS:
            value = properties.get(key)
            if value not in (None, ""):
                return str(value)

        for key, value in properties.items():
            if key in self.DISPLAY_KEYS or value in (None, ""):
                continue
            return f"{key}: {value}"

        return display_name

    def _normalize_node(self, raw_node: dict[str, Any]) -> dict[str, Any]:
        properties = raw_node.get("properties") or {}
        labels = raw_node.get("labels") or []
        node_id = str(raw_node["id"])
        name, label = self._pick_display_name(properties, labels, node_id)

        return {
            "id": node_id,
            "labels": labels,
            "label": label,
            "name": name,
            "properties": properties,
            "preview": self._build_preview(properties, name),
        }

    def _normalize_relation(self, raw_relation: dict[str, Any]) -> dict[str, Any]:
        other_properties = raw_relation.get("other_properties") or {}
        other_labels = raw_relation.get("other_labels") or []
        other_id = str(raw_relation.get("other_id"))
        other_name, other_label = self._pick_display_name(
            other_properties,
            other_labels,
            other_id,
        )

        return {
            "id": str(raw_relation.get("id")),
            "type": raw_relation.get("type") or "RELATED",
            "direction": raw_relation.get("direction") or "OUT",
            "other_id": other_id,
            "other_label": other_label,
            "other_labels": other_labels,
            "other_name": other_name,
            "other_preview": self._build_preview(other_properties, other_name),
            "other_properties": other_properties,
        }

    def search(self, keyword: str = "", label: str = "", limit: int | None = None) -> dict[str, Any]:
        if GraphDatabase is None:
            raise RuntimeError("Neo4j driver is not installed. Run `uv sync` first.")

        config = self._get_connection_config()
        query_limit = max(1, min(int(limit or config["limit"]), 100))
        normalized_keyword = (keyword or "").strip().lower()
        normalized_label = (label or "").strip()
        parameters = {
            "keyword": normalized_keyword,
            "label": normalized_label,
            "limit": query_limit,
        }

        with GraphDatabase.driver(
            config["uri"],
            auth=(config["user"], config["password"]),
        ) as driver:
            driver.verify_connectivity()
            result_records = self._run_query(
                driver,
                self.SEARCH_QUERY,
                parameters,
                config["database"],
            )
            count_records = self._run_query(
                driver,
                self.COUNT_QUERY,
                parameters,
                config["database"],
            )
            facet_records = self._run_query(
                driver,
                self.LABEL_FACETS_QUERY,
                {"keyword": normalized_keyword},
                config["database"],
            )

        items: list[dict[str, Any]] = []
        for record in result_records:
            raw_node = record.get("raw_node")
            if not raw_node:
                continue

            node = self._normalize_node(raw_node)
            raw_relations = record.get("raw_relations") or []
            relations = [
                self._normalize_relation(raw_relation)
                for raw_relation in raw_relations
                if raw_relation
            ]

            items.append(
                {
                    **node,
                    "relation_count": int(record.get("relation_count") or 0),
                    "relations": relations,
                }
            )

        total = 0
        if count_records:
            total = int(count_records[0].get("total") or 0)

        labels = [
            {
                "label": record.get("label") or "Node",
                "count": int(record.get("count") or 0),
            }
            for record in facet_records
        ]

        return {
            "items": items,
            "labels": labels,
            "meta": {
                "total": total,
                "returned": len(items),
                "query": keyword or "",
                "label": normalized_label,
                "limit": query_limit,
                "database": config["database"],
                "uri": config["uri"],
            },
        }


knowledgegraph_service = KnowledgeGraphService()
