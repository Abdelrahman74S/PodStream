import chromadb
from chromadb.utils import embedding_functions
from django.conf import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
            cls._instance._text_splitter = None
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
    def text_splitter(self):
        if self._text_splitter is None:
            self._text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
            )
        return self._text_splitter

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name="django_collection",
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

    def sync_episode_transcript(self, episode):
        if not episode.transcript:
            return
        
        chunks = self.text_splitter.split_text(episode.transcript)
        if not chunks:
            return

        documents = chunks
        metadatas = [
            {
                "title": episode.title, 
                "django_id": str(episode.id),
                "podcast_id": str(episode.podcast.id),
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]
        ids = [f"episode_{episode.id}_chunk_{i}" for i in range(len(chunks))]

        try:
            self.episodes_collection.delete(where={"django_id": str(episode.id)})
        except Exception:
            pass

        self.episodes_collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def delete_episode_transcript(self, episode_id):
        try:
            self.episodes_collection.delete(where={"django_id": str(episode_id)})
        except Exception:
            self.episodes_collection.delete(ids=[f"episode_{episode_id}"])

chroma_service = ChromaService()