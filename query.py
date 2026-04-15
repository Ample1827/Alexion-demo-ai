import os
from dotenv import load_dotenv
import ollama
import chromadb
from pathlib import Path

load_dotenv()

CHROMA_DIR = Path("chroma_db")
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = chroma_client.get_or_create_collection("rag_brain")


def get_embedding(text: str) -> list[float]:
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return response["embedding"]


def retrieve(query: str, n_results: int = 4) -> list[dict]:
    embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({"text": doc, "source": meta["source"], "score": 1 - dist})
    return chunks


def build_prompt(query: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[{c['source']}]\n{c['text']}" for c in chunks
    )
    return f"""You are a helpful research assistant. Use the context below to answer the question.
If the answer isn't in the context, say so honestly.

Context:
{context}

Question: {query}

Answer:"""


def ask_local(prompt: str) -> str:
    model = os.getenv("OLLAMA_MODEL", "llama3")
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


def ask_cloud(prompt: str) -> str:
    provider = os.getenv("CLOUD_PROVIDER", "anthropic")
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    else:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content


def answer(query: str, mode: str = "local") -> dict:
    chunks = retrieve(query)
    prompt = build_prompt(query, chunks)
    if mode == "local":
        response = ask_local(prompt)
    else:
        response = ask_cloud(prompt)
    return {"answer": response, "sources": chunks}