# care_data_tracker/app.py

import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# === CONFIG ===
CQC_DATA_FILE = "data/cqc_data_tq_pl.csv"
SNAPSHOT_FILE = "data/data_snapshot.csv"

# === HELPER FUNCTIONS ===

def load_cqc_data():
    df = pd.read_csv(CQC_DATA_FILE)
    df = df[df['Postcode'].str.startswith(('TQ', 'PL'))]
    df = df[['Location Name', 'Address Line 1', 'Address Line 2', 'Town', 'County',
             'Postcode', 'Number of Beds', 'Main Service Type', 'CQC Link',
             'Provider Name']]
    return df

def compare_snapshots(current_df, snapshot_df):
    changes = []
    for _, row in current_df.iterrows():
        site_id = row['CQC Link']
        snap = snapshot_df[snapshot_df['CQC Link'] == site_id]
        if not snap.empty:
            snap_row = snap.iloc[0]
            for col in row.index:
                if str(row[col]) != str(snap_row[col]):
                    changes.append({
                        'Location Name': row['Location Name'],
                        'Field': col,
                        'Old Value': snap_row[col],
                        'New Value': row[col]
                    })
    return pd.DataFrame(changes)

def save_snapshot(df):
    df.to_csv(SNAPSHOT_FILE, index=False)

def load_snapshot():
    if os.path.exists(SNAPSHOT_FILE):
        return pd.read_csv(SNAPSHOT_FILE)
    else:
        return pd.DataFrame(columns=['Location Name', 'CQC Link'])

# === STREAMLIT UI ===
st.set_page_config(page_title="Care Data Tracker", layout="wide")
st.title("Care Provider Tracker - TQ & PL Postcodes")

st.sidebar.header("Options")
option = st.sidebar.radio("Choose an option:", ["View Data", "Check Changes", "Manual Check"])

# === LOAD DATA ===
cqc_df = load_cqc_data()
snapshot_df = load_snapshot()

if option == "View Data":
    st.subheader("Current CQC Records")
    st.dataframe(cqc_df)
    if st.button("Save Snapshot Now"):
        save_snapshot(cqc_df)
        st.success("Snapshot saved.")

elif option == "Check Changes":
    st.subheader("Compare Current Data to Last Snapshot")
    if snapshot_df.empty:
        st.warning("No previous snapshot found. Please save a snapshot first.")
    else:
        changes_df = compare_snapshots(cqc_df, snapshot_df)
        if changes_df.empty:
            st.success("No changes detected since last snapshot.")
        else:
            st.dataframe(changes_df)
            st.download_button("Download Changes Report", data=changes_df.to_csv(index=False), file_name="cqc_changes_report.csv")

elif option == "Manual Check":
    st.subheader("Manual Account Checker")
    search_term = st.text_input("Enter care home name or postcode")
    if search_term:
        results = cqc_df[cqc_df.apply(lambda row: search_term.lower() in row.to_string().lower(), axis=1)]
        if not results.empty:
            st.dataframe(results)
        else:
            st.info("No matching records found.")
