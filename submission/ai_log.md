# AI Usage Log — Axeom Challenge Pack 165

## 1. AI tools used

**ChatGPT**
- Used to understand the challenge requirements and break the work into manageable steps.
- Used for Python and pandas analysis guidance.
- Used for Streamlit dashboard development, debugging, and user-interface improvements.
- Used to investigate client relationships, invoice reconciliation, lead records, production data, and operational risks.
- Used for drafting and reviewing `answers.json`, `writeup.md`, `assumptions.md`, and this log.
- Used to review the dashboard's usability and improve the upload experience.

**Python and pandas**
- Used to inspect, clean, filter, compare, and validate the supplied datasets.
- Used to independently check important figures before including them in `answers.json`.

## 2. How I checked AI-generated work

I did not treat AI-generated conclusions as automatically correct.

I checked important findings against the source CSV files using Python, including:
- Client counts and identity mappings.
- Invoice balances and matched payments.
- Completed bookings without explicit invoice references.
- Lead statuses and message history.
- Production records and duplicate identifiers.

I also validated `answers.json` using Python's JSON library and checked important totals against the underlying data.

## 3. Example of an AI mistake I caught

**Issue: Duplicate booking uploads**

During dashboard development, repeated booking uploads caused duplicate records to appear. This inflated some dashboard totals, including the number of potentially unbilled bookings.

An initial interpretation of the dashboard figures was therefore unreliable.

**How I caught it:**
- Compared dashboard output with the original cleaned booking dataset.
- Checked booking IDs and identified duplicate records introduced by repeated uploads.
- Used the original cleaned dataset as the baseline for the relevant analysis.
- Avoided presenting the inflated dashboard count as the real business figure.

This reinforced the importance of checking AI-assisted analysis against the original data.

## 4. Other decisions where I avoided unsupported AI conclusions

- Did not automatically merge clients just because they shared contact details.
- Did not classify missing lead-response timestamps as proof that no response was sent.
- Did not label inquiries as lost requests without evidence of a lost sale.
- Did not classify potentially never-billed bookings as confirmed unpaid debt.
- Did not invent a Jev job or accuracy score when I could not complete a job with the available access.

## 5. Work completed on November 6, 2026

ChatGPT was used as a development and analysis assistant while completing the Pack 165 dashboard and submission materials.

Work included:
- Continued investigation of client, payment, booking, lead, and message records.
- Reviewed unresolved findings and avoided repeating investigations that had already been completed.
- Worked on completing the remaining sections of `answers.json`.
- Reviewed the dashboard's business findings and operational priorities.
- Checked the consistency of the analysis with the supplied source data.
- Continued preparing the project for its live demonstration and submission.

## 6. Work completed on November 7, 2026

ChatGPT was used to review and improve the dashboard's usability, particularly on mobile devices.

**Mobile upload-interface improvement:**
- Identified that the file-upload control was located in the sidebar, where it could be difficult to notice on a mobile screen.
- Moved the upload interface from the sidebar to the main page.
- Kept the existing file-upload processing logic, including duplicate detection and upload feedback, rather than rewriting the data-handling workflow.
- Checked the code to confirm that the uploader and success messages now use the main page.

The purpose of this change was to make the dashboard easier to understand and use without requiring users to discover a small sidebar control.

Further live deployment and mobile testing are part of the final verification process.

## 7. Main prompts and conversation references

The main ChatGPT conversations covered:
- Explaining the Axeom challenge deliverables.
- Cleaning and investigating Pack 165 datasets.
- Building and debugging the Streamlit dashboard.
- Reconciling invoices and payments.
- Mapping clients and investigating leads.
- Preparing `answers.json` and submission documentation.
- Improving dashboard usability and mobile upload access.

Conversation links were not separately recorded. The relevant conversation history is available in the ChatGPT account used during the project.

## 8. Limitations

AI assistance helped accelerate development and investigation, but final conclusions still required source-data checks and human judgement.

Jev was not completed because the available access required additional paid credits/API access. No Jev accuracy measurement is claimed.

The dashboard and its findings are based on the supplied challenge data. Ambiguous client identities, unmatched payments, missing timestamps, and potentially unbilled bookings require confirmation before operational or financial action.