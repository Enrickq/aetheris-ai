# Product feedback · Aetheris AI v1.1.0

This feedback describes the implementation and local verification actually available in the delivery. It does not report an AWS onboarding session or a live Alexa/Bedrock execution that did not occur.

## Streamlit

**Used for:** the observatory dashboard, sidebar workspaces and analysis modes, conversational web simulation, tool trace, session state, and CSV/JSON downloads.

**What worked:** a single Python application can combine tabular telemetry, a line chart, and a reviewable interaction flow. AppTest provides a practical way to exercise reruns and error states locally without cloud credentials.

**Friction observed:** the original `use_container_width` calls emitted deprecation warnings in the installed runtime. Switching to `width="stretch"` removed that use. The public `st.set_option` interface does not allow changing `theme.base` inside the script, so the single-file requirement led to CSS and explicit chart styling. CSS selectors used for controls can require maintenance when Streamlit's frontend changes.

**Onboarding:** package installation and local rendering were exercised in the preparation environment. This is local web development experience, not a device-platform onboarding claim.

**Would we use it again?** Yes, for a small, inspectable Python prototype. We would reassess the styling approach and deployment controls before a public production service.

## Pandas and Vega-Lite rendering

**Used for:** reproducible telemetry generation, shared records for table/chart/payload, and exports. The Streamlit chart API renders a Vega-Lite line specification.

**What worked:** a single DataFrame avoids discrepancies between the observations the user sees and the data prepared for analysis. Row numbering and an explicitly injected event make the rehearsal easy to reproduce.

**What needs work in our prototype:** the current batch is deterministic and deliberately simple. It is not evidence of scientific detection quality or of handling an observatory's real acquisition format. We did not independently onboard to a Vega-Lite service or SDK; the chart is rendered through Streamlit.

**Would we use them again?** Yes, for this scale of tabular prototype, with validation of real data formats before extending it.

## boto3 and Amazon Bedrock API implementation

**Used for:** constructing a `bedrock-runtime` client, preparing an `invoke_model` request, and parsing response text. The source includes the exact Claude 3 Sonnet model ID, JSON headers, `anthropic_version`, `max_tokens`, and `messages`.

**What worked locally:** mocked client responses let us check the request payload, text-block parsing, resource cleanup, and visible failure handling without invoking AWS. This is evidence about application behavior under supplied responses, not evidence about the service's performance or reliability.

**Friction and next step:** the prepared `aetheris-demo` profile has region/output metadata but no credentials. We therefore cannot report first-call latency, real model access, account onboarding success, quota behavior, or actual cost. The requested older model also requires a current account/region lifecycle check. A successful authorized invocation is still required before calling this path live validated.

**Would we use it again?** We would continue with boto3 for the Python integration and evaluate Bedrock after a real account test. We do not yet have evidence to rate the live service experience.

## Alexa+ simulated experience

**Used for:** a local browser simulation of scan → explain → prepare follow-up, with visible tool traces and a human-review draft. The experience runs as application code, without an Alexa SDK, Agent Skill, MCP server, Echo device, speech recognition, or live Alexa connection.

**What worked locally:** the interaction makes the relationship between a request, an operation, and its evidence visible. A follow-up draft can be inspected before any future external action is considered.

**Feedback boundary:** we cannot give first-hand feedback on Alexa+ developer onboarding, API behavior, device reliability, or MCP hosting because those paths were not exercised. A future integration should make tool status, permissions, and draft-versus-executed actions equally clear.

## Provenance and reproducibility

| Item | Source or status |
| --- | --- |
| Application | `app.py`, project version `1.1.0`; inspect the current source for exact behavior |
| Dependency versions | `requirements.txt`: Streamlit `1.66.1`, Pandas `3.1.0`, boto3 `1.43.118` |
| Preparation Python | `3.12.14`, inspected locally on October 23, 2026 |
| Local test command | `python -m unittest discover -s tests -v`; AWS clients are mocked |
| Evidence | Current logs/reports in the delivery; rehearsal output remains labeled simulated |
| Live AWS and Alexa evidence | Not available in this delivery |
| Published repository | https://github.com/Enrickq/aetheris-ai; source, tests and assets verified |
| Final video | https://youtu.be/-5itenMafn0 — 1:46, author-supplied English recording, burned-in English subtitles; final local MP4 in `entrega/` |
| Backup video | Earlier 138-second synthetic-narration MP4 and separate captions remain in `demo/` |
| Devpost | https://devpost.com/software/aetheris-ai — submission confirmed by the platform on October 23, 2026, at approximately 18:28 UTC; this is not an eligibility or judging decision |

## Final video preparation

FFmpeg edited and normalized the author-supplied recording and synchronized it with captures of the functioning local app. Local Faster-Whisper (`small.en`, CPU) supplied word timings; caption wording was reviewed against the recording script before burning English subtitles into the final video. No voice was generated for this final edit.

**Local tooling friction:** Faster-Whisper 1.2.1 with PyAV 19 rejected a decoder `metadata_errors` argument. Decoding with FFmpeg to a 16 kHz float32 waveform and passing the NumPy array to the local transcriber resolved that incompatibility. Automatic recognition also needed script review for proper names and technical terms. This was a local media-tool compatibility issue, not an AWS or Alexa failure.

Relevant primary references: [Streamlit configuration restrictions](https://docs.streamlit.io/develop/api-reference/configuration/st.set_option), [AWS Claude Messages schema](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html), [boto3 credentials](https://docs.aws.amazon.com/boto3/latest/guide/credentials.html), and [AWS model lifecycle](https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle-legacy.html). These explain implementation choices; they do not substitute for runtime evidence.
