# Daily Work Log — Axeom Challenge Pack 165

## Day 1 — November 6, 2026

**Time:** Exact working hours not recorded.

**What I did:**
- Reviewed the challenge requirements and supplied datasets.
- Cleaned and explored the business records using Python and pandas.
- Built and improved the Streamlit dashboard, including the Clients, Money, Production, and Leads sections.
- Connected client, booking, invoice, payment, lead, and production data.
- Added CSV/TXT upload functionality and handling for repeated uploads.
- Investigated client identities, financial reconciliation, overdue invoices, and potential billing gaps.
- Identified 16 overdue invoices totalling $15,500.
- Identified 95 potentially never-billed booking entries totalling $77,100.
- Identified two invoices marked unpaid despite matching payments.
- Investigated potential lost requests and client retention concerns.
- Validated `answers.json` using Python: 127 client groups, 16 overdue invoices, and 95 potentially never-billed entries.
- Prepared the writeup and assumptions documentation.

**What I changed my mind about, and why:**
- Focused on building a practical dashboard rather than adding every possible feature.
- Prioritised reliable data relationships over automatically merging records based only on shared contact details.
- Decided not to label inquiries as lost requests without sufficient evidence.
- Decided not to claim a Jev result because completing a job required additional paid credits/API access.

**What went wrong, and how I fixed it:**
- Repeated booking uploads introduced duplicate records and inflated some dashboard totals.
- Compared affected figures against the original cleaned dataset and identified the repeated records.
- Used the original cleaned data as the baseline for the relevant analysis.
- Some answer fields were initially incomplete, so I revisited the underlying records and documented uncertainty rather than inventing findings.

**Where AI was wrong, and how I caught it:**
- AI-assisted analysis and dashboard figures required verification against the original CSV files.
- An initial interpretation overstated potentially unbilled bookings because of duplicate uploads. I checked the booking records and corrected the analysis.
- I did not treat missing lead response timestamps as proof that a lead had been ignored or lost.
- Verified important figures with Python instead of relying solely on AI-generated conclusions.

## Day 2 — November 7, 2026

**Time:** Exact working hours not recorded.

**What I did:**
- Reviewed the dashboard's usability, particularly on mobile screens.
- Identified that the file-upload control in the sidebar could be difficult for mobile users to notice.
- Moved the upload interface from the sidebar to the main page so users can find the data-update functionality more easily.
- Retained the existing upload-processing logic and duplicate-upload feedback.
- Ran the application locally to check the updated interface.
- Updated the AI usage log and reviewed the remaining submission tasks.

**What I changed my mind about, and why:**
- Decided that upload functionality should be visible on the main page rather than hidden in the sidebar.
- Prioritised discoverability and ease of use, especially for mobile users, to better support the requirement that users should understand the dashboard quickly.

**What went wrong, and how I fixed it:**
- The original sidebar upload control was not prominent enough for mobile use.
- Moved the upload section to the main page and checked that the relevant upload code and feedback messages remained in place.

**Where AI was wrong, and how I caught it:**
- Treated AI suggestions as implementation guidance rather than proof that the interface worked.
- Checked the updated source code for the upload control and success/duplicate feedback.
- Further live deployment and mobile-device testing are still required before considering the usability change fully verified.

## Remaining work

- Commit and push the latest dashboard and documentation changes.
- Verify the deployed dashboard works without login.
- Test the updated interface on an actual mobile device.
- Test new uploads and confirm the displayed data updates correctly.
- Record the required video and prepare its transcript.
- Add the live and video links to `answers.json`.
- Package and review the final submission.