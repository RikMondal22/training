import streamlit as st
import requests
import os

# Configure the page
st.set_page_config(
    page_title="BSK Training Optimization",
    page_icon="🎓",
    layout="wide"
)

st.title("BSK Training Optimization System")
st.markdown("""
Welcome to the BSK Training Optimization System!
Use the sidebar to navigate to different data views and analytics.
Each section provides interactive tables and visualizations for your data.
""") 

# Get API URL from environment variable or use localhost as fallback
API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:54300")

def fetch_all_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {e}")
        return []

# Check backend connection
try:
    response = requests.get(f"{API_BASE_URL}/", timeout=5)
    if response.status_code == 200:
        st.success(f"✅ Connected to backend at: {API_BASE_URL}")
    else:
        st.warning(f"⚠️ Backend responded with status {response.status_code}")
except Exception as e:
    st.error(f"❌ Cannot connect to backend at {API_BASE_URL}: {e}")
    st.info("Please ensure the backend service is running.")

bsk_centers = fetch_all_data("bsk/")
deos = fetch_all_data("deo/")
services = fetch_all_data("services/")

num_bsks = len(bsk_centers) if bsk_centers else 0
num_deos = len(deos) if deos else 0
num_services = len(services) if services else 0

# Display summary info at the top
st.markdown("### System Overview")
col_a, col_b, col_c = st.columns(3)
col_a.metric("Total BSKs", num_bsks)
col_b.metric("Total DEOs", num_deos)
col_c.metric("Total Services", num_services)