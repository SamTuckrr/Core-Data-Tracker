import requests
import streamlit as st
from typing import Dict

BASE_URL = "https://api.company-information.service.gov.uk"


def get_company(reg_number: str) -> Dict:
    key = st.secrets.get("companies_house", {}).get("api_key")
    resp = requests.get(
        f"{BASE_URL}/company/{reg_number}",
        auth=(key, ""),
        headers={"Accept": "application/json"},
    )
    resp.raise_for_status()
    return resp.json()
