import streamlit as st
import re
import base64
import textwrap
from generator import GenerationError, generate_answer, source_records
from retriever import Retriever
from vector_store import VectorStore

# Page config
st.set_page_config(
    page_title="FAQ Assistant",
    page_icon=":material/account_balance:",
    initial_sidebar_state="expanded"
)


# Custom UI styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --forest: #064B36;
        --forest-dark: #033D2C;
        --forest-light: #126447;
        --mint: #EAF7F0;
        --mint-light: #F7FCF9;
        --text-dark: #17251F;
        --text-muted: #718078;
        --border: #DCEAE1;
    }

    /* Global application */
    html, body, [class*="css"] {
        font-family: 'Manrope', sans-serif;
    }

    .stApp {
        background: #F7FCF9;
        color: var(--text-dark);
    }

    /* Full-width dashboard workspace */
    [data-testid="stMain"] {
        background:
            radial-gradient(ellipse at 85% 10%, rgba(191, 229, 205, 0.23), transparent 38%),
            radial-gradient(ellipse at 50% 100%, rgba(207, 237, 217, 0.25), transparent 45%),
            linear-gradient(135deg, #F7FCF9 0%, #FFFFFF 52%, #F1F9F4 100%);
        position: relative;
        isolation: isolate;
    }

    /* Subtle silver rupee motifs across the workspace */
    [data-testid="stMain"]::before {
        content: "₹";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: -1;
        opacity: 0.035;
        color: #718A7B;
        font-size: 170px;
        font-weight: 800;
        background-image:
            radial-gradient(circle at 15% 18%, transparent 0 1px, transparent 2px),
            radial-gradient(circle at 75% 35%, transparent 0 1px, transparent 2px);
    }

    .block-container {
        max-width: 100%;
        padding: 3rem 3.2rem 3rem 3.2rem;
    }

    /* Main workspace typography */
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] h4 {
        color: #17251F;
        font-family: 'Manrope', sans-serif;
        font-weight: 700;
    }

    [data-testid="stMain"] p,
    [data-testid="stMain"] label,
    [data-testid="stMain"] li {
        color: #252D29;
        font-family: 'Manrope', sans-serif;
    }

    /* Premium forest-green sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #064B36 0%, #03432F 55%, #023B2B 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.09);
        min-width: 250px !important;
        max-width: 250px !important;
        width: 250px !important;
    }

    /* Keep the sidebar at a compact fixed width and hide its collapse controls. */
    [data-testid="stSidebar"] > div:first-child {
        width: 250px !important;
    }

    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebar"] button[kind="header"] {
        display: none !important;
    }

    [data-testid="stSidebar"] * {
        color: #F4F8F5;
        font-family: 'Manrope', sans-serif;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #DCEBE2;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #BFD6C8;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: rgba(255,255,255,0.055);
        border: 1px solid rgba(210,238,220,0.2);
        border-radius: 12px;
        margin-bottom: 12px;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(220,240,228,0.25);
    }

    /* Inputs */
    [data-testid="stTextInput"] input,
    [data-testid="stChatInput"] textarea {
        background: #FFFFFF !important;
        color: #20372A !important;
        border: 1px solid #DCE7DE !important;
        border-radius: 14px !important;
        font-family: 'Manrope', sans-serif !important;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stChatInput"] textarea:focus {
        border-color: #4D9870 !important;
        box-shadow: 0 0 0 2px rgba(77,152,112,0.12) !important;
    }

    /* Chat and response surfaces */
    [data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.88);
        border: 1px solid #E2ECE5;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 4px 18px rgba(23,65,42,0.035);
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    div[data-testid="stAlert"] p {
        color: #20372A !important;
    }

    /* Hero and section styling */
    .hero-card {
        background: linear-gradient(135deg, #F0FAF3, #FFFFFF);
        padding: 1.8rem;
        border: 1px solid #E0EEE4;
        border-radius: 22px;
        color: #17251F;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 28px rgba(24,79,49,0.045);
    }

    .hero-card h1 {
        color: #064B36 !important;
        font-size: 2.25rem;
        line-height: 1.25;
        letter-spacing: -0.045em;
    }

    .hero-card p {
        color: #596B60;
        font-size: 0.98rem;
        margin-bottom: 0;
    }

    .section-label {
        color: #61796A;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
    }

    /* Fund card and panel styling */
    .fund-card {
        background: #FFFFFF;
        border: 1px solid #DCEAE1;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 4px 16px rgba(20,75,43,0.035);
    }

    /* Welcome-page fund selection buttons: remove dark/black card styling */
    .st-key-fund_button_0 [data-testid="stButton"] button,
    .st-key-fund_button_1 [data-testid="stButton"] button,
    .st-key-fund_button_2 [data-testid="stButton"] button {
        background: #FFFFFF !important;
        color: #064B36 !important;
        border: 1px solid #B8D8C5 !important;
        border-radius: 16px !important;
        min-height: 76px;
        height: auto;
        white-space: normal;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(20,75,43,0.06) !important;
    }

    .st-key-fund_button_0 [data-testid="stButton"] button:hover,
    .st-key-fund_button_1 [data-testid="stButton"] button:hover,
    .st-key-fund_button_2 [data-testid="stButton"] button:hover {
        background: #E8F5EF !important;
        color: #064B36 !important;
        border-color: #78B796 !important;
    }

    .st-key-fund_button_0 [data-testid="stButton"] button[kind="primary"],
    .st-key-fund_button_1 [data-testid="stButton"] button[kind="primary"],
    .st-key-fund_button_2 [data-testid="stButton"] button[kind="primary"] {
        background: #0B6848 !important;
        color: #FFFFFF !important;
        border-color: #0B6848 !important;
    }

    .st-key-fund_button_0 [data-testid="stButton"] button[kind="primary"]:hover,
    .st-key-fund_button_1 [data-testid="stButton"] button[kind="primary"]:hover,
    .st-key-fund_button_2 [data-testid="stButton"] button[kind="primary"]:hover {
        background: #064B36 !important;
        color: #FFFFFF !important;
    }

    /* Smooth transitions */
    [data-testid="stExpander"],
    [data-testid="stAlert"] {
        border-radius: 14px;
    }

    /* Responsive layout */
    @media (max-width: 900px) {
        .block-container {
            padding: 1.4rem 1.2rem 2rem 1.2rem;
        }

        .hero-card h1 {
            font-size: 1.8rem;
        }
    }

    .st-key-related_questions_panel {
        background: #E8F5EF;
        border: 1px solid #CFE5D8;
        border-radius: 22px;
        padding: 18px 20px;
    }

    .st-key-related_questions_panel [data-testid="stMarkdownContainer"] p {
        color: #00543C;
        font-weight: 700;
        font-size: 1.15rem;
    }

    .st-key-related_questions_panel [data-testid="stButton"] button {
        background: #FFFFFF;
        color: #263B52;
        border: 1px solid #B5D9C8;
        border-radius: 16px;
        min-height: 82px;
        white-space: normal;
        font-size: 0.9rem;
    }

    /* How we got this answer panel */
    .st-key-how_answer_panel [data-testid="stExpander"] {
        background: #DCEFE4;
        border: 1px solid #9FCBB2;
        border-radius: 14px;
    }

    .st-key-how_answer_panel [data-testid="stExpander"] summary {
        color: #064B36 !important;
        font-weight: 700;
    }

    .st-key-how_answer_panel [data-testid="stMarkdownContainer"] {
        color: #263B32;
    }
</style>
""", unsafe_allow_html=True)



# Disclaimer
DISCLAIMER = "Facts-only. No investment advice."

# Fund selection and question configuration
FUND_OPTIONS = {
    "HDFC Large Cap Fund": {
        "main_question": "What is the expense ratio of HDFC Large Cap Fund Direct Growth?",
        "related_questions": [
            "Who is the fund manager of HDFC Large Cap Fund?",
            "What risk level is shown for HDFC Large Cap Fund?",
            "What is the investment objective of HDFC Large Cap Fund?"
        ]
    },
    "HDFC ELSS Tax Saver Fund": {
        "main_question": "What is the ELSS lock-in period for HDFC ELSS Tax Saver Fund?",
        "related_questions": [
            "Who is the fund manager of HDFC ELSS Tax Saver Fund?",
            "What risk level is shown for HDFC ELSS Tax Saver Fund?",
            "What is the investment objective of HDFC ELSS Tax Saver Fund?"
        ]
    },
    "HDFC Mid Cap Fund": {
        "main_question": "What is the minimum SIP for HDFC Mid Cap Fund Direct Growth?",
        "related_questions": [
            "Who is the fund manager of HDFC Mid Cap Fund?",
            "What risk level is shown for HDFC Mid Cap Fund?",
            "What is the investment objective of HDFC Mid Cap Fund?"
        ]
    }
}

# Load components
@st.cache_resource
def load_components(): 
    store = VectorStore()
    if store.collection.count() == 0:
        store.index_documents("data/embeddings/embeddings.json")


    retriever = Retriever()
    return retriever

def main():
        

    def queue_related_question(question):
        st.session_state["query_input"] = question
        st.session_state["run_related_query"] = True

    
    # Professional sidebar and main layout

    center = st.container()

    with st.sidebar:
        st.markdown("## FAQ Assistant")
        st.caption("Your mutual fund facts companion")

        st.divider()

        with st.expander(":material/info: About this project", expanded=False):
            st.markdown("""
            HDFC Mutual Fund FAQ Chatbot helps users find factual information
            about HDFC Mutual Fund schemes.

            It uses **Retrieval-Augmented Generation (RAG)** to search indexed
            sources and generate answers grounded in retrieved information.

            This is an independent project, not affiliated with HDFC Mutual Fund
            or Groww.
            """)

        with st.expander(":material/account_tree: How It Works", expanded=False):
            st.markdown("""
            **1. Understand the Query**

            The system processes your question to identify the information required.

            **2. Retrieve Relevant Information**

            It searches the indexed knowledge base and retrieves relevant information from available sources.

            **3. Generate a Factual Response**

            The AI generates an answer grounded in the retrieved information, with supporting source references.
            """)

        st.divider()

        st.markdown("### :material/shield: Disclaimer")
        st.caption(DISCLAIMER)
        st.caption("This assistant does not provide personalized investment advice.")


    with center:
        with open("Heading-small-logo.png", "rb") as logo_file:
            logo_base64 = base64.b64encode(logo_file.read()).decode("utf-8")
        st.markdown(
            f"""
            <div style="
                display:inline-flex;
                align-items:center;
                gap:10px;
                background:#E8F5EF;
                border:1px solid #D5EADF;
                border-radius:24px;
                padding:8px 16px;
                margin-bottom:22px;
                color:#00543C;
                font-family:'Manrope', sans-serif;
                font-size:19px;
                font-weight:700;
                width:fit-content;">
                <img src="data:image/png;base64,{logo_base64}"
                     style="width:27px;height:27px;object-fit:contain;">
                <span>FAQ Assistant</span>
            </div>
            """,
            unsafe_allow_html=True
        )


        with st.container():

            st.markdown(
                """


                <h1 style="
                    color:#064B36;
                    font-size:3.35rem;
                    font-weight:800;
                    line-height:1.22;
                    letter-spacing:-1.3px;
                    margin:0 0 15px 0;">
                    Your Mutual Fund Query<br>
                    <span style="color:#17251F;">Simplified.</span>
                </h1>

                <p style="
                    color:#718078;
                    font-size:1rem;
                    font-weight:500;
                    line-height:1.7;
                    margin-bottom:14px;">
                    Get accurate, factual information about
                    Mutual Fund schemes.
                </p>

                <div style="
                    width:54px;
                    height:4px;
                    background:#16845A;
                    border-radius:5px;
                    margin-bottom:18px;">
                </div>
                """,
                unsafe_allow_html=True
            )

    with center:
        # Fund selection
        def select_fund(fund_name):
            st.session_state["selected_fund"] = fund_name
            st.session_state["query_input"] = FUND_OPTIONS[fund_name]["main_question"]
            st.session_state["run_related_query"] = True

        if "selected_fund" not in st.session_state:
            st.session_state["selected_fund"] = None

        fund_cols = st.columns(3)

        for i, fund_name in enumerate(FUND_OPTIONS):
            with fund_cols[i]:
                st.button(
                    fund_name,
                    key=f"fund_button_{i}",
                    type="primary" if st.session_state["selected_fund"] == fund_name else "secondary",
                    use_container_width=True,
                    on_click=select_fund,
                    args=(fund_name,)
                )

        # Query input
        if "query_input" not in st.session_state:
            st.session_state["query_input"] = st.session_state.get("query", "")

        input_col, send_col = st.columns([6, 1], vertical_alignment="bottom")

        with input_col:
            query = st.text_input(
                "Ask your question",
                key="query_input",
                placeholder="Ask anything about HDFC Mutual Fund...",
                label_visibility="collapsed"
            )

        with send_col:
            ask_clicked = st.button(
                ":material/send:",
                type="primary",
                use_container_width=True
            )

        run_related_query = st.session_state.pop("run_related_query", False)

        if ask_clicked or run_related_query:
            if not query.strip():
                st.warning("Please enter a question.")
                return
            
            # Basic guardrails
            query_lower = query.lower()
            
            # Check for PII patterns (simple)
            if re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', query) or re.search(r'\b\d{12}\b', query) or re.search(r'\b[6-9]\d{9}\b', query):
                st.error("PII is not accepted. Please do not enter PAN, Aadhaar, or phone numbers.")
                return
            
            # Check for advice/opinion questions
            advice_keywords = ['should i', 'buy', 'sell', 'recommend', 'better for me', 'which fund should', 'portfolio', 'investment advice', 'investing in', 'give me advice', 'advise me', 'advice me', 'where should i invest', 'which fund is best for me', 'best fund for me']
            if any(keyword in query_lower for keyword in advice_keywords):
                st.warning("This is a facts-only assistant. I cannot provide investment advice.")
                st.info("For educational information about mutual funds, you can refer to SEBI/AMFI resources.")
                return
            
            # Check for performance/returns
            if any(keyword in query_lower for keyword in ['return', 'performance', 'compare', 'which is better']):
                st.warning("I cannot compute or compare returns. For performance data, please refer to the official factsheet.")
                retriever = load_components()
                results = retriever.retrieve("factsheet", top_k=1)
                if results:
                    st.markdown(f"[Check official factsheet]({results[0]['source_url']})")
                    return
            
            # Retrieve and answer
            retriever = load_components()
            results = retriever.retrieve(query, top_k=150, similarity_threshold=0.3)
            
            
            # Rerank and filter to keep context small for token limits
            def rerank_chunks(query_text, hits):
                ql = query_text.lower()
                scored = []
                for h in hits:
                    text = str(h.get('text','')).lower()
                    score = h.get('similarity', 0)
                    sid = str(h.get('source_id','')).lower()
                    source_name = str(h.get('source_name','')).lower()
                    # Prioritize by query type using query fund name and fact terms
                    if 'expense ratio' in ql:
                        fund_match = ('hdfc large cap' in ql and 'direct growth' in ql)
                        if 'expense ratio' in text and ('hdfc large cap' in text or 'hdfc large cap' in source_name):
                            score += 0.4
                        if fund_match and ('hdfc large cap' in text or 'hdfc large cap' in source_name) and 'expense ratio' in text:
                            score += 0.3
                        elif fund_match and ('hdfc large cap' in text or 'hdfc large cap' in source_name):
                            score += 0.2
                        elif 'expense ratio' in text:
                            score += 0.1
                    elif 'sip' in ql:
                        fund_match = ('hdfc mid cap' in ql and 'direct growth' in ql)
                        sip_terms = ['minimum sip', 'sip investment', 'sip amount', 'minimum sip investment']
                        has_sip = any(t in text for t in sip_terms) or ('sip' in text and 'minimum' in text)
                        if fund_match and has_sip and 'hdfc mid cap' in text:
                            score += 0.25
                        elif fund_match and has_sip:
                            score += 0.15
                        elif has_sip:
                            score += 0.1
                    elif 'elss' in ql and ('lock' in ql or 'lock-in' in ql or '3 year' in ql):
                        has_lock = ('lock' in text or 'lock-in' in text or '3 year' in text or 'three year' in text)
                        if has_lock and ('amfi' in sid or 'elss' in text):
                            score += 0.25
                        elif has_lock and 'elss' in text:
                            score += 0.15
                        elif has_lock:
                            score += 0.1
                    scored.append((score, h))
                scored.sort(key=lambda x: x[0], reverse=True)
                # Take top 5
                return [h for _, h in scored[:5]]
            
            results = rerank_chunks(query, results)
            print(f"Chunks sent to generator: {len(results)}")
            
            if not results:
                st.warning("I don't have enough information in my knowledge base to answer this question.")
                st.info("This assistant only has information from the 5 specified HDFC Mutual Fund pages on Groww. Please check the official factsheet for more details.")
                # Show AMC link as educational
                st.markdown("[HDFC Mutual Fund AMC Overview](https://groww.in/mutual-funds/amc/hdfc-mutual-funds)")
                return
            
            try:
                answer = generate_answer(query, results)
            except GenerationError as exc:
                print(f"Generation error: {type(exc).__name__}: {exc}")
                print(f"Underlying cause: {repr(exc.__cause__)}")
                st.error("Unable to generate an answer right now. Please try again later.")
                return
               

            st.markdown("### Answer:")
            st.write(answer)

            sources = source_records(results)
            

            if sources:
                primary_source = sources[0]

                st.html(
                    textwrap.dedent(
                        f"""
                        <div style="
                            display:flex;
                            align-items:center;
                            gap:14px;
                            margin:8px 0 12px;
                            color:#263B32;
                            font-family:'Manrope', sans-serif;">

                            <strong>Source:</strong>

                            <details style="display:inline-block;">
                                <summary style="
                                    cursor:pointer;
                                    color:#245B38;
                                    font-weight:600;
                                    background:#E8F5EF;
                                    border:1px solid #B5D9C8;
                                    border-radius:10px;
                                    padding:6px 12px;">
                                    View source
                                </summary>

                                <div style="
                                    margin-top:8px;
                                    padding:10px 12px;
                                    background:#FFFFFF;
                                    border:1px solid #E1EAE2;
                                    border-radius:10px;">
                                    <a href="{primary_source['url']}" target="_blank"
                                       style="color:#245B38;font-weight:600;text-decoration:none;">
                                        {primary_source['name']}
                                    </a>
                                </div>
                            </details>
                        </div>
                        """
                    ).strip()
                )

                st.caption("Knowledge Base Last Updated: 06 Nov 2026")

                with st.container(key="how_answer_panel"):
                    with st.expander("How we got this answer", expanded=False):
                        st.markdown(
                            """
                            This answer was generated using information
                            available in the HDFC Mutual Fund knowledge base.

                            1. Your question was matched against relevant information.
                            2. Retrieved passages were reranked for relevance.
                            3. The AI generated an answer grounded in those passages.
                            """
                        )

                        if len(sources) > 1:
                            st.markdown("**Additional supporting sources:**")

                            for source in sources[1:]:
                                st.markdown(
                                    f"- [{source['name']}]({source['url']})"
                                )
            
            # Related questions
            selected_fund = st.session_state.get("selected_fund")

            if selected_fund and selected_fund in FUND_OPTIONS:
                related_questions = FUND_OPTIONS[selected_fund]["related_questions"]

            else:
                fund_name = None

                if "elss" in query_lower:
                    fund_name = "HDFC ELSS Tax Saver Fund"
                elif "mid cap" in query_lower:
                    fund_name = "HDFC Mid Cap Fund"
                elif "large cap" in query_lower:
                    fund_name = "HDFC Large Cap Fund"
                elif "flexi cap" in query_lower:
                    fund_name = "HDFC Flexi Cap Fund"

                if fund_name:
                    related_questions = [
                        f"Who is the fund manager of {fund_name}?",
                        f"What risk level is shown for {fund_name}?",
                        f"What is the investment objective of {fund_name}?"
                    ]
                else:
                    related_questions = [
                        "What is the role of HDFC Asset Management Company?",
                        "What key information is available about HDFC Mutual Fund?"
                    ]

            with st.container(border=True, key="related_questions_panel"):

                st.markdown(
                    '<p style="color:#00543C;font-size:1.15rem;font-weight:700;">'
                    '<span style="color:#00543C;">✦</span> Related Questions'
                    '</p>',
                    unsafe_allow_html=True
                )

                related_cols = st.columns(len(related_questions))

                for i, related_q in enumerate(related_questions):
                    with related_cols[i]:
                        st.button(
                            related_q,
                            key=f"related_{i}",
                            use_container_width=True,
                            on_click=queue_related_question,
                            args=(related_q,)
                        )
                    

            # Show disclaimer
            st.markdown("---")
            st.caption(DISCLAIMER)
            st.caption("Limited to: HDFC AMC Overview, Large Cap, Flexi Cap, ELSS Tax Saver, and Mid Cap Direct Growth funds.")

if __name__ == "__main__":
    main()
