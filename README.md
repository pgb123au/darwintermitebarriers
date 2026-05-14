# Darwin Termite Barriers — rank-and-rent microsite

First in a planned series of locally-targeted lead-gen microsites. Phone calls and form leads route to a single rented contractor who pays a monthly retainer for exclusive access.

## Quick facts

| Item | Value |
|---|---|
| Domain | `darwintermitebarriers.com.au` (registered, GoDaddy fraud-pending) |
| Live URL (interim) | https://darwintermitebarriers.netlify.app |
| Phone | **(03) 9003 0108** (Telnyx, Melbourne) |
| Form action | Netlify Forms → email `peter@yesai.au` |
| Voicemail flow | Telnyx TeXML → dynamic `/.netlify/functions/voice` → record + transcribe → Brevo email to Peter |
| Forward flow (when tenant set) | Whisper "Pete's Lead" → patch caller through → email Peter when call connects, fall through to voicemail on no-answer |
| Stack | Astro 6 (static), Netlify (hosting + functions + forms), Cloudflare (DNS), Telnyx (phone), Brevo (email) |
| Registrant | Yes Right Pty Ltd, ABN 91 664 546 061 |

## Project layout

```
src/
├── layouts/Layout.astro      # site shell + LocalBusiness/WebSite schema + sticky phone CTA
├── pages/
│   ├── index.astro           # home (Pakenham primary)
│   ├── officer.astro         # /nightcliff/
│   ├── berwick.astro         # /palmerston/
│   ├── beaconsfield.astro    # /humpty-doo/
│   ├── cardinia.astro        # /greater-darwin/ (shire-wide overview)
│   ├── quote.astro           # /quote/ contact form
│   ├── thanks.astro          # post-submit
│   ├── 404.astro
│   └── services/
│       ├── timber-retaining-walls.astro
│       ├── concrete-sleeper-walls.astro
│       ├── block-retaining-walls.astro
│       └── excavation-earthworks.astro
└── styles/global.css
public/
├── voice/voicemail.xml       # Telnyx TeXML voicemail definition
├── __forms.html              # Netlify Forms detection helper
├── robots.txt
└── _redirects
netlify/functions/
├── voice.js                  # main TeXML handler — voicemail OR forward-with-whisper based on TENANT_FORWARD_NUMBER env var
├── whisper.js                # "Pete's Lead from Darwin Termite Barriers" played to contractor before patching caller through
├── forward-result.js         # emails Peter when a forwarded call connects to the contractor
├── voicemail.js              # recording_status_callback → Brevo email to Peter
└── voicemail-transcript.js   # transcribeCallback → follow-up email with the AI transcript
```

## Build & deploy

```bash
npm install
npm run build               # outputs ./dist/
netlify deploy --prod --dir=dist
```

## Service IDs (for ops/debugging)

| Service | ID |
|---|---|
| Netlify site | `a811f4bf-4aff-4e36-86d0-6ceee2650200` |
| Netlify form (`quote`) | `69febf0a8f0b410008148fbe` |
| Netlify form notification | `69febf46ea1c0e2e6ae67160` |
| Cloudflare zone | `af2566ae3eb33c3271d4f871ec1b710d` |
| Telnyx number | `+61390030108` (id `2936965401516443297`) |
| Telnyx TeXML app | `PakenhamRetainingWalls-Voicemail` (id `2955788144311535476`) |
| GoDaddy order | `4084253910` |
| GoDaddy domain id | `472416626` |

## Helper scripts

```bash
py register_domain.py --validate-only   # GoDaddy purchase validate
py register_domain.py --purchase        # actual registration (already done)
py finalize_dns.py                       # poll for fraud clearance, then swap NS to Cloudflare + email Peter
py send_status_email.py                  # one-off build report email
```

## Activating "Pete's Lead" forward to a tenant

When you find the contractor renting the site, set these Netlify env vars (Site &rarr; Settings &rarr; Environment variables) — **no code change needed**:

| Var | Example | What it does |
|---|---|---|
| `TENANT_FORWARD_NUMBER` | `+61412345678` | E.164 number of the contractor — the destination of the forwarded call |
| `TENANT_LABEL` | `Pete's Lead` (default) | The phrase whispered to the contractor before they're connected |
| `TENANT_BRAND` | `Darwin Termite Barriers` (default) | What plays after the label — full whisper is `"Pete's Lead. Pete's Lead from Darwin Termite Barriers."` |

After setting `TENANT_FORWARD_NUMBER`, all inbound calls:
1. Telnyx fetches `/voice` → sees the env var is set → returns dial-with-whisper XML
2. Caller hears ringing while contractor's phone rings
3. Contractor picks up &rarr; hears the whisper &rarr; speaks to caller
4. After the call, you get an email confirming the lead was forwarded + talk time
5. If the contractor doesn't pick up within 22 seconds, it falls through to voicemail (you still get the recording email)

To stop forwarding: delete `TENANT_FORWARD_NUMBER` (or set it empty). Calls revert to voicemail-only.

To set the env var via API instead of dashboard:

```bash
NETLIFY_TOKEN=$(cat credentials/NETLIFY_API_TOKEN.txt)
ACCOUNT="6854b409e037d5cc38ff961e"
SITE="a811f4bf-4aff-4e36-86d0-6ceee2650200"
curl -s -X POST "https://api.netlify.com/api/v1/accounts/$ACCOUNT/env?site_id=$SITE" \
  -H "Authorization: Bearer $NETLIFY_TOKEN" -H "Content-Type: application/json" \
  -d '[{"key":"TENANT_FORWARD_NUMBER","values":[{"value":"+61412345678","context":"all"}]}]'
```

## To-do once domain clears fraud check

1. `py finalize_dns.py` will swap NS automatically and email Peter.
2. Verify SSL (Netlify auto-provisions via Let's Encrypt).
3. Submit to Google Search Console (`sc-domain:darwintermitebarriers.com.au`).
4. Set up Google Business Profile (needs registered business name "Darwin Termite Barriers" first).
5. Backlink work: hipages directory, True Local AU, Yelp AU, Cardinia Shire community pages.
6. Shortlist 2–3 retaining wall contractors in Pakenham; pitch the leads with a $1,500–$2,500/mo exclusive retainer.

## Niche-fit notes

| Factor | Why this niche |
|---|---|
| Local fit | Pakenham/Cockatoo estates are sloped — demand is structural, not weather-cyclical |
| Competition | Mostly generic landscapers, no specialist site dominates the local SERP |
| Job value | $5K–$30K average; tenant happily pays $1,500–$2,500/mo |
| Resilience | Permit-driven, year-round, less seasonal than tree services |
| Phone-driven | Customers call before email for site visits |
