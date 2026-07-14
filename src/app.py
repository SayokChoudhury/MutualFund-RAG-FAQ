import os
import sys
import streamlit as st

# Add root directory to python path to resolve src modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.guardrails.intent_classifier import IntentClassifier, QueryIntent
from src.retrieval.retriever import Retriever
from src.generation.llm_client import LLMClient
from src.generation.formatter import format_response
from src.guardrails.post_generation import validate_response

# 7.1 Page Config
st.set_page_config(
    page_title="HDFC Mutual Fund FAQ Assistant",
    page_icon="🏦",
    layout="centered"
)

# 7.9 Custom CSS
st.markdown("""
<style>
    .disclaimer {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ffeeba;
        margin-bottom: 20px;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# 7.2 Header and Disclaimer
st.title("🏦 HDFC Mutual Fund FAQ Assistant")
st.markdown("""
<div class="disclaimer">
    ⚠️ <b>Facts-only. No investment advice.</b><br>
    I can only answer factual questions based on the scheme documents of specific HDFC Mutual Funds.
</div>
""", unsafe_allow_html=True)

# Initialize singletons in session state
if "classifier" not in st.session_state:
    st.session_state.classifier = IntentClassifier()
if "retriever" not in st.session_state:
    st.session_state.retriever = Retriever()
if "llm_client" not in st.session_state:
    st.session_state.llm_client = LLMClient()
if "messages" not in st.session_state:
    st.session_state.messages = []

# 7.3 Example questions
st.markdown("### Try asking:")
example_questions = [
    "What is the expense ratio of HDFC Mid Cap Fund?",
    "What is the minimum SIP amount for HDFC Small Cap Fund?",
    "How do I download my capital gains statement?"
]

prompt = st.chat_input("Ask a factual question...")

# Display examples as buttons
for i, q in enumerate(example_questions):
    if st.button(q, key=f"btn_{i}"):
        prompt = q

# 7.5 Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7.6 Wire up full pipeline
if prompt:
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing intent..."):
            intent = st.session_state.classifier.classify(prompt)
            
        if intent != QueryIntent.FACTUAL:
            final_answer = st.session_state.classifier.get_refusal_response(intent)
        else:
            with st.spinner("Searching documents..."):
                chunks = st.session_state.retriever.retrieve(prompt)
                
            with st.spinner("Generating answer..."):
                raw_answer = st.session_state.llm_client.generate(prompt, chunks)
                
            with st.spinner("Validating and formatting..."):
                formatted_answer = format_response(raw_answer, chunks)
                final_answer = validate_response(formatted_answer)
                    
        st.markdown(final_answer)
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
