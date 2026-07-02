from pathlib import Path
import chromadb

from rag.document_loader import load_documents
from rag.chunking import chunk_documents
from rag.embeddings import embedding_manager


BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = BASE_DIR / "vector_db" / "chroma_db"
COLLECTION_NAME = "ticket_triage_knowledge_base"


class VectorStoreManager:

    def __init__(self):
        VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient( 
            path=str(VECTOR_DB_DIR)
        )

    def build_vector_store(self):
        print("Loading documents from knowledge_base folder...")

        documents = load_documents()

        if not documents:
            raise ValueError("No documents found in knowledge_base folder.")

        print(f"Loaded {len(documents)} document(s).")

        print("Splitting documents into chunks...")
        chunks = chunk_documents(documents)

        if not chunks:
            raise ValueError("No chunks created from documents.")

        print(f"Created {len(chunks)} chunk(s).")

        texts = [chunk["text"] for chunk in chunks]

        ids = [
            f"{chunk['source']}_{chunk['chunk_id']}_{index}"
            for index, chunk in enumerate(chunks)
        ]

        metadatas = [
            {
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"]
            }
            for chunk in chunks
        ]

        print("Generating embeddings for chunks...")
        embeddings = embedding_manager.generate_embeddings(texts)
        embeddings = embeddings.tolist()

        try:
            self.client.delete_collection(name=COLLECTION_NAME)
            print("Old collection deleted.")
        except Exception:
            print("No old collection found. Creating new collection.")

        collection = self.client.create_collection(
            name=COLLECTION_NAME
        )

        print("Adding chunks to ChromaDB collection in batches...")

        BATCH_SIZE = 5000

        for i in range(0, len(texts), BATCH_SIZE):
            batch_ids = ids[i:i + BATCH_SIZE]
            batch_texts = texts[i:i + BATCH_SIZE]
            batch_embeddings = embeddings[i:i + BATCH_SIZE]
            batch_metadatas = metadatas[i:i + BATCH_SIZE]

            collection.add(
                ids=batch_ids,
                documents=batch_texts,
                embeddings=batch_embeddings,
                metadatas=batch_metadatas
            )

            print(f"Batch {i // BATCH_SIZE + 1} added")

        print("ChromaDB vector store created successfully")

        return {
            "status": "success",
            "documents_count": len(documents),
            "chunks_count": len(chunks),
            "collection_name": COLLECTION_NAME,
            "vector_db_path": str(VECTOR_DB_DIR)
        }

    def get_collection(self):

        try:
            collection = self.client.get_collection(
                name=COLLECTION_NAME
            )

            return collection

        except Exception:
            raise ValueError(
                "ChromaDB collection not found. Please build vector store first"
            )


vector_store_manager = VectorStoreManager()



