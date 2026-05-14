"""Register geelongroofrestorations.com.au via GoDaddy API.

Yes AI Pty Ltd as registrant, ABN 51 676 014 855.
Validates first, then optionally purchases.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]  # CC/
CRED = ROOT / "credentials"

GD_KEY = (CRED / "GODADDY_API_KEY.txt").read_text().strip()
GD_SECRET = (CRED / "GODADDY_API_SECRET.txt").read_text().strip()
HEADERS = {
    "Authorization": f"sso-key {GD_KEY}:{GD_SECRET}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

try:
    MY_IP = requests.get("https://api.ipify.org", timeout=10).text.strip()
except Exception:
    MY_IP = "203.0.113.1"

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

CONTACT = {
    "nameFirst": "Peter",
    "nameLast": "Ball",
    "email": "peter@yesai.au",
    "phone": "+61.412111000",
    "organization": "Yes Right Pty Ltd",
    "addressMailing": {
        "address1": "11 McGuire Cres",
        "city": "Williamstown",
        "state": "Victoria",
        "postalCode": "3016",
        "country": "AU",
    },
}

REGISTRATION = {
    "consent": {
        "agreedAt": NOW,
        "agreedBy": MY_IP,
        "agreementKeys": ["DNRA", "AURA"],
    },
    "domain": "geelongroofrestorations.com.au",
    "period": 1,
    "renewAuto": False,
    "legalEntityName": "Yes Right Pty Ltd",
    "legalEntityType": "COMPANY",
    "identificationType": "ABN",
    "identificationNumber": "91664546061",
    "policyReason": "CONNECTED",
    "contactRegistrant": CONTACT,
    "contactAdmin": CONTACT,
    "contactTech": CONTACT,
    "contactBilling": CONTACT,
}


def validate():
    print("Validating registration request...")
    r = requests.post(
        "https://api.godaddy.com/v1/domains/purchase/validate",
        headers=HEADERS,
        json=REGISTRATION,
        timeout=30,
    )
    print(f"Validate status: {r.status_code}")
    print(f"Body: {r.text[:1500]}")
    return r.status_code in (200, 204)


def purchase():
    print("\nPurchasing domain...")
    r = requests.post(
        "https://api.godaddy.com/v1/domains/purchase",
        headers=HEADERS,
        json=REGISTRATION,
        timeout=60,
    )
    print(f"Purchase status: {r.status_code}")
    print(f"Body: {r.text[:2000]}")
    return r


if __name__ == "__main__":
    print(f"My IP for consent: {MY_IP}")
    print(f"Domain: {REGISTRATION['domain']}")
    print(f"Registrant: {REGISTRATION['legalEntityName']} (ABN {REGISTRATION['identificationNumber']})")
    print(f"Period: {REGISTRATION['period']} year")
    print()

    if "--validate-only" in sys.argv:
        validate()
    elif "--purchase" in sys.argv:
        if validate():
            purchase()
        else:
            print("Validation failed.")
    else:
        print("Usage: python register_domain.py --validate-only | --purchase")
