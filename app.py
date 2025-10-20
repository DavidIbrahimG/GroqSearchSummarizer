import os
import json
import textwrap
import streamlit as st
from dotenv import load_dotenv

# Groq LLM (LangChain integration, light dependency)
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage  # works across LC versions

# Direct “tools” (no agent framework)
from duckduckgo_search import DDGS
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper


# ------------------------------------------------------
# Setup
# ------------------------------------------------------
load_dotenv()

st.set_page_config(page_title="🔎 Search + Groq", page_icon="🔎")
st.title("🔎 Search + Groq (no agents)")

st.write(
    "This app queries DuckDuckGo, Wikipedia, and arXiv directly, then asks a Groq model "
    "to synthesize a concise answer. No LangChain agents are used—so no version pin drama."
)

# Sidebar: API key
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your Groq API Key:", type="password")

# Chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi! Ask me about people, topics, or papers. I’ll search and summarize."}
    ]

for m in st.session_state["messages"]:
    st.chat_message(m["role"]).write(m["content"])


# ------------------------------------------------------
# Search helpers (no BaseTool / no agents)
# ------------------------------------------------------
def ddg_search(query: str, max_results: int = 5):
    """
    DuckDuckGo search using the requests backend (avoids curl_cffi + _imp issues).
    Returns a list of dicts: {title, href/link, body}
    """
    try:
        with DDGS(backend="requests", timeout=10) as ddgs:  # <— force requests backend
            results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception as e:
        return [{"title": "DuckDuckGo error", "href": "", "body": str(e)}]


def wiki_search(query: str, max_chars: int = 700):
    """Get a short snippet from Wikipedia for the query."""
    try:
        w = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=max_chars)
        return w.run(query)
    except Exception as e:
        return f"Wikipedia error: {e}"


def arxiv_search(query: str, max_chars: int = 1200):
    """Get a short summary from the most relevant arXiv paper(s) for the query."""
    try:
        a = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=max_chars)
        return a.run(query)
    except Exception as e:
        return f"arXiv error: {e}"


def synthesize_with_llm(api_key: str, question: str, evidence: str) -> str:
    """
    Ask Groq to write a concise answer given the gathered evidence.
    Uses ChatGroq, but avoids any agent APIs—just plain messages.
    """
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant",  # fast & available
        temperature=0,
        streaming=False,
    )
    system = SystemMessage(content=textwrap.dedent("""
        You are a precise research assistant. Use ONLY the provided evidence to answer.
        If the evidence is insufficient, say you don't know. Keep it to 4–6 sentences.
        Cite sources inline briefly (e.g., [Wikipedia], [arXiv], [DDG]). Do not fabricate URLs.
    """).strip())
    user = HumanMessage(content=f"Question:\n{question}\n\nEvidence:\n{evidence}")
    out = llm.invoke([system, user])
    return (out.content or "").strip()


# ------------------------------------------------------
# Chat input + run
# ------------------------------------------------------
user_input = st.chat_input(placeholder="Try: Gareth Bale career summary, or Ronaldo clubs.")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    if not api_key:
        msg = "Please enter your Groq API key in the sidebar."
        st.session_state["messages"].append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
        st.stop()

    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            ddg = ddg_search(user_input, max_results=5)
            wiki = wiki_search(user_input, max_chars=800)
            arxv = arxiv_search(user_input, max_chars=1200)

            # Optional: show raw sources
            with st.expander("🔎 DuckDuckGo (top results)"):
                # show a compact view
                st.write([{k: r.get(k) for k in ("title", "href", "body")} for r in ddg[:3]])
            with st.expander("📘 Wikipedia"):
                st.write(wiki)
            with st.expander("📄 arXiv"):
                st.write(arxv)

            # Build compact evidence string
            ddg_lines = []
            for r in ddg[:3]:
                title = r.get("title") or r.get("title_full") or ""
                href = r.get("href") or r.get("link") or ""
                body = r.get("body", "")
                ddg_lines.append(f"- {title} — {href}\n  {body[:240]}")

            evidence = (
                "== DuckDuckGo ==\n" + "\n".join(ddg_lines) + "\n\n"
                "== Wikipedia ==\n" + (wiki if isinstance(wiki, str) else json.dumps(wiki, ensure_ascii=False)) + "\n\n"
                "== arXiv ==\n" + (arxv if isinstance(arxv, str) else json.dumps(arxv, ensure_ascii=False))
            )

        with st.spinner("Synthesizing answer..."):
            try:
                final = synthesize_with_llm(api_key, user_input, evidence)
            except Exception as e:
                final = f"Sorry, something went wrong with the LLM: {e}"

        st.session_state["messages"].append({"role": "assistant", "content": final})
        st.write(final)
