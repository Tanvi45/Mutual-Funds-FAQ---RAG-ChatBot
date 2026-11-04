import streamlit as st
import re
from generator import GenerationError, generate_answer, source_records
from retriever import Retriever

# Page config
st.set_page_config(page_title="Groww HDFC MF FAQ Assistant", page_icon="📊")
# Custom UI styling
st.markdown("""
<style>
    .stApp {
        background-color: #F7F9F6;
        color: #1F3328;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #183D2B;
    }

    div[data-testid="stButton"] > button {
        border-radius: 14px;
        border: 1px solid #D7E5D9;
        background-color: #FFFFFF;
        color: #244B34;
        padding: 0.7rem 1rem;
    }

    div[data-testid="stButton"] > button:hover {
        border-color: #5B946B;
        background-color: #EEF6EF;
        color: #183D2B;
    }

div[data-testid="stTextInput"] input {
    border-radius: 14px;
    border: 1px solid #D7E5D9;
    background-color: #FFFFFF;
    color: #1F3328 !important;
    -webkit-text-fill-color: #1F3328 !important;
    caret-color: #1F3328;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #718078 !important;
    opacity: 1;
}

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }
/* Make Streamlit warning and info message text readable */
div[data-testid="stAlert"] p {
    color: #222222 !important;
    -webkit-text-fill-color: #222222 !important;
}
</style>
""", unsafe_allow_html=True)

# Disclaimer
DISCLAIMER = "Facts-only. No investment advice."

# Example questions
EXAMPLE_QUESTIONS = [
    "What is the expense ratio of HDFC Large Cap Fund Direct Growth?",
    "What is the ELSS lock-in period for HDFC ELSS Tax Saver Fund?",
    "What is the minimum SIP for HDFC Mid Cap Fund Direct Growth?"
]

# Load components
@st.cache_resource
def load_components():
    retriever = Retriever()
    return retriever

def main():
        

    def queue_related_question(question):
        st.session_state["query_input"] = question
        st.session_state["run_related_query"] = True

    # Three-panel layout
    left, center, right = st.columns([1, 2.2, 1])

    with left:
        with st.expander("ℹ️ About this project", expanded=True):
            st.markdown("""
            HDFC Mutual Fund FAQ Chatbot helps users find factual information
            about HDFC Mutual Fund schemes.

            It uses **Retrieval-Augmented Generation (RAG)** to search indexed
            sources and generate answers grounded in retrieved information.

            This is an independent project, not affiliated with HDFC Mutual Fund
            or Groww. It does not provide personalized investment advice.
            """)

    with center:
        st.markdown(
            "<h1 style='text-align:center;'>🌱 HDFC Mutual Fund FAQ</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align:center;color:#617367;'>"
            "Your friendly assistant for fund facts</p>",
            unsafe_allow_html=True
        )
        st.caption(DISCLAIMER)

        st.markdown("### 💬 What would you like to know?")

        for i, q in enumerate(EXAMPLE_QUESTIONS):
            st.button(
               q, 
               key=f"starter_{i}",
               use_container_width=True,
               on_click=queue_related_question,
               args=(q,)
        )

    with right:
        st.markdown("""
        <div style="background:#FFFFFF;border:1px solid #E1EAE2;
                    border-radius:16px;padding:16px;">
            <h4>🔎 How RAG works</h4>
            <p>💬 Ask a question</p>
            <p>↓</p>
            <p>📚 Retrieve relevant sources</p>
            <p>↓</p>
            <p>✨ Generate a factual answer</p>
        </div>
        """, unsafe_allow_html=True)
        
    with center: 
        # Query input


        if "query_input" not in st.session_state:
            st.session_state["query_input"] = st.session_state.get("query", "")

        query = st.text_input(
            "Ask a factual question about HDFC Mutual Fund schemes:",
            key="query_input"
        )

        ask_clicked = st.button("Ask", type="primary")
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
                st.markdown("#### 📚 Sources")

                for source in sources:
                    st.markdown(
                        f"""
                        <div style="
                            background:#FFFFFF;
                            border:1px solid #E1EAE2;
                            border-radius:12px;
                            padding:12px 16px;
                            margin-bottom:8px;">
                            <span style="color:#617367;font-size:0.85rem;">
                                {source['label']}
                            </span><br>
                            <a href="{source['url']}" target="_blank"
                               style="color:#245B38;font-weight:600;text-decoration:none;">
                                🔗 {source['name']} ↗
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
            # Related questions - suggest different information areas

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
                candidates = [
                    (
                        "manager",
                        f"Who is the fund manager of {fund_name}?",
                        ["fund manager", "manager"]
                    ),
                    (
                        "risk",
                        f"What risk level is shown for {fund_name}?",
                        ["risk", "riskometer"]
                    ),
                    (
                        "objective",
                        f"What is the investment objective of {fund_name}?",
                        ["objective", "investment goal"]
                    )
                ]

                related_questions = [
                    question
                    for topic, question, keywords in candidates
                ][:3]

            else:
                related_questions = [
                    "What is the role of HDFC Asset Management Company?",
                    "What key information is available about HDFC Mutual Fund?"
                ]

            st.markdown("#### 🔎 Related questions")

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
