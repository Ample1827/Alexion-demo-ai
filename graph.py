from pathlib import Path
import re
from pyvis.network import Network


VAULT_DIR = Path("vault")


def build_graph() -> str:
    """Build a pyvis graph from Obsidian vault .md files. Returns HTML string."""
    net = Network(
        height="100%",
        width="100%",
        bgcolor="#0f1117",
        font_color="#e0e0e0",
        notebook=False,
    )
    net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=120)

    notes = list(VAULT_DIR.glob("*.md"))
    if not notes:
        return "<p style='color:gray;padding:1rem'>No documents ingested yet.</p>"

    keyword_docs: dict[str, list[str]] = {}

    for note in notes:
        doc_name = note.stem
        content = note.read_text(encoding="utf-8")

        # extract [[keywords]] links
        links = re.findall(r'\[\[(\w+)\]\]', content)

        net.add_node(
            doc_name,
            label=doc_name,
            color="#4f8ef7",
            size=25,
            title=f"{doc_name}",
            shape="dot",
        )

        for kw in links:
            if kw not in keyword_docs:
                keyword_docs[kw] = []
            keyword_docs[kw].append(doc_name)

    # add keyword nodes + edges
    for kw, docs in keyword_docs.items():
        if len(docs) >= 1:
            net.add_node(
                kw,
                label=kw,
                color="#f7a24f",
                size=12,
                title=f"{kw}",
                shape="diamond",
            )
            for doc in docs:
                net.add_edge(doc, kw, color="#444444", width=1)

    html = net.generate_html()
    return html