import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_DIR = Path(__file__).parent.parent
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    APP_HOST = os.environ.get("APP_HOST", "0.0.0.0")
    APP_PORT = os.environ.get("APP_PORT", 5000)
    APP_DEBUG = os.environ.get("APP_DEBUG", "false").lower() == "true"
    MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", 104857600))
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md"}
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
    MAX_IMAGE_SIZE = int(os.environ.get("MAX_IMAGE_SIZE", 5242880))

    LOG_DIR = os.environ.get("LOG_DIR", "./logs")
    LOG_FILE = os.environ.get("LOG_FILE", "rag_lite.log")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_ENABLE_FILE = os.environ.get("LOG_ENABLE_FILE", "true").lower() == "true"
    LOG_ENABLE_CONSOLE = os.environ.get("LOG_ENABLE_CONSOLE", "true").lower() == "true"

    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", 3306)
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "123456")
    DB_NAME = os.environ.get("DB_NAME", "rag")
    DB_CHARSET = os.environ.get("DB_CHARSET", "utf8mb4")

    STORAGE_TYPE = os.environ.get("STORAGE_TYPE", "local")
    STORAGE_DIR = os.environ.get("STORAGE_DIR", "./storages")

    MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "")
    MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "")
    MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "")
    MINIO_BUCKET_NAME = os.environ.get("MINIO_BUCKET_NAME", "rag-lite")
    MINIO_SECURE = os.environ.get("MINIO_SECURE", "false").lower() == "true"
    MINIO_REGION = os.environ.get("MINIO_REGION", None)

    DEEPSEEK_CHAT_MODEL = os.environ.get("DEEPSEEK_CHAT_MODEL", "deepseek-chat")
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    OPENAI_CHAT_MODEL = os.environ.get("OPENAI_CHAT_MODEL", DEEPSEEK_CHAT_MODEL)
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

    OLLAMA_CHAT_MODEL = os.environ.get("OLLAMA_CHAT_MODEL", "deepseek-chat")
    OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
    OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    VECTOR_DB_TYPE = os.environ.get("VECTOR_DB_TYPE", "chroma")
    CHROMA_PERSIST_DIRECTORY = os.environ.get("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    MILVUS_HOST = os.environ.get("MILVUS_HOST", "localhost")
    MILVUS_PORT = os.environ.get("MILVUS_PORT", "19530")

    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "123456")
    NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE", "")
    KNOWLEDGE_GRAPH_LIMIT = int(os.environ.get("KNOWLEDGE_GRAPH_LIMIT", 50))
