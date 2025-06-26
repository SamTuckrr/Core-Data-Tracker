# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import cqc_api  # assumes cqc_api.py is in the same directory

# === STREAMLIT SETUP ===
st.set_page_config(page_title="Care Provider Tracker", layout="wide")
st.title("Care Provider Tracker - TQ & PL Postcodes")

# === SIDEBAR ===
st.sidebar.header("Options")
option = st.sidebar.radio("Choose a tool:", ["API Updates", "Manual Lookup", "About"])

# === API UPDATES TAB ===
if option == "API Updates":
    st.subheader("Live CQC Change Feed")
    start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=14))
    end_date = st.date_input("End Date", value=datetime.now().date())

    if st.button("Fetch Changes"):
        with st.spinner("Fetching changed locations from CQC..."):
            changes = cqc_api.get_changes(start_date, end_date)
            if changes:
                st.success(f"{len(changes)} changes found.")
                change_ids = [change.get("id") for change in changes]
                st.dataframe(pd.DataFrame(change_ids, columns=["Changed Location IDs"]))
            else:
                st.info("No changes found in this timeframe.")

# === MANUAL LOOKUP TAB ===
elif option == "Manual Lookup":
    st.subheader("Manually Look Up a Location")
    location_id = st.text_input("Enter Location ID (e.g., 1-1234567890)")
    if st.button("Fetch Location Info") and location_id:
        with st.spinner("Fetching location details..."):
            try:
                location = cqc_api.get_location_by_id(location_id)
                st.json(location)
            except Exception as e:
                st.error(f"Error: {e}")

# === ABOUT TAB ===
elif option == "About":
    st.subheader("About This App")
    st.markdown("""
    This tool connects to the **CQC Syndication API** to:
    - Track care provider updates in real time
    - Search by Location ID
    - Help sales teams identify active, changed, or new care settings

    🔐 Your API key is stored securely using Streamlit Secrets.
    """)
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json().get("items", [])

