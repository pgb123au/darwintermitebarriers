"""Set up GA4 property + GSC verification for Geelong Roof Restorations.

Uses ga-service-account.json (project clawdbot-mail-485923).
Creates:
  - GA4 property under account 361935568 ("Google Ads Account")
  - GA4 web data stream for geelongroofrestorations.com.au
  - GSC sc-domain property
  - DNS TXT verification record in Cloudflare
  - Triggers GSC verification
  - Submits sitemap

Outputs the GA4 measurement ID to stdout — capture it for Netlify env var.
"""

import json
import sys
import time
from pathlib import Path

import requests as rq
from google.auth.transport.requests import Request
from google.oauth2 import service_account

ROOT = Path(__file__).resolve().parents[2]
CRED = ROOT / "credentials"

SA_PATH = CRED / "ga-service-account.json"
CF_TOKEN = (CRED / "CLOUDFLARE_API_TOKEN.txt").read_text().strip()

DOMAIN = "goldcoasttermite.com.au"
SITE_URL = f"https://{DOMAIN}"
GSC_PROPERTY = f"sc-domain:{DOMAIN}"
CF_ZONE_ID = "38e0a42da00bed4b2a3a740ec0a7a97e"

GA4_ACCOUNT = "accounts/361935568"
PROPERTY_NAME = "Gold Coast Termite Specialists"
STREAM_NAME = "Web"
TIMEZONE = "Australia/Brisbane"
CURRENCY = "AUD"
INDUSTRY = "BUSINESS_AND_INDUSTRIAL_MARKETS"

SCOPES = [
    "https://www.googleapis.com/auth/analytics.edit",
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/siteverification",
]


def get_token():
    creds = service_account.Credentials.from_service_account_file(str(SA_PATH), scopes=SCOPES)
    creds.refresh(Request())
    return creds.token


def gh(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def cf(method, path, **kw):
    return rq.request(
        method,
        f"https://api.cloudflare.com/client/v4{path}",
        headers={"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"},
        timeout=15,
        **kw,
    )


def find_existing_property(token):
    """Return property name (e.g. 'properties/12345') if one exists for this site."""
    r = rq.get(
        f"https://analyticsadmin.googleapis.com/v1beta/properties?filter=parent:{GA4_ACCOUNT}",
        headers=gh(token),
        timeout=15,
    )
    if not r.ok:
        return None
    for p in r.json().get("properties", []):
        if p.get("displayName") == PROPERTY_NAME:
            return p["name"]
    return None


def create_ga4_property(token):
    existing = find_existing_property(token)
    if existing:
        print(f"  [GA4] property already exists: {existing}")
        return existing

    body = {
        "parent": GA4_ACCOUNT,
        "displayName": PROPERTY_NAME,
        "industryCategory": INDUSTRY,
        "timeZone": TIMEZONE,
        "currencyCode": CURRENCY,
    }
    r = rq.post(
        "https://analyticsadmin.googleapis.com/v1beta/properties",
        headers=gh(token),
        json=body,
        timeout=15,
    )
    print(f"  [GA4] create property: {r.status_code}")
    if not r.ok:
        print(f"    body: {r.text[:400]}")
        return None
    return r.json()["name"]


def create_data_stream(token, property_name):
    # Check existing
    r = rq.get(
        f"https://analyticsadmin.googleapis.com/v1beta/{property_name}/dataStreams",
        headers=gh(token),
        timeout=15,
    )
    if r.ok:
        for ds in r.json().get("dataStreams", []):
            if ds.get("displayName") == STREAM_NAME:
                print(f"  [GA4] data stream already exists: {ds['name']}")
                return ds.get("webStreamData", {}).get("measurementId"), ds["name"]

    body = {
        "displayName": STREAM_NAME,
        "type": "WEB_DATA_STREAM",
        "webStreamData": {"defaultUri": SITE_URL},
    }
    r = rq.post(
        f"https://analyticsadmin.googleapis.com/v1beta/{property_name}/dataStreams",
        headers=gh(token),
        json=body,
        timeout=15,
    )
    print(f"  [GA4] create data stream: {r.status_code}")
    if not r.ok:
        print(f"    body: {r.text[:400]}")
        return None, None
    j = r.json()
    return j.get("webStreamData", {}).get("measurementId"), j["name"]


def gsc_get_token(token):
    """Get the DNS TXT verification token for the domain."""
    body = {
        "site": {"identifier": DOMAIN, "type": "INET_DOMAIN"},
        "verificationMethod": "DNS_TXT",
    }
    r = rq.post(
        "https://www.googleapis.com/siteVerification/v1/token",
        headers=gh(token),
        json=body,
        timeout=15,
    )
    print(f"  [GSC] get verification token: {r.status_code}")
    if not r.ok:
        print(f"    body: {r.text[:400]}")
        return None
    return r.json().get("token")


def cloudflare_add_txt(verification_token):
    # Idempotency: check if TXT already exists
    r = cf("GET", f"/zones/{CF_ZONE_ID}/dns_records?type=TXT&name={DOMAIN}")
    for rec in r.json().get("result", []):
        if "google-site-verification" in rec.get("content", ""):
            # Update existing
            rid = rec["id"]
            cf("PATCH", f"/zones/{CF_ZONE_ID}/dns_records/{rid}", json={
                "type": "TXT",
                "name": DOMAIN,
                "content": verification_token,
                "ttl": 1,
            })
            print(f"  [CF] updated existing TXT record {rid}")
            return True

    r = cf("POST", f"/zones/{CF_ZONE_ID}/dns_records", json={
        "type": "TXT",
        "name": DOMAIN,
        "content": verification_token,
        "ttl": 1,
        "comment": "Google Search Console verification",
    })
    print(f"  [CF] add TXT record: {r.status_code}")
    return r.ok


def gsc_add_site(token):
    # PUT /webmasters/v3/sites/{siteUrl}
    encoded = GSC_PROPERTY.replace(":", "%3A")
    r = rq.put(
        f"https://www.googleapis.com/webmasters/v3/sites/{encoded}",
        headers=gh(token),
        timeout=15,
    )
    print(f"  [GSC] add site: {r.status_code}")
    return r.status_code in (200, 204)


def gsc_verify(token, vtoken):
    body = {
        "site": {"identifier": DOMAIN, "type": "INET_DOMAIN"},
        "verificationMethod": "DNS_TXT",
    }
    r = rq.post(
        f"https://www.googleapis.com/siteVerification/v1/webResource?verificationMethod=DNS_TXT",
        headers=gh(token),
        json=body,
        timeout=15,
    )
    print(f"  [GSC] verify: {r.status_code}")
    if not r.ok:
        print(f"    body: {r.text[:400]}")
    return r.ok


def gsc_submit_sitemap(token):
    encoded_site = GSC_PROPERTY.replace(":", "%3A")
    sitemap = f"{SITE_URL}/sitemap-index.xml"
    encoded_sitemap = sitemap.replace(":", "%3A").replace("/", "%2F")
    r = rq.put(
        f"https://www.googleapis.com/webmasters/v3/sites/{encoded_site}/sitemaps/{encoded_sitemap}",
        headers=gh(token),
        timeout=15,
    )
    print(f"  [GSC] submit sitemap: {r.status_code}")
    return r.status_code in (200, 204)


def main():
    print("Getting OAuth token...")
    token = get_token()
    print()

    print("== GA4 ==")
    prop_name = create_ga4_property(token)
    if not prop_name:
        print("  FAILED to create GA4 property")
        return 1
    measurement_id, stream_name = create_data_stream(token, prop_name)
    if not measurement_id:
        print("  FAILED to create data stream")
        return 1
    print(f"  Property: {prop_name}")
    print(f"  Stream:   {stream_name}")
    print(f"  Measurement ID: {measurement_id}")
    print()

    print("== GSC ==")
    print("  Adding site to GSC...")
    gsc_add_site(token)

    print("  Getting DNS TXT verification token...")
    vtoken = gsc_get_token(token)
    if not vtoken:
        print("  FAILED to get verification token")
        return 1
    print(f"  Verification token: {vtoken[:50]}...")

    print("  Adding TXT record to Cloudflare...")
    cloudflare_add_txt(vtoken)

    print("  Waiting 10s for DNS propagation...")
    time.sleep(10)

    print("  Verifying with Google...")
    gsc_verify(token, vtoken)

    print("  Submitting sitemap (will succeed once DNS resolves to site)...")
    gsc_submit_sitemap(token)
    print()

    print("=" * 60)
    print("DONE.")
    print(f"  GA4 Measurement ID: {measurement_id}")
    print(f"  GSC property: {GSC_PROPERTY}")
    print()
    print("Next: set PUBLIC_GA4_ID env var on Netlify, rebuild, deploy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
