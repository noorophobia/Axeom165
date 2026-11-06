# AI Usage Log — Axeom Challenge Pack 165

## 1. AI tools used

**ChatGPT**
- Used for understanding the challenge requirements and breaking the work into manageable steps.
- Used for Python and pandas analysis guidance.
- Used for Streamlit dashboard development and debugging.
- Used to investigate client relationships, invoice reconciliation, lead records, and production data.
- Used for drafting documentation and structuring findings.

**Python and pandas**
- Used to inspect, clean, filter, compare, and validate the supplied datasets.
- Used to independently check important figures before adding them to `answers.json`.

## 2. How I checked AI-generated work

I did not treat AI-generated conclusions as automatically correct.

I checked important findings against the source CSV files using Python, including:
- Client counts and identity mappings.
- Invoice balances and matched payments.
- Completed bookings without explicit invoice references.
- Lead statuses and message history.
- Production records and duplicate identifiers.

I also validated `answers.json` by loading it with Python's JSON library and checking the key totals.

## 3. Example of an AI mistake I caught

**Issue: Duplicate booking uploads**

During dashboard development, repeated booking uploads caused duplicate records to appear. This inflated some dashboard totals, including the number of potentially unbilled bookings.

An initial interpretation of the dashboard figures was therefore unreliable.

**How I caught it:**
- Compared the dashboard output with the original cleaned booking dataset.
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

## 5. Main prompts and conversation references

The main ChatGPT conversations covered:
- Explaining the Axeom challenge deliverables.
- Cleaning and investigating Pack 165 datasets.
- Building and debugging the Streamlit dashboard.
- Reconciling invoices and payments.
- Mapping clients and investigating leads.
- Preparing `answers.json` and submission documentation.

Conversation links were not separately recorded. The relevant conversation history is available in the ChatGPT account used during the project.

## 6. Limitations

AI assistance helped accelerate development and investigation, but final conclusions still required source-data checks and human judgement.

Jev was not completed because the available access required additional paid credits/API access. No Jev accuracy measurement is claimed.