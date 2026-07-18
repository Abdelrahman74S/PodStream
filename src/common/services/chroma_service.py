import chromadb
from chromadb.utils import embedding_functions
from django.conf import settings

class ChromaService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
            cls._instance._openai_ef = None
            cls._instance._collection = None
            cls._instance._episodes_collection = None
            cls._instance._podcasts_collection = None
        return cls._instance

    @property
    def client(self):
        if self._client is None:
            self._client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT
            )
        return self._client

    @property
    def openai_ef(self):
        if self._openai_ef is None:
            self._openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name="text-embedding-3-small"
            )
        return self._openai_ef

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name="django_articles",
                embedding_function=self.openai_ef
            )
        return self._collection

    @property
    def episodes_collection(self):
        if self._episodes_collection is None:
            self._episodes_collection = self.client.get_or_create_collection(
                name="django_episodes",
                embedding_function=self.openai_ef
            )
        return self._episodes_collection

    @property
    def podcasts_collection(self):
        if self._podcasts_collection is None:
            self._podcasts_collection = self.client.get_or_create_collection(
                name="django_podcasts",
                embedding_function=self.openai_ef
            )
        return self._podcasts_collection

chroma_service = ChromaService()