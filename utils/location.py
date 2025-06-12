# utils/location.py

import requests

# Step 1: Get the country from IP address
def get_country_from_ip(ip_address):
    try:
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        if response.status_code == 200:
            return response.json().get("country", "US")
        return "US"
    except:
        return "US"

# Step 2: Country → Default currency
country_to_currency = {
    "US": "USD", "LB": "LBP", "FR": "EUR", "DE": "EUR",
    "GB": "GBP", "AE": "AED", "IN": "INR", "JP": "JPY",
    "CA": "CAD", "TR": "TRY", "EG": "EGP"
}

def get_currency_for_country(country_code):
    return country_to_currency.get(country_code, "USD")

# Step 3: Optional travel suggestions
def get_travel_currency_suggestions(country_code):
    nearby = {
        "LB": ["USD", "EUR", "AED"],
        "FR": ["EUR", "CHF", "GBP"],
        "US": ["CAD", "MXN", "USD"],
        "AE": ["SAR", "KWD", "USD"]
    }
    return nearby.get(country_code, ["USD", "EUR"])
