import csv
import io
import threading
import time
from datetime import date, datetime, timedelta
from typing import List, Dict

import pandas as pd
import requests
import schedule
import streamlit as st

import cqc_api
import company_api
import job_scraper

st.set_page_config(page_title="Care Provider Tracker", layout="wide")

# --- Authentication (optional) ---
try:
    import streamlit_authenticator as stauth
    credentials = {
        "usernames": st.secrets.get("auth", {}).get("usernames", []),
        "passwords": st.secrets.get("auth", {}).get("passwords", []),
    }
    if credentials["usernames"]:
        authenticator = stauth.Authenticate({u: p for u, p in zip(credentials["usernames"], credentials["passwords"])} , 'some_cookie', 'random_key', cookie_expiry_days=1)
        name, auth_status, username = authenticator.login('Login', 'main')
        if not auth_status:
            st.stop()
except Exception:
    pass

# --- Helpers ---
PAGE_SIZE = 20


def paginate_df(df: pd.DataFrame, page: int) -> pd.DataFrame:
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    return df.iloc[start:end]


def compare_data(current: pd.DataFrame, previous: pd.DataFrame) -> pd.DataFrame:
    diffs = []
    for _, row in current.iterrows():
        match = previous[previous['locationId'] == row['locationId']]
        if not match.empty:
            old = match.iloc[0]
            for col in ['phone', 'email', 'registeredManager']:
                if row.get(col) != old.get(col):
                    diffs.append({
                        'locationId': row['locationId'],
                        'field': col,
                        'old': old.get(col),
                        'new': row.get(col)
                    })
    return pd.DataFrame(diffs)


# --- Scheduler thread ---

def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)


if 'scheduler_started' not in st.session_state:
    st.session_state.scheduler_started = False

if not st.session_state.scheduler_started:
    threading.Thread(target=scheduler_thread, daemon=True).start()
    st.session_state.scheduler_started = True


# --- Sidebar ---
st.sidebar.header('Search')
query = st.sidebar.text_input('Postcode, care home name, or region')
company_no = st.sidebar.text_input('Company Registration Number (optional)')
if st.sidebar.button('Search') and query:
    with st.spinner('Searching CQC...'):
        try:
            data = cqc_api.search_locations(query)
            st.session_state.results = pd.json_normalize(data)
        except Exception as e:
            st.error(f'Error searching CQC: {e}')
            st.session_state.results = pd.DataFrame()
    if company_no:
        with st.spinner('Fetching company info...'):
            try:
                st.session_state.company = company_api.get_company(company_no)
            except Exception as e:
                st.error(f'Error fetching company: {e}')
                st.session_state.company = {}

# --- Results ---
results = st.session_state.get('results')
if isinstance(results, pd.DataFrame) and not results.empty:
    search_filter = st.text_input('Filter results')
    filtered = results[results.apply(lambda r: search_filter.lower() in r.to_string().lower(), axis=1)] if search_filter else results
    pages = (len(filtered) - 1) // PAGE_SIZE + 1
    page = st.number_input('Page', 0, max(pages-1, 0), 0)
    st.dataframe(paginate_df(filtered, int(page)))
    csv_data = filtered.to_csv(index=False)
    st.download_button('Export CSV', csv_data, file_name='cqc_results.csv')
else:
    st.write('No results yet.')

# --- Company info ---
company = st.session_state.get('company')
if company:
    st.subheader('Company House Record')
    st.json(company)

# --- Upload previous results for comparison ---
uploaded = st.file_uploader('Upload previous CSV to compare', type='csv')
if uploaded and isinstance(results, pd.DataFrame) and not results.empty:
    prev = pd.read_csv(uploaded)
    diffs = compare_data(results, prev)
    if not diffs.empty:
        st.subheader('Detected Changes')
        st.dataframe(diffs)
        st.download_button('Download Changes', diffs.to_csv(index=False), file_name='changes.csv')
    else:
        st.info('No differences found.')

# --- Scheduling ---
def weekly_jobs():
    jobs = job_scraper.search_jobs('care assistant', query)
    with open('weekly_jobs.csv', 'w', newline='', encoding='utf-8') as f:
        pd.DataFrame(jobs).to_csv(f, index=False)

def monthly_changes():
    end = date.today()
    start = end - timedelta(days=30)
    changes = cqc_api.get_changes(start, end)
    with open('monthly_changes.csv', 'w', newline='', encoding='utf-8') as f:
        pd.DataFrame(changes).to_csv(f, index=False)

if st.sidebar.button('Schedule Weekly Job Scrape'):
    schedule.every().week.do(weekly_jobs)
    st.sidebar.success('Weekly job scrape scheduled.')

if st.sidebar.button('Schedule Monthly Change Report'):
    schedule.every().month.do(monthly_changes)
    st.sidebar.success('Monthly change report scheduled.')

# --- Profile ---
st.sidebar.header('Profile')
region_pref = st.sidebar.text_input('Preferred region', st.session_state.get('region_pref', ''))
if st.sidebar.button('Save Profile'):
    st.session_state['region_pref'] = region_pref
    st.sidebar.success('Profile saved.')
