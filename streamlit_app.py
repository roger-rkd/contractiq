"""
ContractIQ - Hugging Face Spaces Deployment
Single Space running both Streamlit UI and FastAPI backend
"""
import os
import time
import threading
import streamlit as st
import streamlit.components.v1 as components
import requests

# Configure for HuggingFace Spaces
os.environ.setdefault("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))

API_BASE = "http://127.0.0.1:8000"

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="ContractIQ - AI Contract Analysis",
    page_icon=None,
    layout="wide",
)


# ---------------------------------------------------------------------------
# API Helper
# ---------------------------------------------------------------------------
def call_api(question, top_k=4):
    """Call the /api/v1/ask endpoint and return the parsed result."""
    try:
        payload = {"question": question, "top_k": top_k}
        response = requests.post(f"{API_BASE}/api/v1/ask", json=payload, timeout=60)
        if response.status_code == 200:
            return {"success": True, **response.json()}
        elif response.status_code == 404:
            return {"success": False, "error": "No documents found. Please upload a contract first."}
        else:
            error_data = response.json()
            return {"success": False, "error": error_data.get("detail", "Unknown error")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def display_answer(question, result):
    """Render the answer and sources for a given result dict."""
    st.markdown(f"> {question}")

    if not result.get("success"):
        st.error(result.get("error", "An unknown error occurred."))
        return

    answer = result["answer"]
    if "INSUFFICIENT_INFORMATION" in answer:
        st.warning(answer)
    else:
        st.success(answer)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Latency", f"{result.get('latency_sec', 0):.2f}s")
    with col2:
        st.metric("Sources", len(result.get("sources", [])))

    sources = result.get("sources", [])
    if sources:
        st.markdown("---")
        st.markdown("**Sources**")
        for i, source in enumerate(sources, 1):
            with st.expander(f"Source {i} - {source['clause_title']}"):
                st.markdown(f"**Page:** {source['page_number']}")
                st.markdown(f"**File:** {source['source_file']}")


# ---------------------------------------------------------------------------
# FastAPI Background Server
# ---------------------------------------------------------------------------
def start_fastapi_server():
    """Start FastAPI server in background thread."""
    import uvicorn
    from app.main import app

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


def wait_for_api():
    """Wait for FastAPI server to be ready (up to 5 min for first-time model download)."""
    for _ in range(300):
        try:
            resp = requests.get(f"{API_BASE}/health", timeout=2)
            if resp.status_code == 200:
                return True
        except Exception:
            time.sleep(1)
    return False


# Start FastAPI in background thread (only once)
if "api_started" not in st.session_state:
    st.session_state.api_started = True
    api_thread = threading.Thread(target=start_fastapi_server, daemon=True)
    api_thread.start()
    with st.spinner("Starting ContractIQ API..."):
        if not wait_for_api():
            st.error("Failed to start API server. Please refresh the page.")
            st.stop()


# ---------------------------------------------------------------------------
# Session State Defaults
# ---------------------------------------------------------------------------
if "contract_uploaded" not in st.session_state:
    st.session_state.contract_uploaded = False
if "contract_filename" not in st.session_state:
    st.session_state.contract_filename = ""
if "last_question" not in st.session_state:
    st.session_state.last_question = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ---------------------------------------------------------------------------
# Custom CSS — Poppins font, white backgrounds, responsive
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* ---- Poppins font everywhere EXCEPT Material Icons ---- */
html, body, .stApp,
.stApp p, .stApp div, .stApp li, .stApp td, .stApp th,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stMarkdown, .stText,
button, input, textarea, select, label,
.stTabs [data-baseweb="tab"],
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    font-family: 'Poppins', sans-serif !important;
}

/* ---- Global: white background everywhere, no black ---- */
.stApp {
    background-color: #ffffff !important;
}
section[data-testid="stSidebar"] {
    background-color: #f8f9fa !important;
    padding: 1.5rem 1rem !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: #1f2937 !important;
}

/* Force all text to dark on white */
.stApp, .stApp p, .stApp li, .stApp label,
.stApp .stMarkdown, .stApp .stText {
    color: #1f2937 !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #111827 !important;
}

/* ---- Kill every dark/black background Streamlit adds ---- */
/* File uploader — enclosed in a visible box */
[data-testid="stFileUploader"] {
    background-color: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] label {
    background-color: #ffffff !important;
    color: #1f2937 !important;
}
[data-testid="stFileUploadDropzone"] {
    background-color: #f9fafb !important;
    border: 2px dashed #d1d5db !important;
    border-radius: 8px !important;
    padding: 24px !important;
}
[data-testid="stFileUploadDropzone"] * {
    color: #374151 !important;
}
[data-testid="stFileUploadDropzone"] small {
    color: #6b7280 !important;
    font-size: 0.85rem !important;
}
/* Uploaded file name — force fully visible */
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] a,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] div {
    color: #1f2937 !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #1f2937 !important;
}
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileSize"] {
    color: #6b7280 !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #6b7280 !important;
}
/* The delete/remove button icon */
[data-testid="stFileUploader"] button {
    opacity: 1 !important;
}

/* Buttons — keep primary blue, make others white */
button[kind="secondary"],
.stButton > button:not([kind="primary"]) {
    background-color: #ffffff !important;
    color: #374151 !important;
    border: 1px solid #d1d5db !important;
}
button[kind="secondary"]:hover,
.stButton > button:not([kind="primary"]):hover {
    background-color: #f3f4f6 !important;
    border-color: #9ca3af !important;
}

/* Expanders */
[data-testid="stExpander"],
[data-testid="stExpander"] > div {
    background-color: #ffffff !important;
    color: #1f2937 !important;
}
details, details > summary,
.streamlit-expanderHeader {
    background-color: #ffffff !important;
    color: #374151 !important;
}

/* Metrics */
[data-testid="stMetric"],
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    background-color: #ffffff !important;
    color: #1f2937 !important;
}
[data-testid="stMetricValue"] {
    color: #111827 !important;
    font-weight: 600 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #ffffff !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: #ffffff !important;
    color: #374151 !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    color: #2563eb !important;
    font-weight: 600 !important;
}

/* Text input */
.stTextInput > div > div {
    background-color: #ffffff !important;
    color: #1f2937 !important;
    border-color: #d1d5db !important;
}
.stTextInput input {
    color: #1f2937 !important;
    background-color: #ffffff !important;
}

/* Slider */
.stSlider label, .stSlider span {
    color: #374151 !important;
}

/* ---- Card / Box styling ---- */
.card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.card-muted {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}

/* ---- How-it-works flow step cards ---- */
.flow-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 16px 20px;
    min-width: 140px;
    flex: 1;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.flow-step .flow-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #2563eb;
    color: #fff;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 10px;
}
.flow-step .flow-title {
    font-weight: 600;
    color: #1f2937;
    font-size: 0.95rem;
    margin-bottom: 4px;
}
.flow-step .flow-desc {
    font-size: 0.82rem;
    color: #6b7280;
    max-width: 180px;
}
/* ---- Responsive ---- */
@media (max-width: 768px) {
    .flow-step {
        min-width: unset;
        width: 100%;
    }
    .card { padding: 16px; }
}

/* ---- Sidebar collapse/expand button ---- */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {
    background-color: #f8f9fa !important;
    border: 1px solid #d1d5db !important;
    border-radius: 6px !important;
    color: #374151 !important;
}
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapseButton"]:hover {
    background-color: #e5e7eb !important;
}
/* The icon inside the sidebar button */
[data-testid="collapsedControl"] span,
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarCollapse"] button {
    color: #374151 !important;
    -webkit-text-fill-color: #374151 !important;
}

/* ---- Sidebar spacing ---- */
section[data-testid="stSidebar"] .block-container {
    padding-top: 1rem !important;
}
section[data-testid="stSidebar"] hr {
    margin: 1rem 0 !important;
}

/* ---- Footer ---- */
.footer {
    text-align: center;
    color: #6b7280 !important;
    font-size: 0.85rem;
    padding: 1rem 0 0.5rem 0;
    line-height: 1.8;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px;
    margin-top: 8px;
}
.footer .tech-stack {
    font-size: 0.78rem;
    color: #9ca3af !important;
    margin-top: 2px;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page Title
# ---------------------------------------------------------------------------
st.markdown("# ContractIQ")
st.markdown("*Trustworthy AI contract analysis with citation-first answers*")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ContractIQ")
    st.caption(
        "AI-powered contract analysis with retrieval-augmented generation. "
        "Every answer cites specific clauses."
    )

    st.divider()

    st.markdown("**How It Works**")
    st.markdown("""
1. Upload a PDF contract
2. Wait for processing
3. Ask questions
4. Verify cited clauses
    """)

    st.divider()

    st.markdown("**Features**")
    st.markdown("""
- Citation enforcement
- Hallucination blocking
- Intent-aware retrieval
- Sub-clause chunking
- Production API
    """)


# ---------------------------------------------------------------------------
# Main Content — Two Tabs (API Docs moved to footer)
# ---------------------------------------------------------------------------
tab1, tab2 = st.tabs(["Upload Contract", "Ask Questions"])

# Handle tab switch request from upload page
if st.session_state.get("switch_to_ask"):
    st.session_state.switch_to_ask = False
    components.html(
        '<script>'
        'const tabs = window.parent.document.querySelectorAll("[data-baseweb=\\"tab\\"]");'
        'if (tabs.length >= 2) tabs[1].click();'
        '</script>',
        height=0,
    )


# ===== TAB 1: Upload Contract =====
with tab1:
    st.markdown("### Get Started")
    st.markdown(
        "Upload a contract PDF and start asking questions in seconds. "
        "Here's how it works:"
    )

    # Step-by-step flow using Streamlit columns
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="flow-step">'
            '<div class="flow-num">1</div>'
            '<div class="flow-title">You upload a PDF</div>'
            '<div class="flow-desc">Select any contract PDF from your device.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="flow-step">'
            '<div class="flow-num">2</div>'
            '<div class="flow-title">We process it</div>'
            '<div class="flow-desc">Text extraction, clause detection, and indexing.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="flow-step">'
            '<div class="flow-num">3</div>'
            '<div class="flow-title">You ask questions</div>'
            '<div class="flow-desc">Get cited answers from the contract text.</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a contract PDF for analysis",
    )

    if uploaded_file:
        with st.spinner("Processing contract..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{API_BASE}/api/v1/upload", files=files, timeout=120)

                if response.status_code == 201:
                    result = response.json()
                    st.session_state.contract_uploaded = True
                    st.session_state.contract_filename = result["filename"]

                    st.success("Contract uploaded successfully!")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Filename", result["filename"])
                    with col2:
                        st.metric("Chunks Created", result["chunks_created"])
                    with col3:
                        st.metric("Pages Processed", result["pages_processed"])

                    st.info("You can now ask questions about this contract in the **Ask Questions** tab.")
                    if st.button("Ask Questions Now →", type="primary"):
                        st.session_state.switch_to_ask = True
                        st.rerun()
                else:
                    error_data = response.json()
                    st.error(f"Upload failed: {error_data.get('detail', 'Unknown error')}")

            except Exception as e:
                st.error(f"Error: {str(e)}")


# ===== TAB 2: Ask Questions =====
with tab2:
    st.markdown("### Ask Questions")
    st.markdown(
        "Ask any question about your uploaded contract. "
        "Answers will cite specific clauses from the document."
    )

    # Contract status
    if st.session_state.contract_uploaded:
        st.success(f"Contract loaded: {st.session_state.contract_filename}")
    else:
        st.warning("No contract uploaded yet. Upload one in the **Upload Contract** tab.")

    # Question input — use session key so it can be cleared
    if "question_input" not in st.session_state:
        st.session_state.question_input = ""
    question = st.text_input(
        "Your question",
        value=st.session_state.question_input,
        placeholder="e.g., What are the termination conditions?",
        help="Ask a question about the uploaded contract",
        key="question_widget",
    )

    # Ask button + advanced options on one row
    btn_col, opt_col = st.columns([1, 3])
    with btn_col:
        ask_clicked = st.button("Ask", type="primary", use_container_width=True)
    with opt_col:
        with st.expander("Advanced Options"):
            top_k = st.slider(
                "Number of context chunks to retrieve",
                min_value=1,
                max_value=10,
                value=4,
                help="More chunks = more context but slower",
            )

    if ask_clicked and not question:
        st.warning("Please enter a question.")

    # ---- Determine which question to process ----
    trigger_question = None
    if ask_clicked and question:
        trigger_question = question

    # ---- Also check for example-button clicks (rendered below) ----
    if st.session_state.get("_example_trigger"):
        trigger_question = st.session_state._example_trigger
        st.session_state._example_trigger = None

    # ---- Process the triggered question ----
    if trigger_question:
        with st.spinner("Analyzing contract..."):
            result = call_api(trigger_question, top_k)
        st.session_state.last_question = trigger_question
        st.session_state.last_result = result
        st.session_state.question_input = ""
        st.rerun()

    # ---- Display the answer immediately below input ----
    if st.session_state.last_result is not None:
        st.divider()
        st.markdown("**Answer**")
        display_answer(st.session_state.last_question, st.session_state.last_result)

        st.caption("**Want to explore more?** Try one of these questions or type your own above.")

    # ---- Example / suggestion questions ----
    examples = [
        "What are the termination conditions?",
        "What law governs this agreement?",
        "How is personal data handled?",
        "What are the payment terms?",
    ]

    if st.session_state.last_result is None:
        st.divider()
        st.markdown("**Example Questions**")
        st.caption("Not sure what to ask? Click any question below to get an instant answer.")

    # 2-column layout, full question text
    ex_cols = st.columns(2)
    for i, example in enumerate(examples):
        with ex_cols[i % 2]:
            if st.button(example, key=f"example_{i}", use_container_width=True):
                st.session_state._example_trigger = example
                st.rerun()


# ---------------------------------------------------------------------------
# Footer — credit + API Docs collapsible
# ---------------------------------------------------------------------------
st.divider()
st.markdown(
    '<div class="footer">'
    'ContractIQ v1.0.0 · Built with ❤️ by Rohit Kumar Dubey'
    '<div class="tech-stack">FastAPI · Streamlit · ChromaDB · '
    'sentence-transformers · Groq LLM · pdfplumber</div>'
    '</div>',
    unsafe_allow_html=True,
)

with st.expander("API Documentation"):
    st.markdown("#### Endpoints")

    st.markdown("""
The FastAPI backend provides the following endpoints:

**Health Check**
```
GET /health
```
Returns API status and version.

**Upload Contract**
```
POST /api/v1/upload
```
**Body:** `multipart/form-data`
- `file`: PDF file (required)
- `description`: Optional description

**Response:**
```json
{
  "message": "Contract uploaded and processed successfully",
  "filename": "contract.pdf",
  "chunks_created": 45,
  "pages_processed": 12
}
```

**Ask Question**
```
POST /api/v1/ask
```
**Body:** `application/json`
```json
{
  "question": "What are the termination conditions?",
  "top_k": 4
}
```

**Response:**
```json
{
  "question": "What are the termination conditions?",
  "answer": "According to [Clause 4], the termination conditions are...",
  "sources": [
    {
      "clause_title": "TERMINATION",
      "page_number": 8,
      "source_file": "contract.pdf"
    }
  ],
  "latency_sec": 0.583
}
```
    """)

    st.markdown(
        "**Full API Documentation** -- Swagger UI at `/api/docs` and ReDoc at `/api/redoc` "
        "(available when running locally)."
    )

    st.divider()

    st.markdown("#### Error Handling")
    st.markdown("""
All errors return a consistent format:
```json
{
  "error": "ErrorType",
  "detail": "Detailed error message"
}
```
    """)

    st.markdown("#### Citation Format")
    st.markdown("""
Answers always follow citation-first format:
- **Valid:** "According to [Clause X], ..."
- **Refusal:** "INSUFFICIENT_INFORMATION: The contract does not specify this."
    """)
