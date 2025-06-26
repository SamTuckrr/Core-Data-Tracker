# cqc_api.py
import os
import requests
from datetime import datetime

CQC_API_KEY = os.getenv("CQC_API_KEY")
CQC_API_BASE_URL = "https://api.service.cqc.org.uk/public/v1"

HEADERS = {
    "Ocp-Apim-Subscription-Key": CQC_API_KEY
}

# === Utility: Format Dates ===
def iso_date(date_obj):
    return date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")

# === GET /changes/location ===
def get_changes(start_date, end_date):
    url = f"{CQC_API_BASE_URL}/changes/location"
    params = {
        "startTimestamp": iso_date(start_date),
        "endTimestamp": iso_date(end_date)
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json().get("items", [])

# === GET /locations/{id} ===
def get_location_by_id(location_id):
    url = f"{CQC_API_BASE_URL}/locations/{location_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# === GET /providers/{id} ===
def get_provider_by_id(provider_id):
    url = f"{CQC_API_BASE_URL}/providers/{provider_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# === Optional: Search locations with filters ===
def search_locations(region=None, rating=None, page=1, per_page=25):
    url = f"{CQC_API_BASE_URL}/locations"
    params = {
        "page": page,
        "perPage": per_page
    }
    if region:
        params["region"] = region
    if rating:
        params["overallRating"] = rating

    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json().get("items", [])

