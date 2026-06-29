import logging
import warnings
from sentence_transformers import SentenceTransformer

warnings.filterwarnings(
    "ignore",
    message=".*unauthenticated requests to the HF Hub.*"
)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

class EmbeddingManager:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._load_model()

    def _load_model(self):
        try:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print(
                "Successfully loaded model with embedding dimension: "
                f"{self.model.get_embedding_dimension()}"
            )
        except Exception as e:
            print(f"Error loading embedding model: {e}")

    def generate_embeddings(self, texts: list[str]):
        if not self.model:
            raise ValueError(
                "Embedding model is not loaded. "
            )
        print(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"Generated embeddings shape: {embeddings.shape}")
        return embeddings


embedding_manager = EmbeddingManager()
