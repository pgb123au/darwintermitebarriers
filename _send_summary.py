"""Send Peter the build status email via Brevo transactional."""
from __future__ import annotations
from pathlib import Path
import requests
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
BREVO_KEY = (ROOT / "credentials" / "BREVO_API_KEY.txt").read_text().strip()

NOW = datetime.now().strftime("%a %d %b %Y, %H:%M")

HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:24px;background:#faf7f2;font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#1f2937;line-height:1.6;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:720px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;border:1px solid #e5dfd1;">

<tr><td style="background:linear-gradient(135deg,#14304a,#0d2237);padding:28px 32px;color:#fff;">
  <p style="margin:0 0 6px;font-size:11px;letter-spacing:0.12em;color:#fdba74;text-transform:uppercase;font-weight:700;">Rank &amp; Rent &mdash; Microsite #2</p>
  <h1 style="margin:0;font-family:Georgia,serif;font-size:28px;color:#fff;line-height:1.2;">Geelong Roof Restorations &mdash; built, deployed, partial.</h1>
  <p style="margin:8px 0 0;color:rgba(255,255,255,0.78);font-size:14px;">{NOW}</p>
</td></tr>

<tr><td style="padding:28px 32px;">

<p style="margin:0 0 22px;font-size:16px;">
Site is built and deployed. <strong>Two action items still need you</strong> &mdash; both are documented in the &ldquo;Your turn&rdquo; section below.
</p>

<h2 style="margin:24px 0 10px;font-size:18px;color:#14304a;font-family:Georgia,serif;">What&rsquo;s done</h2>
<table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 18px;border-collapse:collapse;font-size:14px;">
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;width:200px;">Live URL (Netlify subdomain)</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;"><a href="https://geelongroofrestorations.netlify.app" style="color:#d97706;font-weight:600;text-decoration:none;">geelongroofrestorations.netlify.app</a></td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">Custom domain (pending registration)</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;"><strong>geelongroofrestorations.com.au</strong> &mdash; not yet registered (Chrome window is open for you, see action items)</td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">Phone (TEMP)</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;"><a href="tel:+61390030108" style="color:#14304a;font-weight:600;text-decoration:none;">(03) 9003 0108</a> &mdash; reassigned from Reignite demo to a new <code>GeelongRoofRestorations-Voicemail</code> TeXML app, ready to take calls</td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">Phone (target, regulatory pending)</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;"><strong>0485 939 9966</strong> (live) + <strong>0485 813 8822</strong> (spare for next build) &mdash; both ordered, 5/7 regulatory fields filled, 2 still need you (DOB + Onfido)</td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">Pages built</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;">15 (5 service + 5 suburb + hub + index + quote + thanks + 404)</td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">Cloudflare zone</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;">Created &mdash; NS: <code>david.ns.cloudflare.com</code>, <code>paislee.ns.cloudflare.com</code>. CNAME records for apex + www point to Netlify, proxied.</td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">GA4 measurement ID</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;"><code>G-74D0YM2F9L</code> (property 536867820)</td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">GSC property</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;"><code>sc-domain:geelongroofrestorations.com.au</code> &mdash; verification token in Layout.astro and DNS TXT, will pass once NS swap lands</td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">GitHub repo</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;"><a href="https://github.com/pgb123au/geelongroofrestorations" style="color:#d97706;text-decoration:none;">pgb123au/geelongroofrestorations</a> (public)</td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">Netlify form submissions</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;">Will hit Netlify dashboard &mdash; manual email-hook setup required (API path 404'd, can wire later)</td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">Backlink drafts</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;">Medium article (Bass Strait salt-zone), 2 LinkedIn posts, directory NAP &mdash; all in <code>backlinks/</code></td>
  </tr>
</table>

<h2 style="margin:24px 0 10px;font-size:18px;color:#14304a;font-family:Georgia,serif;">Your turn (two manual steps)</h2>

<table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 18px;border-collapse:collapse;font-size:14px;">
  <tr>
    <td style="padding:14px;background:#fef3c7;border:1px solid #fbbf24;border-radius:6px;">
      <p style="margin:0 0 8px;font-weight:700;color:#7c2d12;">1. Complete VentraIP domain registration</p>
      <p style="margin:0 0 8px;">A headed Chrome window is open with the VIPControl ordering form. Search for <strong>geelongroofrestorations.com.au</strong>, proceed through the eligibility step (CONNECTED &mdash; Yes Right Pty Ltd, ABN 91 664 546 061), confirm the purchase. Once it appears in your account, NS swap to Cloudflare will be a one-liner.</p>
      <p style="margin:0;font-size:12px;color:#7c2d12;">If Chrome closed: re-run <code>python C:\\Users\\peter\\Downloads\\CC\\scripts\\ventraip\\register_geelong_v2.py</code> (no auto-close on this version).</p>
    </td>
  </tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 18px;border-collapse:collapse;font-size:14px;">
  <tr>
    <td style="padding:14px;background:#fef3c7;border:1px solid #fbbf24;border-radius:6px;">
      <p style="margin:0 0 8px;font-weight:700;color:#7c2d12;">2. Telnyx mobile bundle &mdash; DOB + Onfido</p>
      <p style="margin:0 0 6px;">Both 0485 numbers are ordered (orders <code>77d20ee2&hellip;</code> live, <code>0da3cacc&hellip;</code> spare). Five of seven regulatory fields submitted via API:</p>
      <ul style="margin:6px 0 8px 18px;padding:0;font-size:13px;">
        <li>Proof of Address: Statement of Account.pdf (existing on file)</li>
        <li>Contact info: Peter Ball / Yes Right Pty Ltd / +61412111000</li>
        <li>In-service AU mobile numbers: None</li>
        <li>Purchaser/Service Activator: Yes Right Pty Ltd / Peter Ball as End User Name</li>
        <li>Physical address: 11 McGuire Cres Williamstown VIC 3016 (address ID on file)</li>
      </ul>
      <p style="margin:0 0 6px;font-weight:600;">Two fields still need you:</p>
      <ul style="margin:6px 0 8px 18px;padding:0;font-size:13px;">
        <li><strong>DOB</strong> &mdash; submit via Telnyx dashboard (Order &rarr; Regulatory) in YYYY-MM-DD format. Field ID <code>d341dbfb-ef9d-41d8-bb40-247a1347c6f7</code>.</li>
        <li><strong>Onfido ID verification</strong> &mdash; trigger via Telnyx dashboard (sends a personal link to your phone for biometric + ID upload). Field ID <code>b7c72fb8-fa08-4529-aaf6-b9117d3f3698</code>.</li>
      </ul>
      <p style="margin:0;font-size:13px;">Once those land, Telnyx reviews the bundle (1&ndash;72hr) and the 0485 numbers activate. The site keeps using <strong>(03) 9003 0108</strong> until then &mdash; calls work today.</p>
    </td>
  </tr>
</table>

<h2 style="margin:24px 0 10px;font-size:18px;color:#14304a;font-family:Georgia,serif;">Once the domain registers (auto-finish list)</h2>
<ol style="margin:0 0 18px 22px;padding:0;font-size:14px;">
  <li>VentraIP NS swap to <code>david.ns.cloudflare.com</code> + <code>paislee.ns.cloudflare.com</code> (one PATCH call &mdash; I can do this from a follow-up session)</li>
  <li>Cloudflare zone goes active</li>
  <li>Site reachable at <strong>https://geelongroofrestorations.com.au/</strong></li>
  <li>GSC verification clicks through (token already in HTML + DNS TXT)</li>
  <li>Sitemap submission goes through</li>
  <li>Once mobile bundle approves: PATCH 0485 939 9966 to the GeelongRoofRestorations-Voicemail TeXML app, swap (03) 9003 0108 back to Reignite if needed, search-replace 0108 &rarr; 9966 in the Astro template, redeploy</li>
</ol>

<h2 style="margin:24px 0 10px;font-size:18px;color:#14304a;font-family:Georgia,serif;">Costs charged today</h2>
<table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 18px;border-collapse:collapse;font-size:14px;">
  <tr><td style="padding:8px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">Telnyx 0485 939 9966 (live, pending bundle)</td><td style="padding:8px 0;border-bottom:1px solid #f3ede1;text-align:right;">$12.00 USD when activated</td></tr>
  <tr><td style="padding:8px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">Telnyx 0485 813 8822 (spare, pending bundle)</td><td style="padding:8px 0;border-bottom:1px solid #f3ede1;text-align:right;">$12.00 USD when activated</td></tr>
  <tr><td style="padding:8px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">VentraIP .com.au (1yr)</td><td style="padding:8px 0;border-bottom:1px solid #f3ede1;text-align:right;">~$15 AUD when you confirm</td></tr>
  <tr><td style="padding:8px 0;border-bottom:1px solid #f3ede1;color:#6b7280;">Cloudflare / Netlify / GitHub / GA4 / GSC</td><td style="padding:8px 0;border-bottom:1px solid #f3ede1;text-align:right;">$0</td></tr>
  <tr><td style="padding:8px 0;color:#6b7280;font-weight:600;">Recurring: Telnyx mobile rent</td><td style="padding:8px 0;text-align:right;font-weight:600;">~$11 USD/mo (~$17 AUD)</td></tr>
</table>

<h2 style="margin:24px 0 10px;font-size:18px;color:#14304a;font-family:Georgia,serif;">Files</h2>
<pre style="background:#f8f5ee;border:1px solid #e5dfd1;border-radius:6px;padding:14px;font-size:12px;line-height:1.45;overflow-x:auto;">C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\layouts\\Layout.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\index.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\quote.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\thanks.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\404.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\highton.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\newtown.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\belmont.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\armstrong-creek.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\lara.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\greater-geelong.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\services\\roof-cleaning.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\services\\roof-painting.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\services\\tile-restoration.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\services\\metal-restoration.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\src\\pages\\services\\gutter-replacement.astro
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\backlinks\\medium-article.md
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\backlinks\\linkedin-post.md
C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\backlinks\\directory-listings.md
C:\\Users\\peter\\Downloads\\CC\\scripts\\ventraip\\register_geelong_v2.py
C:\\Users\\peter\\Downloads\\CC\\infrastructure\\Telcos\\PHONE_NUMBER_ASSIGNMENTS.md (updated)</pre>

<p style="margin:24px 0 0;font-size:13px;color:#6b7280;">
<strong>Recap:</strong> microsite live on .netlify.app subdomain with full Geelong/Bellarine/Surf-Coast content (5 services, 5 suburbs, hub). Two manual items remain: VentraIP confirm + Telnyx DOB/Onfido. Site uses (03) 9003 0108 today, swaps to 0485 939 9966 when bundle approves.
</p>

</td></tr>
</table>
</body></html>
"""

resp = requests.post(
    "https://api.brevo.com/v3/smtp/email",
    headers={"api-key": BREVO_KEY, "Content-Type": "application/json"},
    json={
        "sender": {"name": "Microsite Build", "email": "voicemail@yesai.au"},
        "to": [{"email": "peter@yesai.au", "name": "Peter Ball"}],
        "subject": "New rank-and-rent microsite live - Geelong Roof Restorations (2 items still need you)",
        "htmlContent": HTML,
    },
    timeout=30,
)
print(f"HTTP {resp.status_code}")
print(resp.text[:500])
