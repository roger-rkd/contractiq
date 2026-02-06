"""
ContractIQ - Hugging Face Spaces Deployment
Single Space running both Streamlit UI and FastAPI backend
"""
import os
import time
import threading
import streamlit as st
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
# SVG Icon System (Feather-style icons, inline SVG)
# ---------------------------------------------------------------------------
_SVG_TPL = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="__SZ__" height="__SZ__" '
    'viewBox="0 0 24 24" fill="__FILL__" stroke="__CLR__" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round">__PATH__</svg>'
)

_ICON_PATHS = {
    "file-text": (
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        '<polyline points="14 2 14 8 20 8"/>'
        '<line x1="16" y1="13" x2="8" y2="13"/>'
        '<line x1="16" y1="17" x2="8" y2="17"/>'
        '<line x1="10" y1="9" x2="8" y2="9"/>'
    ),
    "upload-cloud": (
        '<polyline points="16 16 12 12 8 16"/>'
        '<line x1="12" y1="12" x2="12" y2="21"/>'
        '<path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>'
        '<polyline points="16 16 12 12 8 16"/>'
    ),
    "message-circle": (
        '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 '
        '8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 '
        '8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>'
    ),
    "book-open": (
        '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>'
        '<path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>'
    ),
    "check-circle": (
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
        '<polyline points="22 4 12 14.01 9 11.01"/>'
    ),
    "x-circle": (
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="15" y1="9" x2="9" y2="15"/>'
        '<line x1="9" y1="9" x2="15" y2="15"/>'
    ),
    "alert-triangle": (
        '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 '
        '1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/>'
        '<line x1="12" y1="17" x2="12.01" y2="17"/>'
    ),
    "info": (
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="12" y1="16" x2="12" y2="12"/>'
        '<line x1="12" y1="8" x2="12.01" y2="8"/>'
    ),
    "search": (
        '<circle cx="11" cy="11" r="8"/>'
        '<line x1="21" y1="21" x2="16.65" y2="16.65"/>'
    ),
    "sliders": (
        '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/>'
        '<line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/>'
        '<line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/>'
        '<line x1="1" y1="14" x2="7" y2="14"/>'
        '<line x1="9" y1="8" x2="15" y2="8"/>'
        '<line x1="17" y1="16" x2="23" y2="16"/>'
    ),
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "clock": (
        '<circle cx="12" cy="12" r="10"/>'
        '<polyline points="12 6 12 12 16 14"/>'
    ),
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "help-circle": (
        '<circle cx="12" cy="12" r="10"/>'
        '<path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>'
        '<line x1="12" y1="17" x2="12.01" y2="17"/>'
    ),
    "code": (
        '<polyline points="16 18 22 12 16 6"/>'
        '<polyline points="8 6 2 12 8 18"/>'
    ),
    "layers": (
        '<polygon points="12 2 2 7 12 12 22 7 12 2"/>'
        '<polyline points="2 17 12 22 22 17"/>'
        '<polyline points="2 12 12 17 22 12"/>'
    ),
    "target": (
        '<circle cx="12" cy="12" r="10"/>'
        '<circle cx="12" cy="12" r="6"/>'
        '<circle cx="12" cy="12" r="2"/>'
    ),
    "heart": '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>',
    "arrow-right": (
        '<line x1="5" y1="12" x2="19" y2="12"/>'
        '<polyline points="12 5 19 12 12 19"/>'
    ),
    "hash": (
        '<line x1="4" y1="9" x2="20" y2="9"/>'
        '<line x1="4" y1="15" x2="20" y2="15"/>'
        '<line x1="10" y1="3" x2="8" y2="21"/>'
        '<line x1="16" y1="3" x2="14" y2="21"/>'
    ),
    "chevron-down": '<polyline points="6 9 12 15 18 9"/>',
    "arrow-down": (
        '<line x1="12" y1="5" x2="12" y2="19"/>'
        '<polyline points="19 12 12 19 5 12"/>'
    ),
}


def svg(name, size=20, color="#555", fill="none"):
    """Return inline SVG HTML for the named icon."""
    path = _ICON_PATHS.get(name, "")
    return (
        _SVG_TPL
        .replace("__SZ__", str(size))
        .replace("__CLR__", color)
        .replace("__FILL__", fill)
        .replace("__PATH__", path)
    )


def section_header(icon_name, text, size=22, color="#1f2937"):
    """Return HTML for a section header with an SVG icon."""
    return (
        f'<div class="section-header">'
        f'{svg(icon_name, size=size, color=color)}'
        f'<span>{text}</span>'
        f'</div>'
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
    st.markdown(
        f'<div class="card" style="border-left:4px solid #2563eb;">'
        f'<div style="padding:4px 0;color:#374151;font-style:italic;margin-bottom:8px;">'
        f'{svg("message-circle", size=16, color="#2563eb")} {question}</div></div>',
        unsafe_allow_html=True,
    )

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
        st.markdown(section_header("book-open", "Sources"), unsafe_allow_html=True)
        for i, source in enumerate(sources, 1):
            with st.expander(f"Source {i}: {source['clause_title']}"):
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

/* ---- Poppins font everywhere ---- */
html, body, .stApp, .stApp *,
[class*="st-"], .stMarkdown, .stText,
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
}
section[data-testid="stSidebar"] * {
    color: #1f2937 !important;
}

/* Force all text to dark on white */
.stApp, .stApp p, .stApp span, .stApp li, .stApp label,
.stApp .stMarkdown, .stApp .stText {
    color: #1f2937 !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #111827 !important;
}

/* ---- Kill every dark/black background Streamlit adds ---- */
/* File uploader */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] label {
    background-color: #ffffff !important;
    color: #1f2937 !important;
}
[data-testid="stFileUploadDropzone"],
[data-testid="stFileUploadDropzone"] * {
    background-color: #f9fafb !important;
    color: #374151 !important;
    border-color: #d1d5db !important;
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

/* ---- Section headers with SVG icons ---- */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
    margin: 1rem 0 0.5rem 0;
}
.section-header svg {
    flex-shrink: 0;
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

/* ---- How-it-works flow (horizontal arrow steps) ---- */
.flow-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin: 1.5rem 0;
    flex-wrap: wrap;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 24px 16px;
}
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
.flow-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 8px;
    align-self: center;
}
.flow-arrow svg {
    flex-shrink: 0;
}
/* Hide the arrow-down variant on desktop, show on mobile */
.flow-arrow .arrow-down-mobile { display: none; }
.flow-arrow .arrow-right-desktop { display: inline; }

/* ---- Responsive ---- */
@media (max-width: 768px) {
    .flow-row {
        flex-direction: column;
        gap: 8px;
        padding: 16px 12px;
    }
    .flow-step {
        min-width: unset;
        width: 100%;
    }
    .flow-arrow .arrow-right-desktop { display: none; }
    .flow-arrow .arrow-down-mobile { display: inline; }
    .section-header {
        font-size: 1.1rem;
    }
    .card { padding: 16px; }
}

/* ---- Feature list items in sidebar ---- */
.feature-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 3px 0;
    font-size: 0.92rem;
    color: #1f2937;
}

/* ---- Contract status badge ---- */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.88rem;
    font-weight: 500;
    margin-bottom: 12px;
}
.status-badge.loaded {
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
}
.status-badge.empty {
    background: #fef3c7;
    color: #92400e;
    border: 1px solid #fde68a;
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

/* ---- Ask-another prompt ---- */
.ask-another {
    text-align: center;
    padding: 18px 0 8px 0;
    color: #6b7280;
    font-size: 0.92rem;
}
.ask-another strong {
    color: #374151;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page Title
# ---------------------------------------------------------------------------
st.markdown(
    f'<h1 style="display:flex;align-items:center;gap:12px;">'
    f'{svg("file-text", size=32, color="#2563eb")} ContractIQ'
    f'</h1>',
    unsafe_allow_html=True,
)
st.markdown("*Trustworthy AI contract analysis with citation-first answers*")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(section_header("info", "About"), unsafe_allow_html=True)
    st.markdown(
        "**ContractIQ** analyzes legal contracts using retrieval-augmented generation. "
        "Every answer cites specific clauses, and the system refuses to answer "
        "when information is not in the contract."
    )

    st.divider()

    st.markdown(section_header("book-open", "How It Works"), unsafe_allow_html=True)
    st.markdown("""
1. **Upload** a PDF contract
2. **Wait** for automatic processing
3. **Ask** questions about the contract
4. **Verify** the cited clauses in each answer
    """)

    st.divider()

    st.markdown(section_header("shield", "Features"), unsafe_allow_html=True)
    features = [
        "Citation enforcement",
        "Hallucination blocking",
        "Intent-aware retrieval",
        "Sub-clause chunking",
        "Production API",
    ]
    for feat in features:
        st.markdown(
            f'<div class="feature-item">{svg("check-circle", size=16, color="#16a34a")} {feat}</div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Main Content — Two Tabs (API Docs moved to footer)
# ---------------------------------------------------------------------------
tab1, tab2 = st.tabs(["Upload Contract", "Ask Questions"])


# ===== TAB 1: Upload Contract =====
with tab1:
    st.markdown(section_header("upload-cloud", "Get Started"), unsafe_allow_html=True)
    st.markdown(
        '<div class="card-muted" style="margin-top:8px;">'
        '<p style="margin:0 0 4px 0;">Upload a contract PDF and start asking questions in seconds. '
        "Here's how it works:</p></div>",
        unsafe_allow_html=True,
    )

    # Horizontal arrow-connected flow
    st.markdown(f"""
    <div class="flow-row">
        <div class="flow-step">
            <div class="flow-num">1</div>
            <div style="margin-bottom:6px;">{svg("upload-cloud", size=28, color="#2563eb")}</div>
            <div class="flow-title">You upload a PDF</div>
            <div class="flow-desc">Select any contract PDF from your device.</div>
        </div>
        <div class="flow-arrow"><span class="arrow-right-desktop">{svg("arrow-right", size=24, color="#9ca3af")}</span><span class="arrow-down-mobile">{svg("arrow-down", size=24, color="#9ca3af")}</span></div>
        <div class="flow-step">
            <div class="flow-num">2</div>
            <div style="margin-bottom:6px;">{svg("clock", size=28, color="#2563eb")}</div>
            <div class="flow-title">We process it</div>
            <div class="flow-desc">Text extraction, clause detection, and indexing happen automatically.</div>
        </div>
        <div class="flow-arrow"><span class="arrow-right-desktop">{svg("arrow-right", size=24, color="#9ca3af")}</span><span class="arrow-down-mobile">{svg("arrow-down", size=24, color="#9ca3af")}</span></div>
        <div class="flow-step">
            <div class="flow-num">3</div>
            <div style="margin-bottom:6px;">{svg("message-circle", size=28, color="#2563eb")}</div>
            <div class="flow-title">You ask questions</div>
            <div class="flow-desc">Get cited answers grounded in the actual contract text.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
                else:
                    error_data = response.json()
                    st.error(f"Upload failed: {error_data.get('detail', 'Unknown error')}")

            except Exception as e:
                st.error(f"Error: {str(e)}")


# ===== TAB 2: Ask Questions =====
with tab2:
    st.markdown(section_header("message-circle", "Ask Questions"), unsafe_allow_html=True)
    # Contract status + description card
    if st.session_state.contract_uploaded:
        status_html = (
            f'<div class="status-badge loaded">'
            f'{svg("check-circle", size=16, color="#065f46")} '
            f'Contract loaded: {st.session_state.contract_filename}</div>'
        )
    else:
        status_html = (
            f'<div class="status-badge empty">'
            f'{svg("alert-triangle", size=16, color="#92400e")} '
            f'No contract uploaded yet. Upload one in the Upload Contract tab.</div>'
        )

    st.markdown(
        f'<div class="card">'
        f'<p style="margin:0 0 10px 0;">Ask any question about your uploaded contract. '
        f'Answers will cite specific clauses from the document.</p>'
        f'{status_html}</div>',
        unsafe_allow_html=True,
    )

    # Question input
    question = st.text_input(
        "Your question",
        placeholder="e.g., What are the termination conditions?",
        help="Ask a question about the uploaded contract",
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

    # ---- Display the answer immediately below input ----
    if st.session_state.last_result is not None:
        st.divider()
        st.markdown(section_header("zap", "Answer"), unsafe_allow_html=True)
        display_answer(st.session_state.last_question, st.session_state.last_result)

        # "Ask another question" prompt
        st.markdown(
            '<div class="ask-another"><strong>Want to explore more?</strong> '
            'Try one of these questions or type your own above.</div>',
            unsafe_allow_html=True,
        )

    # ---- Example / suggestion questions ----
    examples = [
        "What are the termination conditions?",
        "What law governs this agreement?",
        "How is personal data handled?",
        "What are the payment terms?",
        "What are the liability limits?",
    ]

    if st.session_state.last_result is None:
        st.divider()
        st.markdown(section_header("help-circle", "Example Questions"), unsafe_allow_html=True)
        st.markdown(
            '<div class="card-muted"><p style="margin:0;font-size:0.9rem;color:#6b7280;">'
            'Not sure what to ask? Click any question below to get an instant answer.</p></div>',
            unsafe_allow_html=True,
        )

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
    f'<div class="footer">'
    f'ContractIQ v1.0.0 &middot; Built with {svg("heart", size=14, color="#ef4444", fill="#ef4444")} by Rohit Kumar Dubey'
    f'<div class="tech-stack">FastAPI &middot; Streamlit &middot; ChromaDB &middot; '
    f'sentence-transformers &middot; Groq LLM &middot; pdfplumber</div>'
    f'</div>',
    unsafe_allow_html=True,
)

with st.expander("API Documentation"):
    st.markdown(section_header("hash", "Endpoints", size=20), unsafe_allow_html=True)

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

    st.markdown(section_header("shield", "Error Handling", size=20), unsafe_allow_html=True)
    st.markdown("""
All errors return a consistent format:
```json
{
  "error": "ErrorType",
  "detail": "Detailed error message"
}
```
    """)

    st.markdown(section_header("target", "Citation Format", size=20), unsafe_allow_html=True)
    st.markdown("""
Answers always follow citation-first format:
- **Valid:** "According to [Clause X], ..."
- **Refusal:** "INSUFFICIENT_INFORMATION: The contract does not specify this."
    """)
