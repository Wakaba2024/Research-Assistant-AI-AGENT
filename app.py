import streamlit as st
from main import agent_executor, parser  # Import your agent and parser from main.py
from httpx import HTTPStatusError

st.set_page_config(page_title="Research Assistant", layout="wide")
st.title("🧠 AI Research Assistant")

st.write(
    """
This AI-powered assistant generates research summaries for any topic, 
with sources and tools used.
"""
)

# Text input for user query
query = st.text_area("Enter your research query:", height=120)

# Cache results to avoid repeated API calls for the same query
@st.cache_data(show_spinner=False)
def run_agent(query_text):
    try:
        raw_response = agent_executor.invoke({"query": query_text})

        # DEBUG: Check the structure of raw_response
        # st.write(raw_response)

        # If raw_response is a dict with "output", extract text
        if isinstance(raw_response, dict) and "output" in raw_response:
            text_content = raw_response["output"][0]["text"]
        # If raw_response is already a string
        elif isinstance(raw_response, str):
            text_content = raw_response
        else:
            return None, f"Unexpected raw_response structure: {type(raw_response)}"

        structured_response = parser.parse(text_content)
        return structured_response, None

    except HTTPStatusError as e:
        if e.response.status_code == 429:
            return None, "Mistral API limit reached or model is busy. Please try again later."
        return None, f"API Error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


if st.button("Search"):
    if not query.strip():
        st.warning("Please enter a query to start research.")
    else:
        with st.spinner("Generating research..."):
            result, error = run_agent(query)
            
            if error:
                st.error(error)
            else:
                st.subheader("📄 Summary")
                st.write(result.summary)
                
                st.subheader("🔗 Sources")
                for source in result.sources:
                    st.write("-", source)
                
                st.subheader("🛠 Tools Used")
                st.write(", ".join(result.tools_used))
