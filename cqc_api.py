import os
from typing import List, Dict
from datetime import date
import requests
import streamlit as st

BASE_URL = "https://api.service.cqc.org.uk/public/v1"


def _headers() -> Dict[str, str]:
    key = st.secrets.get("cqc", {}).get("api_key")
    headers = {"Accept": "application/json"}
    if key:
        headers["Ocp-Apim-Subscription-Key"] = key
    return headers


def search_locations(query: str) -> List[Dict]:
    params = {"term": query}
    r = requests.get(f"{BASE_URL}/locations", headers=_headers(), params=params)
    r.raise_for_status()
    return r.json().get("locations", [])


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
