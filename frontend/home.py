import streamlit as st
from utils.api import api_request
from utils.ui import apply_custom_styles, render_sidebar

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

if "access_token" not in st.session_state:
    st.switch_page("pages/Login.py")

apply_custom_styles()
render_sidebar(current_page="home")


st.title("🚀 Dashboard")
st.write("Overview of your documents and AI interactions.")

st.markdown("---")

# 3. Stats Section
col1, col2, col3 = st.columns(3)

# Fetch actual doc count
docs_count = 0
try:
    res = api_request("GET", "/documents/")
    if res and res.status_code == 200:
        docs = res.json()
        docs_count = len(docs)
except:
    pass

with col1:
    st.metric(label="Uploaded Documents", value=docs_count, delta="Total Files")
with col2:
    processed = len([d for d in docs if d['status'] == 'processed']) if 'docs' in locals() else 0
    st.metric(label="AI Ready (Processed)", value=processed, delta="Ready to Chat")
with col3:
    st.metric(label="AI Model", value="llama3.2", delta="Active")

st.markdown("---")

# 4. Quick Actions
st.subheader("Quick Actions")
ac1, ac2 = st.columns(2)

with ac1:
    st.info("📂 **Manage Documents**")
    st.write("Upload new PDF/TXT files or delete old ones.")
    if st.button("Go to Documents"):
        st.switch_page("pages/Documents.py")

with ac2:
    st.success("💬 **Start Chatting**")
    st.write("Ask questions based on your processed documents.")
    if st.button("Go to Chat"):
        st.switch_page("pages/Chat.py")