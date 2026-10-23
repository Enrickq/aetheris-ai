# Aetheris AI · English demo script

The completed local video is [Aetheris-AI-demo-en.mp4](demo/Aetheris-AI-demo-en.mp4): **2 min 18 s**, 1920×1080, with synthetic English narration. It is an edited walkthrough of captures from the working local simulator; it has not been published to YouTube or Vimeo. The table below remains a guide for a live presentation or a new recording. The actual video narration is in [NARRATION_EN.txt](demo/NARRATION_EN.txt).

## Prepare the screen

Run the app, choose **Workspace → Alexa+ simulation**, and set the analysis mode to **Ensayo local (sin AWS)**. Keep the simulation disclaimer visible. Use the local path for the script below; do not describe it as a live AWS or Alexa demonstration. Clear or restart the session before recording if it contains older results.

## Narration and actions

| Time | Screen action | English narration |
| --- | --- | --- |
| 0–15 s | Show the Alexa+ simulation workspace and disclaimer | “This is Aetheris AI, a browser simulation of an Alexa+ observatory assistant. It uses synthetic telescope data. This recording uses local rehearsal: there is no live Alexa connection and no AWS call.” |
| 15–32 s | Click **Scan the observatory**; show its response and tool trace | “An observer starts with a simple request: scan the observatory. The local tool inspects twenty measurements. The trace shows the operation behind the response, so the user can inspect the evidence.” |
| 32–47 s | Switch briefly to **Observatory**, showing row seven and the peak; return to the simulation | “The seventh observation, GTC-007, contains our deliberately injected event. Its luminosity and thermal variation are far above the surrounding values. This is a reproducible test case, not a discovery.” |
| 47–67 s | Click **Explain the anomaly**; show the explanation and trace | “Explain the anomaly turns the measurements into a concise account. Here, a labeled local rule supplies the rehearsal explanation. The possible-supernova label is a demonstration hypothesis and still needs scientific follow-up.” |
| 67–88 s | Click **Prepare follow-up**; show the draft and `pending_human_review` status | “Prepare follow-up creates a reviewable JSON draft. Its state is pending human review. Nothing is sent and no telescope time is scheduled. The operator can inspect the proposed next step before a future action.” |
| 88–104 s | Show available JSON/evidence downloads and the visible analysis-mode control | “The same prototype also implements a real Amazon Bedrock invocation path using Claude's Messages format. That path needs an authenticated account and model access; it has not been live validated in this delivery.” |
| 104–115 s | End on the conversation and tool trace | “Aetheris connects a signal, an explanation, and a reviewable next step. Our next milestone is an authorized cloud test, followed by evaluation with astronomers and representative observations.” |

Keep the actions visible rather than showing only slides. If a control or download label differs slightly in the final source, follow the actual app and keep the statements about simulation and human review unchanged.

## If recording a later real Bedrock run

Only say a call is real after it succeeds with an authorized account. Keep the **Alexa+ simulation** disclaimer: a real Bedrock analysis does not turn the web simulation into a real Alexa integration. Show the selected mode and preserve the returned report. Do not claim a particular latency, cost, or scientific accuracy without evidence.

## Before adding a video link to Devpost

Watch the recording from start to finish. Confirm the narration is in English, the functioning simulation is visible, and the video is publicly accessible on YouTube or Vimeo with a duration under three minutes. Use your own screen capture and narration; add only media you are authorized to use. The [event rules](https://amazonappdev2026.devpost.com/rules) remain the authority for submission requirements.

**Pending external fields:** public video URL, team/author credits, repository URL, and final account submission. The local video already exists. Do not replace missing external fields with placeholder links.
