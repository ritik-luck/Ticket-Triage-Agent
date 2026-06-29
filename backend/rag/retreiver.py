from rag.embeddings import embedding_manager
from rag.vector_store import vector_store_manager


class Retriever:
    def __init__(self, top_k: int = 3):
        self.top_k = top_k

    def retrieve(self, query: str):
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        collection = vector_store_manager.get_collection()

        print("Generating query embedding...")
        query_embedding = embedding_manager.generate_embeddings([query])

        query_embedding = query_embedding.tolist()[0]

        print("Searching ChromaDB for relevant chunks...")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=self.top_k,
            include=["documents", "metadatas", "distances"]
        )

        retrieved_chunks = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for document, metadata, distance in zip(documents, metadatas, distances):
            score = self._convert_distance_to_score(distance)

            retrieved_chunks.append(
                {
                    "text": document,
                    "source": metadata.get("source", "unknown"),
                    "chunk_id": metadata.get("chunk_id", "unknown"),
                    "distance": distance,
                    "score": score
                }
            )

        sources = list(
            {
                chunk["source"]
                for chunk in retrieved_chunks
            }
        )

        best_score = retrieved_chunks[0]["score"] if retrieved_chunks else 0.0

        return {
            "retrieved_chunks": retrieved_chunks,
            "sources": sources,
            "best_score": best_score
        }

    def _convert_distance_to_score(self, distance: float) -> float:

        score = 1 / (1 + distance)
        return round(score, 4)


retriever = Retriever()
