# Core Data Tracker

Streamlit application for tracking care provider information using the CQC Syndication API and Companies House. Users can search by postcode, name or region, compare results against previous CSV uploads and schedule regular data checks.

## Features
- Search the CQC API for locations and providers
- Optional lookup of Companies House details by registration number
- Paginated, searchable results table
- Compare new results with uploaded CSVs and highlight differences
- Export results or change reports as CSV
- Schedule weekly job-ad scraping and monthly change reports
- Basic user profile preferences stored in session state

## Setup
1. Install requirements
```bash
pip install -r requirements.txt
```
2. Add API keys to `.streamlit/secrets.toml` (see provided template).
3. Run the app
```bash
streamlit run app.py
```

The application is designed to be deployable on Streamlit Cloud.
