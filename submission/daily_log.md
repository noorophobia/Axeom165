# Daily Work Log — Axeom Challenge Pack 165

## Day 1 — November 4, 2026

**Time:** Exact working hours not recorded.

**What I did:**
- Reviewed the challenge requirements and supplied datasets.
- Started cleaning and exploring the business records.
- Built the initial Streamlit dashboard structure.
- Started connecting client, booking, invoice, payment, and production data.

**What I changed my mind about, and why:**
- Focused on building a practical dashboard instead of trying to build every possible feature.
- Prioritised reliable data relationships over automatically merging records that only shared contact details.

**What went wrong, and how I fixed it:**
- Some records had inconsistent names and missing references.
- Used additional data checks and manual review rather than assuming every match was correct.

**Where AI was wrong, and how I caught it:**
- AI-assisted analysis needed verification against the original CSV files. I checked important figures against the underlying records before using them in the final answers.

## Day 2 — November 5, 2026

**Time:** Exact working hours not recorded.

**What I did:**
- Continued developing the Streamlit dashboard.
- Added and improved the Clients, Money, Production, and Leads sections.
- Worked on financial reconciliation and potential billing gaps.
- Added CSV/TXT upload functionality and conflict handling.
- Reviewed client identity and payment relationships.

**What I changed my mind about, and why:**
- Decided not to add every suggested feature. Prioritised functionality that directly supported the challenge.
- Skipped additional client approval/rejection controls to keep the scope manageable.

**What went wrong, and how I fixed it:**
- Repeated booking uploads introduced duplicate records and inflated some dashboard totals.
- Compared the affected figures against the original cleaned dataset and decided not to treat duplicate rows as additional real bookings.
- Continued with the original cleaned data as the baseline for relevant analysis.

**Where AI was wrong, and how I caught it:**
- An initial dashboard interpretation overstated potentially unbilled bookings. I checked the original booking records and identified the duplicate-upload issue rather than accepting the inflated figure.

## Day 3 — November 6, 2026

**Time:** Exact working hours not recorded.

**What I did:**
- Completed further checks on the client mapping and financial figures.
- Populated the overdue invoice section with 16 invoices totalling $15,500.
- Populated 95 potentially never-billed booking entries totalling $77,100.
- Identified two invoices incorrectly marked unpaid despite matching payments.
- Investigated potential lost requests and client retention concerns.
- Validated `answers.json` successfully: 127 client groups, 16 overdue invoices, and 95 potentially never-billed entries.
- Prepared the writeup and updated assumptions.

**What I changed my mind about, and why:**
- Decided not to label inquiries as lost requests without sufficient evidence.
- Decided not to claim a Jev result because the available access required paid credits/API access.

**What went wrong, and how I fixed it:**
- Some answer fields were initially incomplete.
- Revisited the underlying message and lead records and documented uncertainty instead of inventing findings.
- Confirmed that `answers.json` was valid JSON using Python.

**Where AI was wrong, and how I caught it:**
- AI-generated conclusions and dashboard figures were not always reliable without checking the source records. I verified important claims using Python and the original CSV data.
- I did not treat missing response timestamps as proof that a lead was ignored or lost.

## Remaining work

- Save and finalise all documentation.
- Deploy the dashboard publicly and test it without login.
- Test the application on a phone and with new uploads.
- Record the video and obtain its transcript.
- Add the live and video links to `answers.json`.
- Package the final submission.

