from __future__ import annotations

from typing import Any

from app.config import Config

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover
    GraphDatabase = None


class KnowledgeGraphService:
    GRAPH_QUERY = """
    MATCH (n)
    WITH n LIMIT $limit
    WITH collect(n) AS seed_nodes
    UNWIND seed_nodes AS n
    OPTIONAL MATCH (n)-[r]-(m)
    WHERE m IN seed_nodes
    RETURN
      collect(DISTINCT {
        id: id(n),
        labels: labels(n),
        properties: properties(n)
      }) AS raw_nodes,
      collect(DISTINCT CASE
        WHEN r IS NULL THEN NULL
        ELSE {
          id: id(r),
          source: id(startNode(r)),
          target: id(endNode(r)),
          type: type(r),
          properties: properties(r)
        }
      END) AS raw_edges
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

    def _get_connection_config(self) -> dict[str, Any]:
        uri = Config.NEO4J_URI
        user = Config.NEO4J_USER
        password = Config.NEO4J_PASSWORD
        database = Config.NEO4J_DATABASE
        limit = Config.KNOWLEDGE_GRAPH_LIMIT

        if not uri or not user or not password:
            raise ValueError("Neo4j 连接未配置，请先在 app/config.py 或环境变量中填写 URI、用户名和密码。")

        return {
            "uri": uri,
            "user": user,
            "password": password,
            "database": database,
            "limit": max(1, min(int(limit), 500)),
        }

    def _normalize_node(self, node: dict[str, Any]) -> dict[str, Any]:
        properties = node.get("properties") or {}
        labels = node.get("labels") or []
        label = labels[0] if labels else "Node"
        node_id = str(node["id"])

        name = None
        for key in self.DISPLAY_KEYS:
            if properties.get(key):
                name = str(properties[key])
                break

        if not name:
            name = f"{label}:{node_id}"

        return {
            "id": node_id,
            "labels": labels,
            "label": label,
            "name": name,
            "properties": properties,
        }

    def _normalize_edge(self, edge: dict[str, Any]) -> dict[str, Any]:
        return {
            **edge,
            "id": str(edge["id"]),
            "source": str(edge["source"]),
            "target": str(edge["target"]),
        }

    def get_graph(self, limit: int | None = None) -> dict[str, Any]:
        if GraphDatabase is None:
            raise RuntimeError("未安装 neo4j 驱动，请先执行 uv sync。")

        config = self._get_connection_config()
        query_limit = max(1, min(int(limit or config["limit"]), 500))

        with GraphDatabase.driver(
            config["uri"],
            auth=(config["user"], config["password"]),
        ) as driver:
            driver.verify_connectivity()
            records, _, _ = driver.execute_query(
                self.GRAPH_QUERY,
                {"limit": query_limit},
                database_=config["database"] or None,
            )

        record = records[0] if records else {"raw_nodes": [], "raw_edges": []}
        raw_nodes = record.get("raw_nodes") or []
        raw_edges = record.get("raw_edges") or []

        nodes_by_id = {
            node["id"]: self._normalize_node(node)
            for node in raw_nodes
            if node and node.get("id")
        }
        edges = [
            self._normalize_edge(edge)
            for edge in raw_edges
            if edge
            and str(edge.get("source")) in nodes_by_id
            and str(edge.get("target")) in nodes_by_id
        ]

        return {
            "nodes": list(nodes_by_id.values()),
            "edges": edges,
            "meta": {
                "node_count": len(nodes_by_id),
                "edge_count": len(edges),
                "limit": query_limit,
                "database": config["database"],
                "uri": config["uri"],
            },
        }


knowledgegraph_service = KnowledgeGraphService()
