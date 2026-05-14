// Shared rank-and-rent voicemail webhook — Telnyx TeXML
//
// (03) 9003 0108 is shared across multiple VIC rank-and-rent sites. This
// function is brand-neutral — the email subject / body don't claim a specific
// brand because we can't tell from the call alone which site the caller saw.
// The caller's voicemail content (suburb + what they're calling about) is what
// identifies the source brand.
//
// Telnyx sends form-encoded POST with fields:
//   AccountSid, CallSid, From, To, Direction, CallStatus,
//   RecordingSid, RecordingUrl, RecordingStatus, RecordingDuration,
//   RecordingChannels, RecordingSource, RecordingTrack

const TO_EMAIL = "peter@yesai.au";
const FROM_EMAIL = "voicemail@yesai.au";
const FROM_NAME = "Lead Line";
const SHARED_PHONE_DISPLAY = "(03) 9003 0108";

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }

  const params = new URLSearchParams(event.body || "");
  const data = {
    callSid: params.get("CallSid") || "",
    from: params.get("From") || "(unknown)",
    to: params.get("To") || "",
    direction: params.get("Direction") || "",
    callStatus: params.get("CallStatus") || "",
    recordingSid: params.get("RecordingSid") || "",
    recordingUrl: params.get("RecordingUrl") || "",
    recordingStatus: params.get("RecordingStatus") || "",
    recordingDuration: params.get("RecordingDuration") || "0",
  };

  console.log("Voicemail callback:", JSON.stringify(data));

  // Skip if no recording (e.g. failed status, empty hangup)
  if (!data.recordingUrl || data.recordingStatus !== "completed") {
    console.log("Skipping email — no completed recording");
    return { statusCode: 200, body: "OK (no recording)" };
  }

  const apiKey = process.env.BREVO_API_KEY;
  if (!apiKey) {
    console.error("BREVO_API_KEY not set");
    return { statusCode: 200, body: "OK (no email key)" };
  }

  const recordingMp3 = data.recordingUrl.endsWith(".mp3")
    ? data.recordingUrl
    : `${data.recordingUrl}.mp3`;

  const callerDisplay = data.from
    .replace("+61", "0")
    .replace(/(\d{2})(\d{4})(\d{4})/, "$1 $2 $3");

  const subject = `New voicemail on ${SHARED_PHONE_DISPLAY} — from ${callerDisplay} (${data.recordingDuration}s)`;

  const html = `
<!DOCTYPE html>
<html><body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6;color:#1f2937;background:#faf7f2;padding:24px;margin:0;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;border:1px solid #e5dfd1;">
    <tr><td style="background:linear-gradient(135deg,#14304a,#0d2237);padding:20px 24px;color:#fff;">
      <p style="margin:0 0 4px;font-size:11px;letter-spacing:0.1em;color:#fdba74;text-transform:uppercase;font-weight:700;">New Voicemail</p>
      <h1 style="margin:0;font-family:Georgia,serif;font-size:22px;color:#fff;">Shared Lead Line ${SHARED_PHONE_DISPLAY}</h1>
      <p style="margin:6px 0 0;font-size:12px;color:rgba(255,255,255,0.7);">Caller will mention their suburb + what they need — listen to the recording to identify which site.</p>
    </td></tr>
    <tr><td style="padding:24px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="font-size:15px;">
        <tr><td style="padding:8px 0;color:#6b7280;width:120px;">From</td><td style="padding:8px 0;font-weight:700;color:#14304a;font-size:18px;"><a href="tel:${data.from}" style="color:#14304a;text-decoration:none;">${callerDisplay}</a></td></tr>
        <tr><td style="padding:8px 0;color:#6b7280;">Called</td><td style="padding:8px 0;">${data.to.replace("+61", "0").replace(/(\d{2})(\d{4})(\d{4})/, "$1 $2 $3")}</td></tr>
        <tr><td style="padding:8px 0;color:#6b7280;">Duration</td><td style="padding:8px 0;">${data.recordingDuration} seconds</td></tr>
        <tr><td style="padding:8px 0;color:#6b7280;">Received</td><td style="padding:8px 0;">${new Date().toLocaleString("en-AU", { timeZone: "Australia/Melbourne" })} AEDT</td></tr>
      </table>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:20px;">
        <tr><td align="center">
          <a href="${recordingMp3}" style="display:inline-block;background:#d97706;color:#fff;padding:12px 28px;border-radius:6px;font-weight:700;text-decoration:none;font-size:15px;">Listen to recording</a>
        </td></tr>
      </table>

      <p style="margin:24px 0 0;font-size:13px;color:#6b7280;text-align:center;">
        Call back: <a href="tel:${data.from}" style="color:#d97706;font-weight:600;">${callerDisplay}</a>
      </p>

      <p style="margin:16px 0 0;font-size:11px;color:#9ca3af;text-align:center;border-top:1px solid #e5dfd1;padding-top:12px;">
        Recording stays available for 7 days at the link above. Call SID: ${data.callSid}
      </p>
    </td></tr>
  </table>
</body></html>
`;

  try {
    const resp = await fetch("https://api.brevo.com/v3/smtp/email", {
      method: "POST",
      headers: {
        "api-key": apiKey,
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify({
        sender: { name: FROM_NAME, email: FROM_EMAIL },
        to: [{ email: TO_EMAIL, name: "Peter" }],
        subject,
        htmlContent: html,
        tags: ["voicemail", "rank-rent-shared"],
      }),
    });

    const result = await resp.text();
    console.log("Brevo response:", resp.status, result);

    if (!resp.ok) {
      return { statusCode: 200, body: `Email failed: ${resp.status}` };
    }

    return { statusCode: 200, body: "OK" };
  } catch (err) {
    console.error("Email error:", err);
    return { statusCode: 200, body: `Error: ${err.message}` };
  }
};
