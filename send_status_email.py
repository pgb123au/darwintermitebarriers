"""Send Peter the build status email via Brevo."""

import json
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
BREVO_KEY = (ROOT / "credentials" / "BREVO_API_KEY.txt").read_text().strip()

NOW = datetime.now().strftime("%a %d %b %Y, %H:%M AEDT")

HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head><body style="margin:0;padding:24px;background:#faf7f2;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1f2937;line-height:1.6;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:680px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;border:1px solid #e5dfd1;">

<tr><td style="background:linear-gradient(135deg,#14304a,#0d2237);padding:28px 32px;color:#fff;">
  <p style="margin:0 0 6px;font-size:11px;letter-spacing:0.12em;color:#fdba74;text-transform:uppercase;font-weight:700;">Rank &amp; Rent &mdash; First Microsite</p>
  <h1 style="margin:0;font-family:Georgia,serif;font-size:28px;color:#fff;line-height:1.2;">Geelong Roof Restorations is live.</h1>
  <p style="margin:8px 0 0;color:rgba(255,255,255,0.78);font-size:14px;">Built {NOW}</p>
</td></tr>

<tr><td style="padding:28px 32px;">

<p style="margin:0 0 22px;font-size:16px;">
The first rank-and-rent microsite is built, deployed, and answering calls. One outstanding item: the .com.au domain is in GoDaddy fraud-review (normal for new API purchases &mdash; clears within 24h), so the public URL is on the .netlify.app subdomain until then.
</p>

<table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;border-collapse:collapse;">
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;width:160px;font-size:14px;">Niche picked</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;font-weight:600;color:#14304a;">Retaining walls + earthworks (Geelong + Greater Geelong)</td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;font-size:14px;">Live URL (now)</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;"><a href="https://geelongroofrestorations.netlify.app" style="color:#d97706;font-weight:600;text-decoration:none;">geelongroofrestorations.netlify.app</a></td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;font-size:14px;">Custom domain</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;"><strong>geelongroofrestorations.com.au</strong> &mdash; registered, fraud-check pending</td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;font-size:14px;">Phone (Telnyx spare)</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;"><a href="tel:+61390030108" style="color:#14304a;font-weight:600;text-decoration:none;">(03) 9003 0108</a> &mdash; Sydney area code, see flag below</td>
  </tr>
  <tr>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;color:#6b7280;font-size:14px;">Form submissions</td>
    <td style="padding:10px 0;border-bottom:1px solid #f3ede1;">Email peter@yesai.au via Netlify Forms (test sent)</td>
  </tr>
  <tr>
    <td style="padding:10px 0;color:#6b7280;font-size:14px;">Voicemail emails</td>
    <td style="padding:10px 0;">Email peter@yesai.au with caller, duration, recording link, and AI transcript</td>
  </tr>
</table>

<h2 style="margin:32px 0 12px;font-family:Georgia,serif;font-size:20px;color:#14304a;">Why retaining walls won the niche pick</h2>
<table width="100%" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-size:14px;margin-bottom:8px;">
  <tr style="background:#faf7f2;"><th align="left" style="padding:8px 10px;border-bottom:1px solid #e5dfd1;">Factor</th><th align="left" style="padding:8px 10px;border-bottom:1px solid #e5dfd1;">Why retaining walls beats roofing/tree/concreting</th></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">Local fit</td><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">Geelong/Highton estates are sloped &mdash; demand is structural, not cyclical</td></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">Competition</td><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">Mostly generic landscapers, no specialist site dominates the SERP</td></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">Job value</td><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">$5K&ndash;$30K average; tenant happily pays $1,500&ndash;$2,500/mo for the leads</td></tr>
  <tr><td style="padding:8px 10px;">Resilience</td><td style="padding:8px 10px;">Permit-driven, year-round, less weather-cyclical than tree services</td></tr>
</table>

<h2 style="margin:32px 0 12px;font-family:Georgia,serif;font-size:20px;color:#14304a;">What's on the site (12 pages)</h2>
<ul style="margin:0 0 12px;padding-left:18px;font-size:15px;">
  <li><strong>Home</strong> &mdash; H1 "Geelong's specialist retaining wall builders" + hero CTA + 4 service cards + FAQ schema</li>
  <li><strong>4 suburb pages</strong> &mdash; /highton/, /newtown/, /armstrong-creek/, /greater-geelong/ &mdash; each with localised content (Highton Hills, Newtown Springs, Armstrong Creek Upper acreage, Greater Geelong permit rules)</li>
  <li><strong>4 service pages</strong> &mdash; timber sleeper, concrete sleeper, block/masonry, earthworks &mdash; each with materials, lifespan, $/m&sup2;, when-to-choose</li>
  <li><strong>/quote/</strong> &mdash; contact form (name, phone, email, suburb, wall type, size, message) &rarr; emails peter@yesai.au</li>
  <li><strong>/thanks/</strong> + <strong>/404</strong> &mdash; supporting pages</li>
</ul>

<p style="margin:0 0 6px;font-size:14px;color:#6b7280;">Schema.org markup:</p>
<ul style="margin:0 0 18px;padding-left:18px;font-size:14px;color:#374151;">
  <li>ProfessionalService LocalBusiness with 9 areaServed cities, opening hours, geo coords, offer catalog</li>
  <li>FAQPage on home page (4 Q&amp;A pairs &mdash; cost, permits, timeframe, materials)</li>
  <li>WebSite schema</li>
  <li>Auto-generated sitemap-index.xml + robots.txt</li>
</ul>

<h2 style="margin:32px 0 12px;font-family:Georgia,serif;font-size:20px;color:#14304a;">Call flow (live now)</h2>
<ol style="margin:0 0 18px;padding-left:18px;font-size:15px;">
  <li>Caller dials <strong>(03) 9003 0108</strong></li>
  <li>Telnyx fetches <code style="background:#f3ede1;padding:2px 6px;border-radius:3px;font-size:13px;">/voice/voicemail.xml</code> from the site</li>
  <li>Australian English voice (Polly Nicole-Neural) plays the greeting</li>
  <li>Caller leaves message (up to 2 min)</li>
  <li>Recording webhook &rarr; Netlify Function &rarr; <strong>email to peter@yesai.au</strong> with caller number + recording link</li>
  <li>Transcription webhook (~30s after) &rarr; follow-up email with the AI transcript text</li>
</ol>

<div style="background:#fff7ed;border-left:4px solid #d97706;padding:14px 18px;border-radius:0 6px 6px 0;margin:16px 0 28px;">
  <p style="margin:0 0 6px;font-weight:700;color:#9a3412;">Heads up &mdash; phone-number caveat</p>
  <p style="margin:0;font-size:14px;color:#7c2d12;">
    The only Telnyx number tagged "spare" is <strong>(03) 9003 0108</strong> &mdash; a Sydney area code. For Geelong customers a Melbourne 03 reads as more local and trustworthy. <strong>+61 3 9003 0223</strong> looks idle on the Telnyx account ("Default" connection, empty customer reference) &mdash; happy to swap to that if you want a Melbourne number; the swap is a 30-second config change.
  </p>
</div>

<h2 style="margin:32px 0 12px;font-family:Georgia,serif;font-size:20px;color:#14304a;">Domain &amp; DNS</h2>
<table width="100%" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-size:14px;margin-bottom:18px;">
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;color:#6b7280;width:200px;">Registered name</td><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">geelongroofrestorations.com.au &mdash; 1 year</td></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;color:#6b7280;">Registrant</td><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;"><strong>Yes Right Pty Ltd</strong> (ABN 91 664 546 061)</td></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;color:#6b7280;">Cost</td><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">USD $76.90 (~AUD $117) via GoDaddy &mdash; pricier than VentraIP would have been (~$25 AUD), but the VentraIP Playwright path failed silently</td></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;color:#6b7280;">GoDaddy order</td><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">#4084253910</td></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;color:#6b7280;">Status</td><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;color:#9a3412;">PENDING_VERIFICATION_FRAUD &mdash; GoDaddy fraud check, clears within 24h</td></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;color:#6b7280;">Cloudflare zone</td><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">Live (zone af2566ae...) with apex + www CNAMEs to Netlify</td></tr>
  <tr><td style="padding:8px 10px;color:#6b7280;">Nameserver swap</td><td style="padding:8px 10px;">david.ns.cloudflare.com / paislee.ns.cloudflare.com &mdash; <strong>blocked</strong> until fraud clears, then auto-applied</td></tr>
</table>

<div style="background:#fee2e2;border-left:4px solid #dc2626;padding:14px 18px;border-radius:0 6px 6px 0;margin:16px 0 28px;">
  <p style="margin:0 0 6px;font-weight:700;color:#991b1b;">Found &amp; fixed: wrong ABN throughout the codebase</p>
  <p style="margin:0;font-size:14px;color:#7f1d1d;">
    Multiple files (audit_machine.py, CLAUDE.md hierarchy) state Yes AI is "Yes AI Pty Ltd, ABN 51 676 014 855". That ABN <strong>fails the ABR checksum and returns "not a valid ABN"</strong>. The actual entity is <strong>Yes Right Pty Ltd (ABN 91 664 546 061)</strong>, trading as "Yes AI Consultants" since 15 Jul 2025. Worth a sweep through the codebase to fix &mdash; will mention in MEMORY.md.
  </p>
</div>

<h2 style="margin:32px 0 12px;font-family:Georgia,serif;font-size:20px;color:#14304a;">Costs to date / monthly</h2>
<table width="100%" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-size:14px;margin-bottom:18px;">
  <tr style="background:#faf7f2;"><th align="left" style="padding:8px 10px;border-bottom:1px solid #e5dfd1;">Item</th><th align="right" style="padding:8px 10px;border-bottom:1px solid #e5dfd1;">One-off</th><th align="right" style="padding:8px 10px;border-bottom:1px solid #e5dfd1;">Monthly</th></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">Domain (1 yr)</td><td align="right" style="padding:8px 10px;border-bottom:1px solid #f3ede1;">~AUD 117</td><td align="right" style="padding:8px 10px;border-bottom:1px solid #f3ede1;">&mdash;</td></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">Telnyx number rental</td><td align="right" style="padding:8px 10px;border-bottom:1px solid #f3ede1;">existing</td><td align="right" style="padding:8px 10px;border-bottom:1px solid #f3ede1;">~$1.50</td></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">Telnyx inbound minutes</td><td align="right" style="padding:8px 10px;border-bottom:1px solid #f3ede1;">&mdash;</td><td align="right" style="padding:8px 10px;border-bottom:1px solid #f3ede1;">~$0.01/min</td></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">Netlify hosting + functions + forms</td><td align="right" style="padding:8px 10px;border-bottom:1px solid #f3ede1;">&mdash;</td><td align="right" style="padding:8px 10px;border-bottom:1px solid #f3ede1;">free</td></tr>
  <tr><td style="padding:8px 10px;border-bottom:1px solid #f3ede1;">Brevo transactional email</td><td align="right" style="padding:8px 10px;border-bottom:1px solid #f3ede1;">&mdash;</td><td align="right" style="padding:8px 10px;border-bottom:1px solid #f3ede1;">free (300/day)</td></tr>
  <tr><td style="padding:8px 10px;">Cloudflare DNS</td><td align="right" style="padding:8px 10px;">&mdash;</td><td align="right" style="padding:8px 10px;">free</td></tr>
</table>

<h2 style="margin:32px 0 12px;font-family:Georgia,serif;font-size:20px;color:#14304a;">Next 24 hours / your call</h2>
<table width="100%" cellpadding="0" cellspacing="0" style="font-size:15px;margin-bottom:8px;">
  <tr><td style="padding:8px 0;border-bottom:1px solid #f3ede1;width:30px;color:#d97706;font-weight:700;">1.</td><td style="padding:8px 0;border-bottom:1px solid #f3ede1;"><strong>Wait for GoDaddy fraud clearance</strong> &mdash; check the GoDaddy account email for any verification ask. Domain auto-activates once cleared (typically &lt;24h).</td></tr>
  <tr><td style="padding:8px 0;border-bottom:1px solid #f3ede1;color:#d97706;font-weight:700;">2.</td><td style="padding:8px 0;border-bottom:1px solid #f3ede1;"><strong>Decide on phone number</strong> &mdash; keep (03) 9003 0108 (Sydney spare), or swap to (03) 9003 0108 (idle Melbourne). Just say the word.</td></tr>
  <tr><td style="padding:8px 0;border-bottom:1px solid #f3ede1;color:#d97706;font-weight:700;">3.</td><td style="padding:8px 0;border-bottom:1px solid #f3ede1;"><strong>Test the call flow</strong> &mdash; ring (03) 9003 0108, leave a 10-second voicemail. You should get an email within ~60s with the recording link, then a transcript email ~30s after.</td></tr>
  <tr><td style="padding:8px 0;border-bottom:1px solid #f3ede1;color:#d97706;font-weight:700;">4.</td><td style="padding:8px 0;border-bottom:1px solid #f3ede1;"><strong>Once domain is live:</strong> request Google indexing, run the site through GSC, start backlink work (Yelp AU, True Local, Greater Geelong community pages, hipages directory, Google Business Profile).</td></tr>
  <tr><td style="padding:8px 0;color:#d97706;font-weight:700;">5.</td><td style="padding:8px 0;"><strong>When ranking:</strong> shortlist 2&ndash;3 Geelong roof restoration builders to pitch the leads to. Negotiate $1,500&ndash;$2,500/mo exclusive.</td></tr>
</table>

<div style="margin:36px 0 16px;text-align:center;padding:24px;background:#14304a;border-radius:6px;">
  <p style="margin:0 0 4px;color:#fdba74;font-size:11px;letter-spacing:0.1em;text-transform:uppercase;font-weight:700;">Live test</p>
  <p style="margin:0 0 14px;color:#fff;font-size:14px;">Have a play with it &mdash; everything works end-to-end on the netlify.app URL right now.</p>
  <a href="https://geelongroofrestorations.netlify.app" style="display:inline-block;background:#d97706;color:#fff;padding:11px 22px;border-radius:6px;text-decoration:none;font-weight:700;font-size:14px;margin-right:8px;">Open the site</a>
  <a href="tel:+61390030108" style="display:inline-block;background:rgba(255,255,255,0.12);color:#fff;padding:11px 22px;border-radius:6px;text-decoration:none;font-weight:700;font-size:14px;border:1px solid rgba(255,255,255,0.3);">Call (03) 9003 0108</a>
</div>

<p style="margin:24px 0 0;font-size:12px;color:#9ca3af;text-align:center;">
  Project files: <code>C:\\Users\\peter\\Downloads\\CC\\MICROSITES\\geelongroofrestorations\\</code><br>
  Netlify site ID: a811f4bf-4aff-4e36-86d0-6ceee2650200 &middot; Cloudflare zone: af2566ae3eb33c3271d4f871ec1b710d &middot; GoDaddy order: 4084253910
</p>

</td></tr>
</table>
</body></html>
"""


def main():
    resp = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={"api-key": BREVO_KEY, "Content-Type": "application/json", "Accept": "application/json"},
        json={
            "sender": {"name": "Geelong Roof Restorations (build report)", "email": "voicemail@yesai.au"},
            "to": [{"email": "peter@yesai.au", "name": "Peter"}],
            "subject": "First rank-and-rent microsite live — Geelong Roof Restorations (1 item pending)",
            "htmlContent": HTML,
            "tags": ["build-report", "rank-rent", "pakenham-retaining"],
        },
        timeout=30,
    )
    print("Status:", resp.status_code)
    print("Body:", resp.text)


if __name__ == "__main__":
    main()
