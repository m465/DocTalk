import streamlit as st
from utils.api import api_request
import pandas as pd


st.set_page_config(page_title="Manage Documents", page_icon="📂", layout="wide")

# 1. Check Login
if "access_token" not in st.session_state:
    st.warning("Please Login first!")
    st.stop()

st.title("📂 Document Management")

# Tabs for better UI organization
tab1, tab2 = st.tabs(["📤 Upload New", "⚙️ Manage Files"])

# --- TAB 1: UPLOAD ---
with tab1:
    st.header("Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose PDF or TXT files", 
        type=["pdf", "txt"], 
        accept_multiple_files=True
    )

    if st.button("Upload Files") and uploaded_files:
        with st.spinner("Uploading..."):
            files_payload = [
                ("files", (file.name, file, file.type)) for file in uploaded_files
            ]
            # Call API
            response = api_request("POST", "/documents/upload", files=files_payload)
            
            if response and response.status_code == 200:
                st.success(f"✅ Successfully uploaded {len(uploaded_files)} files!")
                # Force reload to update the list in Tab 2
                st.rerun() 
            else:
                st.error("❌ Upload failed.")

# --- TAB 2: MANAGE & PROCESS ---
with tab2:
    st.header("Your Documents")
    
    # Fetch latest documents
    response = api_request("GET", "/documents/")
    
    if response and response.status_code == 200:
        docs = response.json()
        
        if not docs:
            st.info("No documents found. Go to the 'Upload' tab to get started.")
        else:
            # Create a header row
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            col1.markdown("**Filename**")
            col2.markdown("**Status**")
            col3.markdown("**Size**")
            col4.markdown("**Process**")
            col5.markdown("**Delete**")
            st.divider()

            # Iterate through documents
            for doc in docs:
                c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
                
                c1.write(f"📄 {doc['filename']}")
                
                # Status Badge
                if doc['status'] == 'processed':
                    c2.success("Processed")
                elif doc['status'] == 'processing':
                    c2.warning("Processing")
                elif doc['status'] == 'failed':
                    c2.error("Failed")
                else:
                    c2.info("Uploaded")

                c3.write(f"{doc['file_size']/1024:.1f} KB")

                # Process Button
                # Only show if not yet processed
                if doc['status'] == 'uploaded':
                    if c4.button("⚡ Process", key=f"proc_{doc['id']}"):
                        with st.spinner("Processing (Chunking & Embedding)..."):
                            payload = {
                                "document_id": doc['id'],
                                "chunk_size": 1000,
                                "chunk_overlap": 200
                            }
                            proc_res = api_request("POST", "/documents/process", data=payload)
                            
                            if proc_res and proc_res.status_code == 200:
                                st.toast(f"Processing Complete for {doc['filename']}!")
                                st.rerun()
                            else:
                                st.error("Processing Failed")
                else:
                    c4.write("-")

                # Delete Button
                if c5.button("🗑️", key=f"del_{doc['id']}"):
                    del_res = api_request("DELETE", f"/documents/{doc['id']}")
                    if del_res and del_res.status_code == 200:
                        st.success("Deleted!")
                        st.rerun()
                    else:
                        st.error("Delete failed")
                
                st.divider()

    else:
        st.error("Failed to fetch documents.")