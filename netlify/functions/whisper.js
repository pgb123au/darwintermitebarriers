// Whisper — played to the contractor BEFORE patching the caller through.
// The caller hears ringing while the contractor hears this announcement,
// so they know the lead is a Peter-sourced lead (not a random direct call).
//
// Brand-neutral by design — the shared (03) 9003 0108 line serves multiple
// VIC rank-and-rent sites, so the whisper just identifies the *source* (Peter),
// not a specific brand. The contractor can ask the caller "which site did you
// find us on?" if they need to know.
//
// Configurable via Netlify env vars (only `TENANT_LABEL` is used here):
//   TENANT_LABEL  — default "Pete's Lead"

exports.handler = async () => {
  const label = (process.env.TENANT_LABEL || "Pete's lead").trim();

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Nicole-Neural" language="en-AU">${label}. ${label}.</Say>
  <Pause length="1"/>
</Response>`;

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/xml; charset=utf-8" },
    body: xml,
  };
};
