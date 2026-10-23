# Aetheris AI · Local development friction log

**Observation date:** October 23, 2026  
**Runtime:** Streamlit 1.66.1  
**Scope:** Local implementation observations from the prototype. These entries do not describe a failure of Alexa+, Amazon Bedrock, or any live AWS service. They are consistent with `FEEDBACK_EN.md` and `entrega/DEVPOST-COPY.txt`.

## Case 1 · Container-width API migration

- **Task:** Make the application controls and chart fill their available container width.
- **Steps:** Run the original application with `use_container_width=True` calls in the installed Streamlit 1.66.1 runtime and inspect the runtime output.
- **Expected:** A responsive layout without deprecation warnings.
- **Actual:** Streamlit emitted deprecation warnings requesting replacement of `use_container_width` with the `width` parameter. The layout could render, but the existing calls needed migration.
- **Severity:** Low. This was a compatibility warning, not a blocked application or service outage.
- **Workaround:** Replace the affected calls with `width="stretch"` and rerun the local checks.
- **Actionable suggestion:** Keep the migration mapping prominent in the relevant chart and button API examples so developers can update an existing app without searching across references.

## Case 2 · Dark theme within a single Python file

- **Task:** Apply a dark appearance while keeping the application implementation in one Python file.
- **Steps:** Check the public `st.set_option` interface and its supported options for changing `theme.base` from inside the application script.
- **Expected:** A supported in-script theme setting that satisfies the single-file constraint.
- **Actual:** The public API does not permit changing `theme.base` inside the script. This is an API constraint identified during implementation, not a claim of a live runtime crash.
- **Severity:** Important for this prototype's single-file and dark-interface requirements; not a cloud service failure.
- **Workaround:** Use CSS in `app.py`, together with explicit dark colors for the table and Vega-Lite chart.
- **Actionable suggestion:** Provide a supported per-app theme mechanism or a documented single-file recipe that avoids dependence on frontend CSS selectors, which may require maintenance as the UI changes.

The second entry's API restriction is documented in the [official Streamlit `st.set_option` reference](https://docs.streamlit.io/develop/api-reference/configuration/st.set_option). Neither entry establishes Alexa or AWS onboarding, performance, reliability, or live integration results.
