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
├── app.py          # Streamlit UI — split-panel layout
├── ingest.py       # PDF/DOCX/image → chunks → ChromaDB + Obsidian notes
├── query.py        # Retrieval + LLM router (local vs cloud)
├── graph.py        # pyvis graph builder from Obsidian vault
├── vault/          # Obsidian .md files (auto-generated on ingest)
├── chroma_db/      # Persistent vector store
└── .env            # API keys and model config (see setup below)
```

---

## 🛠️ Tech Stack

| Component | Library | Purpose |
|---|---|---|
| PDF parsing | `pdfplumber` | Text extraction from PDFs |
| DOCX parsing | `python-docx` | Word document ingestion |
| Image OCR | `pytesseract` | Text from images and scanned docs |
| Vector store | `ChromaDB` | Local embeddings storage, no server needed |
| Embeddings | `nomic-embed-text` via Ollama | Local embedding model |
| Local LLM | Ollama (`llama3` / `mistral`) | On-device inference |
| Cloud LLM | Claude / OpenAI | Cloud fallback via env flag |
| Knowledge graph | `pyvis` | Interactive HTML graph in Streamlit |
| UI | `Streamlit` | Split-panel web interface |
| Notes | Obsidian `.md` files | Human-readable vault + graph view |

---

## ⚙️ Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/youruser/rag-brain.git
cd rag-brain
pip install -r requirements.txt
```

### 2. Install and start Ollama

```bash
# Install Ollama: https://ollama.com
ollama pull llama3
ollama pull nomic-embed-text
```

### 3. Configure environment

Create a `.env` file in the project root:

```env
# LLM mode: set to "true" to use cloud providers
USE_CLOUD=false

# Ollama config (local mode)
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

# Cloud providers (only needed if USE_CLOUD=true)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
CLOUD_PROVIDER=anthropic   # or "openai"

# Obsidian vault path (optional — defaults to ./vault)
VAULT_PATH=./vault
```

### 4. Run the app

```bash
streamlit run app.py
```

---

## 🚀 Usage

1. **Upload documents** using the left panel (PDF, DOCX, or image)
2. The ingestion pipeline will:
   - Extract and chunk the text
   - Generate embeddings and store them in ChromaDB
   - Write a `.md` note to the Obsidian vault
   - Detect shared concepts and create graph edges
3. **Ask a question** in the chat input
4. The query pipeline will retrieve the top-k relevant chunks and pass them to the LLM
5. The **brain graph** on the right updates live — nodes are documents, edges are shared concepts
6. Toggle **Local ↔ Cloud** in the bottom-left at any time

---

## 🔀 Local vs Cloud Mode

| | Local (Ollama) | Cloud (Claude / OpenAI) |
|---|---|---|
| Privacy | ✅ Fully local | ⚠️ Data leaves device |
| Cost | ✅ Free | 💲 Per-token billing |
| Speed | Depends on hardware | Fast |
| Best for | Sensitive data, demos offline | Production, higher quality |

Switch modes by setting `USE_CLOUD=true/false` in `.env`, or use the toggle in the UI.

---

## 📦 Requirements

```
streamlit
pdfplumber
python-docx
pytesseract
chromadb
pyvis
python-dotenv
ollama
anthropic
openai
Pillow
```

Install with:

```bash
pip install -r requirements.txt
```

You will also need [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed on your system for image ingestion.

---

## 🗺️ Roadmap

- [ ] Drag-and-drop bulk upload
- [ ] Chunk size tuning controls in the UI
- [ ] Export conversation history
- [ ] Obsidian vault sync via API
- [ ] Evaluation harness for retrieval quality

---

## 🤝 Contributing

Pull requests welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## 📄 License

MIT