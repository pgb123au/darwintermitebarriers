// Shared rank-and-rent voice handler — Telnyx TeXML
//
// (03) 9003 0108 is shared across all VIC rank-and-rent microsites. The greeting
// is brand-neutral and prompts the caller to mention their suburb and what they're
// calling about — that's how we identify which site sent the lead from the recording
// + transcript emails.
//
// Behaviour controlled by Netlify env vars:
//   - TENANT_FORWARD_NUMBER (E.164, e.g. "+61412345678") — if set, calls forward to the rented contractor with a "Pete's Lead" whisper
//   - TENANT_LABEL — what's whispered before connecting (default "Pete's Lead")
//
// When TENANT_FORWARD_NUMBER is unset, calls go straight to voicemail.
// When set, contractor hears the whisper, then the caller is patched through.
// If the contractor doesn't pick up within 22 seconds, the call falls through to voicemail.
//
// Telnyx TeXML app voice_url should point to this function:
//   https://darwintermitebarriers.netlify.app/.netlify/functions/voice

const SITE = "https://darwintermitebarriers.netlify.app";
const RECORD_CALLBACK = `${SITE}/.netlify/functions/voicemail`;
const TRANSCRIBE_CALLBACK = `${SITE}/.netlify/functions/voicemail-transcript`;
const WHISPER_URL = `${SITE}/.netlify/functions/whisper`;
const FORWARD_RESULT_CALLBACK = `${SITE}/.netlify/functions/forward-result`;

const VOICE = `voice="Polly.Nicole-Neural" language="en-AU"`;

function xml(body) {
  return {
    statusCode: 200,
    headers: { "Content-Type": "application/xml; charset=utf-8" },
    body: `<?xml version="1.0" encoding="UTF-8"?>\n${body}`,
  };
}

const VOICEMAIL_BLOCK = `<Pause length="1"/>
  <Say ${VOICE}>Thanks for calling. We're sorry we missed you. After the beep, please leave your name, your phone number, your suburb, and a quick description of what you need help with — and we'll call you back within one business day.</Say>
  <Record maxLength="120" playBeep="true" finishOnKey="#"
    recordingStatusCallback="${RECORD_CALLBACK}"
    recordingStatusCallbackMethod="POST"
    recordingStatusCallbackEvent="completed"
    transcribe="true"
    transcribeCallback="${TRANSCRIBE_CALLBACK}"/>
  <Say ${VOICE}>Thanks for that. We'll be in touch soon.</Say>
  <Hangup/>`;

const FORWARD_FALLBACK_VOICEMAIL = `<Say ${VOICE}>Sorry we missed you. After the beep, please leave your name, number, suburb, and what you're calling about — we'll call you back within one business day.</Say>
  <Record maxLength="120" playBeep="true" finishOnKey="#"
    recordingStatusCallback="${RECORD_CALLBACK}"
    recordingStatusCallbackMethod="POST"
    recordingStatusCallbackEvent="completed"
    transcribe="true"
    transcribeCallback="${TRANSCRIBE_CALLBACK}"/>
  <Hangup/>`;

exports.handler = async () => {
  const tenantNumber = (process.env.TENANT_FORWARD_NUMBER || "").trim();

  if (!tenantNumber) {
    // No tenant configured — voicemail only.
    return xml(`<Response>\n  ${VOICEMAIL_BLOCK}\n</Response>`);
  }

  // Tenant configured — forward with whisper, fall through to voicemail on no-answer.
  return xml(`<Response>
  <Dial timeout="22" answerOnBridge="true" action="${FORWARD_RESULT_CALLBACK}" method="POST">
    <Number url="${WHISPER_URL}">${tenantNumber}</Number>
  </Dial>
  ${FORWARD_FALLBACK_VOICEMAIL}
</Response>`);
};
