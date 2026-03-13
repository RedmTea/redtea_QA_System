from app.models.settings import Settings
from app.services.base_service import BaseService
from app.config import Config


class SettingsService(BaseService[Settings]):
    def get(self):
        with self.session() as session:
            settings = session.query(Settings).filter_by(id="global").first()
            print("session.query settings", settings)
            if settings:
                return settings.to_dict()
            else:
                return self._get_default_settings()

    def _get_default_settings(self) -> dict:
        return {
            "id": "global",
            "embedding_provider": "huggingface",
            "embedding_model_name": "C:/Users/fei77/.cache/modelscope/hub/models/sentence-transformers/all-MiniLM-L6-v2",
            "embedding_api_key": "embedding_api_key",
            "embedding_base_url": "embedding_base_url",
            "llm_provider": "deepseek",
            "llm_model_name": Config.DEEPSEEK_CHAT_MODEL,
            "llm_api_key": Config.DEEPSEEK_API_KEY,
            "llm_base_url": Config.DEEPSEEK_BASE_URL,
            "llm_temperature": 0.7,
            "chat_system_prompt": "你是一个专业的AI助手。请友好、准确地回答用户的问题。",
            "rag_system_prompt": "你是一个专业的AI助手。请基于文档内容回答问题。",
            "rag_query_prompt": "文档内容：\n{context}\n\n问题：{question}\n\n请基于文档内容回答问题。如果文档中没有相关信息，请明确说明。",
            "retrieval_mode": "hybrid",
            "vector_threshold": 0.2,
            "keyword_threshold": 0.0,
            "vector_weight": 0.7,
            "top_k": 5,
        }

    def update(self, data):
        with self.transaction() as session:
            settings = session.query(Settings).filter_by(id="global").first()
            if not settings:
                settings = Settings(id="global")
                session.add(settings)
            for key, value in data.items():
                if hasattr(settings, key) and value is not None:
                    setattr(settings, key, value)
            session.flush()
            session.refresh(settings)
            return settings.to_dict()


settings_service = SettingsService()
