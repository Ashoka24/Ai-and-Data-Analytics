from pathlib import Path

import streamlit as st

from src.rag_assistant import ResearchAssistant

PROJECT_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = PROJECT_DIR / "data" / "documents"

st.set_page_config(page_title="AI Research Assistant", page_icon="📚", layout="wide")
st.title("AI Research Assistant")
st.caption("Ask questions across your local TXT, Markdown and PDF documents. Answers include source references.")

with st.sidebar:
    st.header("Document collection")
    st.write("Add files to this folder:")
    st.code("ai-research-assistant-rag/data/documents/")
    st.write("Supported formats: TXT, Markdown and PDF")
    top_k = st.slider("Passages to retrieve", min_value=1, max_value=8, value=4)
    if st.button("Refresh document index", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()
    st.divider()
    st.caption("Local retrieval works without an API key. If OPENAI_API_KEY is set, answer generation uses the optional OpenAI integration.")

@st.cache_resource
def get_assistant() -> ResearchAssistant:
    return ResearchAssistant(DOCUMENTS_DIR)

assistant = get_assistant()
left, right = st.columns([3, 1])
with left:
    st.metric("Indexed passages", len(assistant.chunks))
with right:
    st.metric("Document collection", "Ready" if DOCUMENTS_DIR.exists() else "Missing")

if not assistant.chunks:
    st.warning("No readable documents found. Add TXT, Markdown or text-based PDF files, then refresh the index.")

question = st.text_area("Research question", placeholder="Example: What are the limitations of TF-IDF retrieval?", height=100)
if st.button("Search and answer", type="primary", disabled=not question.strip()):
    with st.spinner("Searching the local document collection..."):
        try:
            result = assistant.answer(question, top_k=top_k)
        except Exception as exc:
            st.error(f"Answer generation failed: {exc}")
            st.stop()
    st.subheader("Answer")
    st.caption(f"Answer mode: {result['mode']}")
    st.markdown(result["answer"])
    st.subheader("Retrieved source passages")
    if not result["sources"]:
        st.info("No relevant passages were found. Try a different query or add more source material.")
    for source in result["sources"]:
        with st.expander(f"[{source.source_id}] {source.source} · chunk {source.chunk_id}"):
            st.caption(f"TF-IDF relevance score: {source.score:.3f} (ranking signal, not confidence)")
            st.write(source.text)

st.divider()
st.caption("Use citations to return to the original document. This tool does not browse the web or verify whether a source is true.")
