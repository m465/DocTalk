import streamlit as st
from utils.api import api_request
from utils.ui import apply_custom_styles, render_sidebar

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")
apply_custom_styles()
render_sidebar(current_page="login") 

# Centered Card Layout
st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("🔐 Login")
    st.write("Sign in to continue to your dashboard.")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submit = st.form_submit_button("Sign In", use_container_width=True)

    if submit:
        if not email or not password:
            st.warning("⚠️ Please fill in all fields.")
        else:
            with st.spinner("Authenticating..."):
                payload = {"email": email, "password": password}
                response = api_request("POST", "/auth/login", data=payload)
                
                if response and response.status_code == 200:
                    token_data = response.json()
                    st.session_state["access_token"] = token_data["access_token"]
                    # DIRECT ROUTING TO HOME
                    st.switch_page("home.py")
                else:
                    st.error("❌ Invalid credentials")

    st.markdown("---")
    st.caption("Don't have an account? Go to the **Signup** page.")