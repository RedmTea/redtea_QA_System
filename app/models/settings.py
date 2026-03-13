from sqlalchemy import Column, String, DateTime, Text, Float, Integer
from sqlalchemy.sql import func
from app.models.base import BaseModel


class Settings(BaseModel):
    __tablename__ = "settings"
    __repr_fields__ = ["id"]
    id = Column(String(32), primary_key=True, default="global")
    embedding_provider = Column(
        String(64), nullable=False, default="huggingface"
    )
    embedding_model_name = Column(String(256), nullable=False)
    embedding_base_url = Column(String(64), nullable=True)
    embedding_api_key = Column(String(64), nullable=True)

    llm_provider = Column(
        String(64), nullable=False, default="deepseek"
    )
    llm_model_name = Column(String(64), nullable=True)
    llm_base_url = Column(String(64), nullable=True)
    llm_api_key = Column(String(64), nullable=True)
    llm_temperature = Column(String(64), nullable=True, default="0.7")

    chat_system_prompt = Column(Text, nullable=True)
    rag_system_prompt = Column(Text, nullable=True)
    rag_query_prompt = Column(Text, nullable=True)

    retrieval_mode = Column(
        String(32),
        nullable=False,
        default="vector",
        comment="检索模型：vector(向量检索) keyword(关键字检索) hybird(混合检索)",
    )
    vector_threshold = Column(Float, nullable=True, default=0.2, comment="向量检索阈值")
    keyword_threshold = Column(
        Float, nullable=True, default=0.2, comment="关键字检索阈值"
    )
    vector_weight = Column(
        Float,
        nullable=True,
        default=0.5,
        comment="向量检索的权重(只会在混合检索的时候使用)",
    )
    top_k = Column(Integer, nullable=True, default=5, comment="返回结果的数量")
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
