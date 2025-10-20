# 🔎 SearchSynth: A Streamlit + Groq App for Web & Research Summaries

SearchSynth is a lightweight **Streamlit web application** that combines
**web search (DuckDuckGo)**, **encyclopedic context (Wikipedia)**, and
**academic research (arXiv)**, then synthesizes a concise summary using
**Groq LLMs**.

This project is intentionally **agent-free**: no fragile LangChain
`initialize_agent` or `create_react_agent` APIs. Instead, it directly
calls the sources and lets Groq handle the synthesis. This avoids common
version mismatch errors and keeps the app reliable across environments.

------------------------------------------------------------------------

## ✨ Features

-   🔍 **DuckDuckGo search** (top 3--5 results for breadth)
-   📘 **Wikipedia snippet** (concise background context)
-   📄 **arXiv search** (latest research paper abstracts/summaries)
-   🧠 **Groq LLM synthesis** (Llama-3.1-8B-Instant by default)
-   📊 **Interactive Streamlit UI** with expandable raw sources
-   🔒 **API key protected** (Groq API key required via sidebar)

------------------------------------------------------------------------

## 🚀 Demo Flow

1.  User enters a query (e.g., *"Gareth Bale career summary"*).
2.  App queries:
    -   DuckDuckGo → top 3 results
    -   Wikipedia → \~600--800 character snippet
    -   arXiv → \~1200 character abstract snippet
3.  Results are shown in expandable sections.
4.  Evidence is passed to Groq LLM with a **structured prompt**:
    -   4--6 sentence summary
    -   Inline citations `[Wikipedia]`, `[arXiv]`, `[DDG]`
    -   No fabricated URLs
5.  Final synthesized answer is displayed in the chat window.

------------------------------------------------------------------------

## 🛠️ Installation

### 1. Clone this repository

``` bash
git clone https://github.com/YOUR-USERNAME/searchsynth.git
cd searchsynth
```

### 2. Create a virtual environment

``` bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

``` bash
pip install -U streamlit python-dotenv langchain-groq langchain-community duckduckgo-search>=6.1.5
```

### 4. Set up environment variables

Create a `.env` file in the project root:

``` env
GROQ_API_KEY=your_api_key_here
```

------------------------------------------------------------------------

## ▶️ Usage

Run the Streamlit app:

``` bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

------------------------------------------------------------------------

## 📂 Project Structure

    .
    ├── app.py         # Main Streamlit app
    ├── .env.example   # Example environment file
    ├── README.md      # Project documentation
    └── requirements.txt (optional)

------------------------------------------------------------------------

## 🧩 Customization

-   Change the Groq model in `synthesize_with_llm`:

    ``` python
    model_name="llama-3.1-70b-versatile"
    ```

-   Adjust max characters for Wikipedia or arXiv.

-   Swap or add other data sources.

------------------------------------------------------------------------

## 📜 License

MIT License. Free to use and modify.

------------------------------------------------------------------------

## 🙌 Acknowledgements

-   [Groq](https://groq.com/) for blazing fast inference
-   [LangChain Community](https://python.langchain.com/) for Wikipedia
    and arXiv wrappers
-   [duckduckgo-search](https://pypi.org/project/duckduckgo-search/) for
    robust DDG results
-   [Streamlit](https://streamlit.io/) for the interactive UI
