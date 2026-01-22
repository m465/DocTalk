import streamlit as st
from utils.api import api_request
from utils.ui import apply_custom_styles, render_sidebar

st.set_page_config(page_title="AI Chat", page_icon="💬", layout="wide")
apply_custom_styles()
render_sidebar()

# Check Auth
if "access_token" not in st.session_state:
    st.switch_page("pages/Login.py")

st.title("💬 Chat with Documents")

# --- Sidebar Settings ---
with st.sidebar:
    st.divider()
    st.markdown("### ⚙️ Model Settings")
    model_choice = st.selectbox("LLM Model", ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4-turbo"])
    temp = st.slider("Temperature (Creativity)", 0.0, 1.0, 0.7)
    k_val = st.slider("Context Chunks", 1, 10, 5)

# --- Chat Logic ---

# 1. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Show sources if available
        if "sources" in message:
            with st.expander("📚 Referenced Sources"):
                for idx, source in enumerate(message["sources"]):
                    st.markdown(f"**{idx+1}. {source['source']}** (Page {source.get('page', 1)})")
                    st.caption(source['content'])

# 3. Handle User Input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            payload = {
                "question": prompt,
                "model": model_choice,
                "temperature": temp,
                "k": k_val
            }
            
            response = api_request("POST", "/chat/query", data=payload)
            
            if response and response.status_code == 200:
                data = response.json()
                answer = data["answer"]
                sources = data["sources"]
                
                st.markdown(answer)
                
                if sources:
                    st.markdown("### 📚 Reference Sources")
                    
                    for idx, source in enumerate(sources):
                        
                        with st.container(border=True):
                            c1, c2 = st.columns([4, 1])
                            with c1:
                                st.markdown(f"**📄 {source['source']}**")
                            with c2:
                                st.caption(f"Page {source['page']}")
                            
                            # Body: The actual text content
                            st.markdown(f"_{source['content']}..._")
                            
                            # Optional: A visual divider if it's not the last one
                            # st.divider() 

                # Save to history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "sources": sources
                })
            else:
                error_msg = "Sorry, I encountered an error."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})