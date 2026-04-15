import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="RAG Brain",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🧠"
)

# ── Minimal dark style ──────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding: 1.5rem 2rem; }
    .stTextArea textarea { font-size: 0.95rem; }
    .source-chip {
        display: inline-block;
        background: #1e2a3a;
        color: #7eb3f5;
        border: 1px solid #2e4060;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 0.78rem;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ── Layout ───────────────────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

# ────────────────────────────────────────────────────────────────────
# LEFT PANEL — Input + Q&A
# ────────────────────────────────────────────────────────────────────
with left:
    st.markdown("## RAG Brain")
    st.caption("Upload documents · Ask questions · Watch the brain grow")

    # ── Document upload ──────────────────────────────────────────────
    st.markdown("### Ingest Documents")
    uploaded_files = st.file_uploader(
        "Drop PDFs, DOCX, images, or TXT",
        accept_multiple_files=True,
        type=["pdf", "docx", "png", "jpg", "jpeg", "txt"],
        label_visibility="collapsed",
    )

    if uploaded_files:
        if st.button("⚡ Ingest All", use_container_width=True, type="primary"):
            from ingest import ingest_file
            progress = st.progress(0)
            results = []
            for i, uf in enumerate(uploaded_files):
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=Path(uf.name).suffix
                ) as tmp:
                    tmp.write(uf.read())
                    tmp_path = tmp.name
                try:
                    with st.spinner(f"Processing {uf.name}..."):
                        result = ingest_file(tmp_path)
                        results.append(result)
                finally:
                    os.unlink(tmp_path)
                progress.progress((i + 1) / len(uploaded_files))

            st.success(f"Ingested {len(results)} document(s)")
            for r in results:
                with st.expander(f"📄 {r['doc_name']} — {r['chunks']} chunks"):
                    st.write("**Keywords:**", ", ".join(r["keywords"]))
                    st.write("**Note saved to:**", r["note_path"])
            st.rerun()  # refresh graph

    st.divider()

    # ── Query ────────────────────────────────────────────────────────
    st.markdown("### Ask Your Documents")

    # LLM mode toggle
    col1, col2 = st.columns([2, 1])
    with col1:
        query = st.text_area(
            "Your question",
            placeholder="What does the document say about...",
            height=100,
            label_visibility="collapsed",
        )
    with col2:
        mode = st.radio(
            "LLM",
            ["local", "cloud"],
            index=0,
            help="Local = Ollama · Cloud = Anthropic/OpenAI"
        )
        if mode == "cloud":
            provider = st.selectbox("Provider", ["anthropic", "openai"])
            os.environ["CLOUD_PROVIDER"] = provider

    if st.button(" Ask", use_container_width=True, type="primary", disabled=not query):
        from query import answer
        with st.spinner("Thinking..."):
            result = answer(query, mode=mode)

        st.markdown("#### Answer")
        st.markdown(result["answer"])

        if result["sources"]:
            st.markdown("#### Sources")
            for src in result["sources"]:
                score_pct = f"{src['score']*100:.0f}%"
                st.markdown(
                    f'<span class="source-chip">{src["source"]} · {score_pct}</span>',
                    unsafe_allow_html=True,
                )
                with st.expander("View chunk"):
                    st.write(src["text"])

    # ── Vault browser ────────────────────────────────────────────────
    st.divider()
    vault_notes = list(Path("vault").glob("*.md"))
    st.markdown(f"### Vault — {len(vault_notes)} notes")
    for note in vault_notes:
        with st.expander(f"{note.stem}"):
            st.code(note.read_text(encoding="utf-8"), language="markdown")

# ────────────────────────────────────────────────────────────────────
# RIGHT PANEL — Knowledge Graph
# ────────────────────────────────────────────────────────────────────
with right:
    st.markdown("### 🕸️ Knowledge Graph")
    st.caption("Blue = documents · Orange = concepts · Edges = shared keywords")

    from graph import build_graph
    graph_html = build_graph()

    if "<p " in graph_html:
        st.info("Upload and ingest documents to see the knowledge graph.")
    else:
        components.html(graph_html, height=680, scrolling=False)