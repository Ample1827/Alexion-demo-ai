# 🧠 RAG Brain

A local-first RAG (Retrieval-Augmented Generation) demo that ingests documents, stores them as vector embeddings, surfaces them as an Obsidian knowledge graph, and lets you query them through a conversational UI — with a toggle to switch between a local LLM and a cloud provider.

Built as a technical demo for AstraZeneca's "intelligent search + conversational assistant" use case.

---

## ✨ Features

- 📄 **Multi-format ingestion** — PDF, DOCX, and images (via OCR)
- 🗂️ **Local vector store** — ChromaDB, no server required
- 🔗 **Obsidian integration** — every ingested document becomes a `.md` note; shared concepts create edges in the graph view
- 🧭 **Interactive knowledge graph** — force-directed graph powered by `pyvis`, rendered live in Streamlit
- 🔀 **Local / Cloud toggle** — switch between Ollama (local) and Claude / OpenAI (cloud) at runtime
- 💬 **Split-panel UI** — query input on the left, live brain graph on the right

---

## 🗂️ Project Structure

```
rag-brain/
├── app.py              # Streamlit UI — split-panel layout
├── ingest.py           # PDF/DOCX/image → chunks → ChromaDB + Obsidian notes
├── query.py            # Retrieval + LLM router (local vs cloud)
├── graph.py            # pyvis graph builder from Obsidian vault
├── vault/              # Obsidian .md files (auto-generated on ingest)
├── chroma_db/          # Persistent vector store
├── .env                # API keys and model config
└── pyproject.toml      # Project dependencies (managed by uv)
```

---

## 🛠️ Tech Stack

| Component | Library | Purpose |
|---|---|---|
| **Package manager** | `uv` | High-performance Python bundler |
| PDF parsing | `pdfplumber` | Text extraction from PDFs |
| DOCX parsing | `python-docx` | Word document ingestion |
| Image OCR | `pytesseract` | Text from images and scanned docs |
| Vector store | `ChromaDB` | Local embeddings storage |
| Embeddings | `nomic-embed-text` | Local embedding model via Ollama |
| Local LLM | Ollama (`gemma2` / `llama3`) | On-device inference |
| Cloud LLM | Claude / OpenAI | Cloud fallback via env flag |
| Knowledge graph | `pyvis` | Interactive HTML graph in Streamlit |
| UI | `Streamlit` | Split-panel web interface |

---

## ⚙️ Setup

### 1. Install `uv`

If you haven't already, install the fastest Python package manager:

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and initialize

```bash
git clone https://github.com/youruser/rag-brain.git
cd rag-brain

# Create virtual environment and install dependencies instantly
uv sync
```

### 3. Install and start Ollama

Ensure Ollama is running, then pull the required models:

```bash
ollama pull gemma2
ollama pull nomic-embed-text
```

### 4. Configure environment

Create a `.env` file in the project root:

```env
USE_CLOUD=false
OLLAMA_MODEL=gemma2
OLLAMA_BASE_URL=http://localhost:11434
ANTHROPIC_API_KEY=your_key_here
VAULT_PATH=./vault
```

### 5. Run the app

Use `uv run` to ensure you're using the correct environment:

```bash
uv run streamlit run app.py
```

---

## 🚀 Usage

1. **Upload documents** using the left panel (PDF, DOCX, or image).
2. The ingestion pipeline extracts text, generates embeddings, and writes an Obsidian-compatible `.md` note.
3. **Ask a question** in the chat input.
4. The **brain graph** on the right updates live — nodes represent documents, edges represent shared concepts.
5. **Toggle Local ↔ Cloud** to compare performance and accuracy.

---

## 🔀 Local vs Cloud Mode

| | Local (Ollama) | Cloud (Claude / OpenAI) |
|---|---|---|
| Privacy | ✅ Fully local | ⚠️ Data leaves device |
| Cost | ✅ Free | 💲 Per-token billing |
| Speed | Fast (on RTX GPU) | Fast |
| Model | `gemma2:9b` | `claude-sonnet-4-5` |

---

## 🤝 Contributing

Pull requests welcome. For major changes, open an issue first to discuss what you'd like to change.

---