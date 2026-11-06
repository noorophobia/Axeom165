# Axeom Challenge — Pack 165
**Prepared by:** Noor Fatima  
**Reporting date:** October 6, 2026

## 1. How I found the answers

I started by inspecting the supplied datasets, cleaning and standardising records, and connecting related clients, bookings, invoices, payments, leads, messages, and production records.

I used Python and pandas to explore the data, identify inconsistencies, and calculate the figures used in `answers.json`.

Key findings:

- **Clients:** Mapped 127 canonical client groups using names, emails, phone numbers, and related records. Ambiguous matches were not automatically treated as confirmed identities.
- **Overdue invoices:** Identified 16 invoices with positive remaining balances, totalling **$15,500**, as of October 6, 2026. Matched payments were deducted before identifying overdue balances.
- **Potentially never-billed bookings:** Identified 95 completed, positive-price bookings without an explicit invoice match, with a listed value of **$77,100**. These are potential billing gaps, not confirmed unpaid debt.
- **Billing errors:** Found two invoices marked unpaid despite matching payments fully covering their balances: INV-1090 and INV-1092.
- **Lost requests:** No lost requests could be confirmed from the available evidence. An inquiry without a recorded response or booking was not automatically classified as lost.
- **Retention risk:** Romero Law Firm was identified as the strongest current retention concern based on repeated naming instructions, a complaint, and subsequent contract-related messages.
- **Marketing:** Referrals had the highest observed conversion rate in the supplied lead data, at 8 out of 10. The sample is small, so this should not be treated as a guaranteed future result.

I cross-checked important findings against the underlying CSV records instead of relying only on dashboard summaries.

## 2. How the system works

I built a Python and Streamlit dashboard to make the supplied business data easier to explore.

The dashboard includes:

- **Clients:** A mapped client directory and related records.
- **Money:** Invoice, payment, overdue, and reconciliation information.
- **Production:** Booking and video-production status information.
- **Leads:** Lead information and follow-up priorities.
- **File uploads:** CSV and TXT uploads to bring additional records into the dashboard, with safeguards for conflicting identifiers and upload conflicts.

The goal was to turn disconnected spreadsheets into a practical owner-facing review tool. It supports investigation and decision-making rather than automatically contacting clients or taking financial actions.

## 3. What does not work yet

The results depend on the completeness and accuracy of the supplied records.

- Some client identities and payer-to-business relationships remain provisional.
- Payments without invoice references cannot always be allocated confidently.
- Bookings without explicit invoice matches may be covered by retainers, bundles, or missing references.
- Missing lead-response timestamps do not prove that no response was sent.
- No confirmed lost-request trend could be established.
- Cost and profitability figures are estimates, not audited financial results.
- Repeated uploads can introduce duplicate records, so upload-derived totals require validation.
- The system has not been tested against every possible new-file format or data-quality issue.

**Jev:** I did not complete a Jev job. The available access required additional paid credits/API access, which I could not use for this challenge. Therefore, I have no Jev accuracy measurement to report. I have not fabricated a result.

## 4. What I would do in the next two weeks

1. Validate the client mapping and unresolved payer relationships with the owner.
2. Reconcile unreferenced payments and potentially unbilled bookings against the accounting system.
3. Review the 11 leads with no recorded first-response timestamp and establish whether they were contacted.
4. Contact Romero Law Firm to address the repeated naming issue and contract concern.
5. Test the dashboard with fresh uploads, duplicate records, missing columns, and conflicting identifiers.
6. Improve data validation, upload feedback, and dashboard usability based on owner feedback.

The most important next step is to verify uncertain records with the owner before using the dashboard's findings for collections, client communication, or business decisions.