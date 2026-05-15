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
//
// IMPORTANT (PFRCPR 2026-05-15): Telnyx's RecordingUrl is an AWS S3 *presigned*
// URL that expires 600 seconds (10 minutes) after the call. The old version of
// this handler emailed that link with the claim "available for 7 days" — by the
// time the email was opened the link returned S3 "Request has expired".
// Fix: download the audio here (the presigned URL is still valid because this
// webhook fires within seconds of the recording completing) and attach the MP3
// to the email so it never expires. The link is intentionally NOT emailed.

const TO_EMAIL = "peter@yesai.au";
const FROM_EMAIL = "voicemail@yesai.au";
const FROM_NAME = "Lead Line";
const SHARED_PHONE_DISPLAY = "(03) 9003 0108";

// Build candidate download URLs without corrupting a presigned query string.
// Only append an audio extension to the URL *path*, never after `?X-Amz-...`.
function recordingCandidates(raw) {
  const list = [];
  try {
    const u = new URL(raw);
    if (/\.(mp3|wav)$/i.test(u.pathname)) {
      list.push(raw);
    } else {
      const mp3 = new URL(raw);
      mp3.pathname = `${mp3.pathname}.mp3`;
      const wav = new URL(raw);
      wav.pathname = `${wav.pathname}.wav`;
      list.push(mp3.toString(), wav.toString(), raw);
    }
  } catch {
    list.push(raw.endsWith(".mp3") ? raw : `${raw}.mp3`, raw);
  }
  return [...new Set(list)];
}

async function fetchRecording(raw) {
  for (const url of recordingCandidates(raw)) {
    try {
      const resp = await fetch(url);
      if (!resp.ok) continue;
      const buf = Buffer.from(await resp.arrayBuffer());
      if (buf.length === 0) continue;
      const ct = (resp.headers.get("content-type") || "").toLowerCase();
      const ext = ct.includes("wav") ? "wav" : "mp3";
      return { buf, ext };
    } catch {
      /* try next candidate */
    }
  }
  return null;
}

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

  const callerDisplay = data.from
    .replace("+61", "0")
    .replace(/(\d{2})(\d{4})(\d{4})/, "$1 $2 $3");

  // Download the audio now, while the presigned URL is still valid.
  const rec = await fetchRecording(data.recordingUrl);

  let attachment;
  let recordingBlock;
  if (rec) {
    const stamp = new Date().toISOString().slice(0, 10).replace(/-/g, "");
    const digits = callerDisplay.replace(/\D/g, "") || "unknown";
    const fileName = `voicemail-${digits}-${stamp}.${rec.ext}`;
    attachment = [{ content: rec.buf.toString("base64"), name: fileName }];
    recordingBlock = `
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:20px;background:#faf7f2;border-radius:6px;">
        <tr><td style="padding:14px 18px;font-size:14px;color:#1f2937;">
          &#127911; <strong>Voicemail recording attached</strong> to this email as
          <code style="font-size:12px;">${fileName}</code> &mdash; play it any time, it never expires.
        </td></tr>
      </table>`;
  } else {
    // Couldn't retrieve the audio. Be HONEST about the link's short life rather
    // than repeat the old "available for 7 days" lie.
    console.error("Recording download failed for", data.recordingUrl);
    recordingBlock = `
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:20px;background:#fef2f2;border:1px solid #fecaca;border-radius:6px;">
        <tr><td style="padding:14px 18px;font-size:14px;color:#7f1d1d;">
          &#9888; The audio could not be attached. Telnyx's recording link below
          <strong>expires about 10 minutes after the call</strong> &mdash; open it immediately:<br>
          <a href="${data.recordingUrl}" style="color:#b91c1c;font-weight:600;word-break:break-all;">${data.recordingUrl}</a>
        </td></tr>
      </table>`;
  }

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

      ${recordingBlock}

      <p style="margin:24px 0 0;font-size:13px;color:#6b7280;text-align:center;">
        Call back: <a href="tel:${data.from}" style="color:#d97706;font-weight:600;">${callerDisplay}</a>
      </p>

      <p style="margin:16px 0 0;font-size:11px;color:#9ca3af;text-align:center;border-top:1px solid #e5dfd1;padding-top:12px;">
        Call SID: ${data.callSid}
      </p>
    </td></tr>
  </table>
</body></html>
`;

  const payload = {
    sender: { name: FROM_NAME, email: FROM_EMAIL },
    to: [{ email: TO_EMAIL, name: "Peter" }],
    subject,
    htmlContent: html,
    tags: ["voicemail", "rank-rent-shared"],
  };
  if (attachment) payload.attachment = attachment;

  try {
    const resp = await fetch("https://api.brevo.com/v3/smtp/email", {
      method: "POST",
      headers: {
        "api-key": apiKey,
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify(payload),
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
