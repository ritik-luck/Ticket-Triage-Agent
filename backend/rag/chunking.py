from typing import List, Dict

def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start = end - overlap

    return chunks


def chunk_documents(documents: List[Dict[str, str]]) -> List[Dict[str, str]]:

    all_chunks = []

    for document in documents:
        source = document["source"]
        content = document["content"]

        chunks = split_text_into_chunks(content)

        for index, chunk_text in enumerate(chunks):
            all_chunks.append(
                {
                    "source": source,
                    "chunk_id": f"{source}_chunk_{index + 1}",
                    "text": chunk_text
                }
            )

    return all_chunks