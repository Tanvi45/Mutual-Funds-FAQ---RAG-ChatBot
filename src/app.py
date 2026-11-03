import streamlit as st
import re
from generator import GenerationError, generate_answer, source_records
from retriever import Retriever

# Page config
st.set_page_config(page_title="Groww HDFC MF FAQ Assistant", page_icon="📊")

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
    st.title("Welcome to Groww HDFC Mutual Fund FAQ Assistant")
    st.caption(DISCLAIMER)
    
    st.markdown("### Example Questions:")
    cols = st.columns(3)
    for i, q in enumerate(EXAMPLE_QUESTIONS):
        if cols[i].button(q, use_container_width=True):
            st.session_state.query = q
    
    # Query input
    query = st.text_input("Ask a factual question about HDFC Mutual Fund schemes:", 
                          value=st.session_state.get('query', ''))
    
    if st.button("Ask", type="primary") or query:
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
        advice_keywords = ['should i', 'buy', 'sell', 'recommend', 'better for me', 'which fund should', 'portfolio']
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
            st.markdown("**Sources used:**")
            for source in sources:
                st.markdown(f"- [{source['label']}] [{source['name']}]({source['url']})")
        
        # Show disclaimer
        st.markdown("---")
        st.caption(DISCLAIMER)
        st.caption("Limited to: HDFC AMC Overview, Large Cap, Flexi Cap, ELSS Tax Saver, and Mid Cap Direct Growth funds.")

if __name__ == "__main__":
    main()
