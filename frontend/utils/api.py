import requests
import streamlit as st
import os

# Default to localhost if .env is missing
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def api_request(method, endpoint, data=None, files=None):
    """
    Generic function to make API requests with authentication.
    """
    url = f"{API_URL}{endpoint}"
    
    headers = {}
    
    # Add Token if user is logged in
    if "access_token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            # If sending files, don't set Content-Type header manually (requests does it)
            if files:
                response = requests.post(url, headers=headers, files=files, data=data)
            else:
                response = requests.post(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
            
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the Backend. Is it running?")
        return None