// Forward result — hit by Telnyx after the <Dial> verb completes.
// Lets us email Peter when a forwarded call connects (or fails) so he can
// track lead-flow to the rented contractor.
//
// Telnyx posts form-encoded fields:
//   CallSid, From, To, DialCallStatus, DialCallDuration, DialCallSid

const TO_EMAIL = "peter@yesai.au";
const FROM_EMAIL = "voicemail@yesai.au";
const FROM_NAME = "Darwin Termite Barriers";

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") return { statusCode: 405, body: "Method not allowed" };

  const params = new URLSearchParams(event.body || "");
  const data = {
    callSid: params.get("CallSid") || "",
    from: params.get("From") || "(unknown)",
    to: params.get("To") || "",
    dialStatus: params.get("DialCallStatus") || "",
    dialDuration: params.get("DialCallDuration") || "0",
  };

  // Only email when the call CONNECTED to the contractor.
  // For no-answer/busy/failed, the caller falls through to voicemail and the
  // voicemail handler will fire its own email — don't double up here.
  if (data.dialStatus !== "completed") {
    // Tell Telnyx to continue executing the next verb in the parent XML
    // (which is the voicemail fallback). Returning empty XML signals "done".
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/xml; charset=utf-8" },
      body: '<?xml version="1.0" encoding="UTF-8"?>\n<Response/>',
    };
  }

  const apiKey = process.env.BREVO_API_KEY;
  if (!apiKey) {
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/xml; charset=utf-8" },
      body: '<?xml version="1.0" encoding="UTF-8"?>\n<Response/>',
    };
  }

  const callerDisplay = data.from.replace("+61", "0").replace(/(\d{2})(\d{4})(\d{4})/, "$1 $2 $3");
  const minutes = Math.floor(parseInt(data.dialDuration || "0", 10) / 60);
  const seconds = parseInt(data.dialDuration || "0", 10) % 60;
  const duration = `${minutes}m ${seconds}s`;

  const html = `
<!DOCTYPE html>
<html><body style="font-family:-apple-system,sans-serif;color:#1f2937;background:#faf7f2;padding:24px;margin:0;">
  <table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto;background:#fff;border-radius:8px;border:1px solid #e5dfd1;">
    <tr><td style="background:linear-gradient(135deg,#047857,#065f46);padding:20px 24px;color:#fff;">
      <p style="margin:0 0 4px;font-size:11px;letter-spacing:0.1em;color:#a7f3d0;text-transform:uppercase;font-weight:700;">Lead Forwarded</p>
      <h1 style="margin:0;font-family:Georgia,serif;font-size:22px;color:#fff;">Caller patched through &mdash; ${duration}</h1>
    </td></tr>
    <tr><td style="padding:24px;">
      <p style="margin:0 0 16px;">A lead from <strong>Darwin Termite Barriers</strong> was answered by the rented contractor and stayed on for <strong>${duration}</strong>.</p>
      <table width="100%" cellpadding="0" cellspacing="0" style="font-size:15px;">
        <tr><td style="padding:8px 0;color:#6b7280;width:120px;">Caller</td><td style="padding:8px 0;font-weight:700;color:#14304a;"><a href="tel:${data.from}" style="color:#14304a;text-decoration:none;">${callerDisplay}</a></td></tr>
        <tr><td style="padding:8px 0;color:#6b7280;">Talk time</td><td style="padding:8px 0;">${duration}</td></tr>
        <tr><td style="padding:8px 0;color:#6b7280;">Call SID</td><td style="padding:8px 0;font-family:monospace;font-size:12px;color:#6b7280;">${data.callSid}</td></tr>
      </table>
    </td></tr>
  </table>
</body></html>
`;

  try {
    await fetch("https://api.brevo.com/v3/smtp/email", {
      method: "POST",
      headers: { "api-key": apiKey, "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify({
        sender: { name: FROM_NAME, email: FROM_EMAIL },
        to: [{ email: TO_EMAIL, name: "Peter" }],
        subject: `Lead forwarded — ${callerDisplay} talked for ${duration}`,
        htmlContent: html,
        tags: ["lead-forwarded", "darwintermitebarriers"],
      }),
    });
  } catch (err) {
    console.error("Email error:", err);
  }

  // Return empty <Response> — Telnyx will hang up since the dial completed.
  return {
    statusCode: 200,
    headers: { "Content-Type": "application/xml; charset=utf-8" },
    body: '<?xml version="1.0" encoding="UTF-8"?>\n<Response><Hangup/></Response>',
  };
};
