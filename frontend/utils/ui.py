import streamlit as st

def apply_custom_styles():
    # ... (Keep your existing CSS with the Teal/Green colors exactly as before) ...
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
        h1 { color: #1E293B; font-weight: 700; }
        h2, h3 { color: #334155; font-weight: 600; }
        
        /* YOUR CUSTOM COLORS */
        div[data-testid="stMetric"], .stMetric {
            background-color: #8fc7c0;
            border: 1px solid #E2E8F0;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        [data-testid="stSidebar"] {
            background-color: #43615a;
            border-right: 1px solid #E2E8F0;
        }
        
        /* DELTA BADGE STYLING */
        div[data-testid="stMetricDelta"] {
            background-color: #f8fafc;
            color: #334155;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 13px;
            font-weight: 600;
            width: fit-content;
            margin-top: 8px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.5);
        }
        div[data-testid="stMetricDelta"] > svg { fill: #334155 !important; }
        div[data-testid="stMetricValue"] { color: #ffffff; font-weight: 700; }

        div.stButton > button {
            background-color: #2563EB;
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        div.stButton > button:hover { background-color: #1D4ED8; }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar(current_page="home"):
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2921/2921226.png", width=50)
        st.markdown("<h3 style='color: white;'>DocTalk AI</h3>", unsafe_allow_html=True)
        st.markdown("---")

        # LOGIC: Check Auth State
        if "access_token" in st.session_state:
            # --- LOGGED IN VIEW ---
            st.success(f"🟢 User: {st.session_state.get('user_name', 'Online')}")
            
            st.markdown("### Navigation")
            # st.page_link is cleaner than buttons for navigation
            st.page_link("home.py", label="Dashboard", icon="🏠")
            st.page_link("pages/Documents.py", label="Documents", icon="📂")
            st.page_link("pages/Chat.py", label="Chat", icon="💬")
            
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.clear()
                st.switch_page("pages/Login.py")

        else:
            # --- LOGGED OUT VIEW ---
            st.info("🔴 Guest Mode")
            
            if current_page == "login":
                st.markdown("New here?")
                if st.button("Create Account", use_container_width=True):
                    st.switch_page("pages/Signup.py")
            
            elif current_page == "signup":
                st.markdown("Have an account?")
                if st.button("Log In", use_container_width=True):
                    st.switch_page("pages/Login.py")