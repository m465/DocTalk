import streamlit as st
import time  # Import time for the delay
from utils.api import api_request
from utils.ui import apply_custom_styles, render_sidebar

st.set_page_config(page_title="Sign Up", page_icon="✍", layout="centered")
apply_custom_styles()
render_sidebar(current_page="signup") 

st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("✍ Create Account")
    st.write("Join us to chat with your documents.")

    with st.form("signup_form"):
        full_name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        # Make the button wide
        submit = st.form_submit_button("Sign Up", use_container_width=True)

    if submit:
        if not email or not password or not full_name:
            st.warning("⚠️ Please fill in all fields.")
        else:
            with st.spinner("Creating account..."):
                payload = {
                    "email": email,
                    "password": password,
                    "full_name": full_name
                }
                response = api_request("POST", "/auth/signup", data=payload)
                
                # Case 1: Success
                if response and response.status_code == 200:
                    st.success("✅ Account created successfully! Redirecting to login...")
                    time.sleep(1.5)
                    st.switch_page("pages/Login.py")
                
                # Case 2: Account already exists (Backend sends 400)
                elif response and response.status_code == 400 :
                    detail = response.json().get("detail", "")
                    if "already registered" in detail:
                        st.warning("⚠️ Account already exists with this email! Please Log In.")
                    else:
                        # Some other 400 error (e.g., weak password)
                        st.error(f"❌ {detail}")
                
                # Case 3: Server/Connection Errors
                else:
                    error_msg = response.json().get("detail", "Signup failed") if response else "Unknown error"
                    st.error(f"❌ {error_msg}")

    st.markdown("---")
    st.caption("Already have an account?")
    if st.button("Go to Login"):
        st.switch_page("pages/Login.py")