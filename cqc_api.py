import os
from typing import List, Dict
from datetime import date
import requests
import streamlit as st

# Use the CQC Syndication API rather than the public API
BASE_URL = "https://api.service.cqc.org.uk/syndication/v1"


def _headers() -> Dict[str, str]:
    key = st.secrets.get("cqc", {}).get("api_key")
    headers = {"Accept": "application/json"}
    if key:
        headers["Ocp-Apim-Subscription-Key"] = key
    return headers


def search_locations(term):
    """Search CQC locations using the Syndication API."""
    import requests
    import streamlit as st

    api_key = st.secrets["cqc"]["api_key"]
    url = f"{BASE_URL}/locations?term={term}"
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": response.status_code}


def get_location(location_id: str) -> Dict:
    r = requests.get(f"{BASE_URL}/locations/{location_id}", headers=_headers())
    r.raise_for_status()
    return r.json()


def get_provider(provider_id: str) -> Dict:
    r = requests.get(f"{BASE_URL}/providers/{provider_id}", headers=_headers())
    r.raise_for_status()
    return r.json()


def get_changes(start: date, end: date) -> List[Dict]:
    params = {"startTimestamp": start.isoformat(), "endTimestamp": end.isoformat()}
    r = requests.get(f"{BASE_URL}/changes", headers=_headers(), params=params)
    r.raise_for_status()
    return r.json().get("changes", [])
