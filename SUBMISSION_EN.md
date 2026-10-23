# Aetheris AI · Devpost copy

Use the blocks below as project text. Replace the external fields at the end with real URLs and team information before submission.

## Project title

Aetheris AI

## Tagline

An Alexa+ web simulation for explainable observatory anomaly alerts.

## Inspiration

An unusual signal matters only if someone can understand it and decide what to do next. Inspired by the Roque de los Muchachos observatory in the Canary Islands, we explored a conversational interface that connects an observation, an explanation, and a reviewable next step. Aetheris AI makes that workflow visible using synthetic telescope data and an explicitly simulated Alexa+ experience.

## What it does

The web app provides two connected workspaces. Observatory shows a batch of 20 synthetic measurements, including an intentionally extreme event in row seven, sector GTC-007. Alexa+ simulation turns that batch into a three-step conversation: scan the observatory, explain the anomaly, and prepare follow-up.

Each action exposes a tool trace so the user can see the operation behind the response. Follow-up is a local JSON draft marked `pending_human_review`; it does not send a message or schedule telescope time. Users can inspect and export the evidence instead of receiving an unexplained alert.

The analysis mode is explicit. Local rehearsal runs a deterministic, clearly labeled rule without AWS. The real Amazon Bedrock path is implemented for Claude 3 Sonnet, but a successful live invocation has not been verified in this delivery. The Alexa+ experience itself is a browser simulation, not a connection to Alexa or an Echo device.

## How we built it

The entire application is implemented in one Python file using Streamlit and Pandas. A shared DataFrame supplies the table, chart, conversation tools, and analysis payload, keeping the observations consistent across the workflow.

The AWS integration creates a boto3 `bedrock-runtime` client and calls `invoke_model` with the exact model ID `anthropic.claude-3-sonnet-20240229-v1:0`. The payload uses Claude's Messages format, and the parser extracts text blocks from the returned content. Credentials stay outside the application through the standard AWS credential chain. A scoped IAM policy and setup instructions document the integration.

Local orchestration drives the simulated conversation and tool trace. The source includes dependency pins, a Windows launcher, cross-platform run instructions, automated tests with mocked AWS responses, and separate provenance for local versus AWS analysis.

## Challenges we ran into

The hardest boundary was making a compelling demonstration without implying evidence we did not have. We separated synthetic observations, deterministic rehearsal output, a simulated assistant, and the implemented AWS invocation path. Authentication or model-access errors remain visible errors rather than triggering an unlabeled fallback.

We also had to preserve the original single-file application constraint while adding a reviewable conversational workflow. Session state keeps results consistent, while changes to the analysis context invalidate stale output. The requested older Claude model introduces account, region, and lifecycle constraints that still require a real AWS validation step.

## Accomplishments that we're proud of

We built a runnable workflow from a visible signal to an explanation and a human-reviewed draft, while exposing the intermediate tool operations. The demo works locally without credentials and makes its simulation boundaries explicit. The Bedrock request and response handling are implemented and can be exercised with reproducible mocked tests, rather than being described only in a slide.

## What we learned

A conversational interface is easier to assess when users can inspect the data, tool calls, and output provenance. We learned to treat a prepared follow-up as a draft with an explicit review state, and to distinguish a working integration implementation from a successful live service call. We also learned that model lifecycle and regional access must be part of a demo's preparation, not an assumption hidden in the UI.

## What's next

Complete an authorized live Bedrock run and retain its evidence. Evaluate a supported model migration before the requested model retires in the selected region. Then test with astronomers and representative observations, add richer time-series and uncertainty handling, and measure classification quality and latency. A future Alexa integration would need its own real device or supported integration testing; the current deliverable remains the web simulation.

## Built with

Python, Streamlit, Pandas, boto3, Amazon Bedrock invocation API, Anthropic Claude 3 Sonnet request format, Vega-Lite, unittest, Streamlit AppTest.

## Primary track

**Alexa+ — simulated web experience path.** The runnable simulation source is in `app.py`, under the Alexa+ simulation workspace. It demonstrates local conversational orchestration and tool traces. It does not claim to be an Alexa Skill, an MCP server, or a live Alexa integration. The [official rules](https://amazonappdev2026.devpost.com/rules) describe this alternative path; organizer eligibility decisions remain separate from this project description.

## Additional mini challenge disclosure: AWS Builder

**Documented integration: Amazon Bedrock.** The code serializes the synthetic batch and prompt, invokes `bedrock-runtime.invoke_model`, and parses Claude text. The repository includes credential setup, a scoped `bedrock:InvokeModel` policy, and mocked integration tests. **Live AWS validation is pending** because this delivery does not have authenticated access to the requested model. The local rehearsal is not evidence of Bedrock execution. This disclosure should accompany any AWS Builder selection; it is not a claim that runtime use or eligibility has been verified.

## Product feedback

Paste the observed feedback from [FEEDBACK_EN.md](FEEDBACK_EN.md). It identifies implementation experience and local checks separately from services we have not used live.

## Remaining external fields

| Field | Status |
| --- | --- |
| GitHub repository URL | https://github.com/Enrickq/aetheris-ai — public, source and assets verified |
| Repository license or reviewer access | MIT license included; public repository |
| Public English demo video URL | No URL yet. Current MP4 is 138 seconds with synthetic narration. The author plans to record their own voice; no new audio has been received or edited. Author will publish on YouTube/Vimeo |
| Devpost account and event registration | Authenticated and registered |
| Devpost draft | https://devpost.com/software/aetheris-ai; management ID 1257991-aetheris-ai; 3/5 steps complete |
| Saved project details | English description, repository, four technology tags and three inline screenshots saved |
| Saved additional information | Tool feedback, testing instructions and friction log saved |
| Selected track and mini challenges | Alexa+ simulated web experience; AWS Builder and Open Source not selected in the draft |
| Public friction log | https://github.com/Enrickq/aetheris-ai/blob/main/evidencias/FRICTION_LOG_EN.md |
| Team names, author credits, project dates | Owner must confirm during final review |
| Final terms and submission | Final terms not accepted; final submission not sent; no submission confirmation |

The source package and English video are complete and available in the public GitHub repository. No YouTube/Vimeo URL, Alexa connection, live AWS call, or submitted entry is asserted by this text.
