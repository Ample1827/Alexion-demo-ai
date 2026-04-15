import os
import re
import uuid
import pdfplumber
import pytesseract
from docx import Document
from PIL import Image
from pathlib import Path
from dotenv import load_dotenv
import chromadb
import ollama

load_dotenv()

VAULT_DIR = Path("vault")
CHROMA_DIR = Path("chroma_db")
VAULT_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)

chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = chroma_client.get_or_create_collection("rag_brain")


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    elif ext == ".docx":
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        img = Image.open(path)
        return pytesseract.image_to_string(img)

    elif ext == ".txt":
        return path.read_text(encoding="utf-8")

    else:
        raise ValueError(f"Unsupported file type: {ext}")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return [c for c in chunks if len(c.strip()) > 50]


def get_embedding(text: str) -> list[float]:
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return response["embedding"]


def extract_keywords(text: str, n: int = 8) -> list[str]:
    """Simple keyword extraction — top N frequent non-stopwords."""
    stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
                 "for", "of", "with", "by", "from", "is", "was", "are", "were",
                 "be", "been", "have", "has", "had", "do", "does", "did", "that",
                 "this", "it", "as", "not", "we", "they", "he", "she", "you", "i"}
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    freq = {}
    for w in words:
        if w not in stopwords:
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq, key=freq.get, reverse=True)
    return sorted_words[:n]


def write_obsidian_note(doc_name: str, chunks: list[str], keywords: list[str]):
    """Write a .md file to the Obsidian vault."""
    safe_name = re.sub(r'[^\w\-_]', '_', doc_name)
    note_path = VAULT_DIR / f"{safe_name}.md"

    tag_line = " ".join(f"#{kw}" for kw in keywords)
    links = " ".join(f"[[{kw}]]" for kw in keywords)

    content = f"""# {doc_name}

**Tags:** {tag_line}
**Concepts:** {links}

---

## Chunks

"""
    for i, chunk in enumerate(chunks):
        content += f"### Chunk {i+1}\n{chunk}\n\n"

    note_path.write_text(content, encoding="utf-8")
    return str(note_path)


def ingest_file(file_path: str) -> dict:
    path = Path(file_path)
    doc_name = path.stem

    print(f"Extracting text from {path.name}...")
    text = extract_text(file_path)

    print(f"Chunking...")
    chunks = chunk_text(text)

    print(f"Extracting keywords...")
    keywords = extract_keywords(text)

    print(f"Embedding {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        doc_id = str(uuid.uuid4())
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"source": doc_name, "chunk_index": i, "keywords": ",".join(keywords)}]
        )

    print(f"Writing Obsidian note...")
    note_path = write_obsidian_note(doc_name, chunks, keywords)

    return {
        "doc_name": doc_name,
        "chunks": len(chunks),
        "keywords": keywords,
        "note_path": note_path,
    }