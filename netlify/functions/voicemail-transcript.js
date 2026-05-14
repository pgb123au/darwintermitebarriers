// Shared rank-and-rent transcription callback — Telnyx TeXML
// Brand-neutral follow-up email with the AI transcription text.

const TO_EMAIL = "peter@yesai.au";
const FROM_EMAIL = "voicemail@yesai.au";
const FROM_NAME = "Lead Line";

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") return { statusCode: 405, body: "Method not allowed" };

  const params = new URLSearchParams(event.body || "");
  const data = {
    callSid: params.get("CallSid") || "",
    from: params.get("From") || "(unknown)",
    transcriptionSid: params.get("TranscriptionSid") || "",
    transcriptionText: params.get("TranscriptionText") || "",
    transcriptionStatus: params.get("TranscriptionStatus") || "",
  };

  console.log("Transcript callback:", JSON.stringify(data));

  if (data.transcriptionStatus !== "completed" || !data.transcriptionText) {
    return { statusCode: 200, body: "OK (no transcript)" };
  }

  const apiKey = process.env.BREVO_API_KEY;
  if (!apiKey) return { statusCode: 200, body: "OK (no email key)" };

  const callerDisplay = data.from.replace("+61", "0").replace(/(\d{2})(\d{4})(\d{4})/, "$1 $2 $3");

  const html = `
<!DOCTYPE html>
<html><body style="font-family:-apple-system,sans-serif;line-height:1.6;color:#1f2937;background:#faf7f2;padding:24px;margin:0;">
  <table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto;background:#fff;border-radius:8px;border:1px solid #e5dfd1;">
    <tr><td style="background:#14304a;padding:20px 24px;color:#fff;">
      <p style="margin:0;font-size:11px;letter-spacing:0.1em;color:#fdba74;text-transform:uppercase;font-weight:700;">Voicemail Transcript</p>
      <h1 style="margin:4px 0 0;font-family:Georgia,serif;font-size:20px;color:#fff;">From ${callerDisplay}</h1>
    </td></tr>
    <tr><td style="padding:24px;">
      <p style="margin:0 0 6px;font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">What they said</p>
      <blockquote style="margin:0 0 20px;padding:14px 18px;border-left:3px solid #d97706;background:#faf7f2;font-size:16px;line-height:1.65;color:#1f2937;border-radius:0 6px 6px 0;">
        ${data.transcriptionText.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}
      </blockquote>
      <p style="margin:0;font-size:13px;color:#6b7280;text-align:center;">
        <a href="tel:${data.from}" style="color:#d97706;font-weight:600;text-decoration:none;">Call back: ${callerDisplay}</a>
      </p>
      <p style="margin:14px 0 0;font-size:11px;color:#9ca3af;text-align:center;">Call SID: ${data.callSid}</p>
    </td></tr>
  </table>
</body></html>
`;

  try {
    const resp = await fetch("https://api.brevo.com/v3/smtp/email", {
      method: "POST",
      headers: { "api-key": apiKey, "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify({
        sender: { name: FROM_NAME, email: FROM_EMAIL },
        to: [{ email: TO_EMAIL, name: "Peter" }],
        subject: `Voicemail transcript — from ${callerDisplay}`,
        htmlContent: html,
        tags: ["voicemail-transcript", "rank-rent-shared"],
      }),
    });
    console.log("Brevo response:", resp.status, await resp.text());
    return { statusCode: 200, body: "OK" };
  } catch (err) {
    console.error("Email error:", err);
    return { statusCode: 200, body: `Error: ${err.message}` };
  }
};
