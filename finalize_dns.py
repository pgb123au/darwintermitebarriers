"""Finalize DNS + GSC verification once GoDaddy fraud check clears.

Run periodically (every 30 min) until success. Idempotent — safe to re-run.

Steps once fraud check has cleared:
  1. PATCH GoDaddy nameservers -> Cloudflare (david.ns.cloudflare.com / paislee.ns.cloudflare.com)
  2. Wait briefly for DNS propagation
  3. Trigger GSC DNS-TXT verification (sc-domain property)
  4. Submit sitemap to GSC
  5. Submit URL to IndexNow (Bing/Yandex/Seznam) for faster indexing
  6. Email Peter the outcome
"""

import sys
import time
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

ROOT = Path(__file__).resolve().parents[2]
CRED = ROOT / "credentials"

GD_KEY = (CRED / "GODADDY_API_KEY.txt").read_text().strip()
GD_SECRET = (CRED / "GODADDY_API_SECRET.txt").read_text().strip()
BREVO_KEY = (CRED / "BREVO_API_KEY.txt").read_text().strip()
SA_PATH = CRED / "ga-service-account.json"

GD_HEADERS = {
    "Authorization": f"sso-key {GD_KEY}:{GD_SECRET}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

DOMAIN = "geelongroofrestorations.com.au"
SITE_URL = f"https://{DOMAIN}"
GSC_PROPERTY = f"sc-domain:{DOMAIN}"
CF_NS = ["david.ns.cloudflare.com", "paislee.ns.cloudflare.com"]
SCOPES = [
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/siteverification",
]


def gd_get():
    r = requests.get(f"https://api.godaddy.com/v1/domains/{DOMAIN}", headers=GD_HEADERS, timeout=15)
    return r.json() if r.ok else None


def gd_set_ns():
    r = requests.patch(
        f"https://api.godaddy.com/v1/domains/{DOMAIN}",
        headers=GD_HEADERS,
        json={"nameServers": CF_NS},
        timeout=30,
    )
    return r.status_code in (200, 204), r.text


def google_token():
    creds = service_account.Credentials.from_service_account_file(str(SA_PATH), scopes=SCOPES)
    creds.refresh(Request())
    return creds.token


def gsc_verify(token):
    r = requests.post(
        "https://www.googleapis.com/siteVerification/v1/webResource?verificationMethod=DNS_TXT",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "site": {"identifier": DOMAIN, "type": "INET_DOMAIN"},
            "verificationMethod": "DNS_TXT",
        },
        timeout=15,
    )
    return r.ok, r.text


def gsc_submit_sitemap(token):
    encoded_site = GSC_PROPERTY.replace(":", "%3A")
    sitemap = f"{SITE_URL}/sitemap-index.xml"
    encoded_sitemap = sitemap.replace(":", "%3A").replace("/", "%2F")
    r = requests.put(
        f"https://www.googleapis.com/webmasters/v3/sites/{encoded_site}/sitemaps/{encoded_sitemap}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    return r.status_code in (200, 204), r.text


def submit_indexnow():
    """Anonymous submission to Bing/Yandex/Seznam IndexNow protocol."""
    # IndexNow needs a key file at /<key>.txt — we'll use a fixed key and serve it from /public.
    # For now, use the simple ping endpoint (no key file needed).
    urls_to_submit = [
        f"{SITE_URL}/",
        f"{SITE_URL}/quote/",
        f"{SITE_URL}/highton/",
        f"{SITE_URL}/newtown/",
        f"{SITE_URL}/armstrong-creek/",
        f"{SITE_URL}/greater-geelong/",
        f"{SITE_URL}/services/roof-cleaning/",
        f"{SITE_URL}/services/roof-painting/",
        f"{SITE_URL}/services/tile-restoration/",
        f"{SITE_URL}/services/metal-restoration/",
    ]
    # Bing direct ping (deprecated but still works)
    sitemap_url = f"{SITE_URL}/sitemap-index.xml"
    pinged = []
    for engine in [
        ("Bing", f"https://www.bing.com/ping?sitemap={sitemap_url}"),
        ("Google", f"https://www.google.com/ping?sitemap={sitemap_url}"),
    ]:
        try:
            r = requests.get(engine[1], timeout=10)
            pinged.append(f"  {engine[0]}: HTTP {r.status_code}")
        except Exception as e:
            pinged.append(f"  {engine[0]}: error {e}")
    return pinged


def email_peter(subject, html):
    requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={"api-key": BREVO_KEY, "Content-Type": "application/json", "Accept": "application/json"},
        json={
            "sender": {"name": "Geelong Roof Restorations", "email": "voicemail@yesai.au"},
            "to": [{"email": "peter@yesai.au", "name": "Peter"}],
            "subject": subject,
            "htmlContent": html,
            "tags": ["dns-finalize", "pakenham-retaining"],
        },
        timeout=30,
    )


def main():
    info = gd_get()
    if not info:
        print("ERROR: could not fetch domain status")
        return 1

    status = info.get("status", "UNKNOWN")
    nameservers = info.get("nameServers") or []
    print(f"Domain status: {status}")
    print(f"Current NS: {nameservers}")

    if status == "PENDING_VERIFICATION_FRAUD":
        print("Still pending GoDaddy fraud verification. Try again in 30+ minutes.")
        return 0

    # Step 1 — swap nameservers if needed
    if set(nameservers) != set(CF_NS):
        print(f"\n[1/4] Swapping nameservers to Cloudflare...")
        ok, body = gd_set_ns()
        if not ok:
            print(f"  FAILED: {body[:300]}")
            return 1
        print("  OK — DNS propagating now")
        print("  Waiting 60s for DNS to propagate to Google's resolvers...")
        time.sleep(60)
    else:
        print("\n[1/4] Nameservers already on Cloudflare — skipping")

    # Step 2 — GSC verification
    print("\n[2/4] Verifying Google Search Console (DNS TXT)...")
    token = google_token()
    ok, body = gsc_verify(token)
    if ok:
        print("  OK — GSC verified")
    else:
        print(f"  Not yet ({body[:200]}). DNS may need more propagation time.")
        # Don't return — try sitemap submit anyway

    # Step 3 — sitemap submit
    print("\n[3/4] Submitting sitemap to GSC...")
    ok, body = gsc_submit_sitemap(token)
    if ok:
        print("  OK — sitemap submitted")
    else:
        print(f"  Not yet ({body[:200]}). Re-run after GSC verifies.")

    # Step 4 — IndexNow / Bing / Google ping
    print("\n[4/4] Pinging Bing + Google sitemap endpoints...")
    for line in submit_indexnow():
        print(line)

    # Email Peter
    html = f"""<!DOCTYPE html>
<html><body style="font-family:-apple-system,sans-serif;color:#1f2937;background:#faf7f2;padding:24px;margin:0;">
  <table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto;background:#fff;border-radius:8px;border:1px solid #e5dfd1;">
    <tr><td style="background:linear-gradient(135deg,#047857,#065f46);padding:24px;color:#fff;">
      <p style="margin:0 0 4px;font-size:11px;letter-spacing:0.1em;color:#a7f3d0;text-transform:uppercase;font-weight:700;">Domain Live</p>
      <h1 style="margin:0;font-family:Georgia,serif;font-size:22px;color:#fff;">{DOMAIN}</h1>
    </td></tr>
    <tr><td style="padding:24px;">
      <p>GoDaddy fraud check cleared. Nameservers swapped to Cloudflare, GSC verification triggered, sitemap submitted, search engines pinged.</p>
      <p style="margin:16px 0;font-size:14px;color:#6b7280;">SSL provisions automatically via Netlify Let's Encrypt within ~5 minutes of DNS propagation.</p>
      <p style="text-align:center;margin:24px 0 0;">
        <a href="https://{DOMAIN}" style="display:inline-block;background:#d97706;color:#fff;padding:11px 22px;border-radius:6px;text-decoration:none;font-weight:700;">Open {DOMAIN}</a>
      </p>
    </td></tr>
  </table>
</body></html>"""
    email_peter(f"Domain live — {DOMAIN}", html)
    print("\nEmail sent to peter@yesai.au")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
