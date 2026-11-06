# Assumptions and Open Questions

**Pack:** 165  
**Reporting date:** October 6, 2026

This document records the assumptions used while analysing the supplied data. Where the records do not provide enough evidence, findings are treated as provisional rather than confirmed facts.

## 1. Client identity and duplicate records

**Questions to confirm:**
- Do people or businesses sharing an email address or phone number represent the same client, related businesses, or separate clients?
- Should provisional client matches be counted as confirmed clients?

**Assumptions used:**
- Client records were grouped using available names, email addresses, phone numbers, and related records.
- Records were not automatically merged based only on a shared contact detail.
- The resulting 127 groups represent mapped client identities, not 127 independently verified legal clients.
- Ambiguous matches remain subject to owner review.

## 2. Payers who are not clients

**Questions to confirm:**
- Are individual payment senders owners, employees, representatives, or third parties paying on behalf of a business?
- Can the associated business relationships be confirmed?

**Assumptions used:**
- Where an individual appears as the payer and a separate business is associated with the payment, the individual is listed separately as a potential non-client payer.
- The payer-to-business relationship is an inference from the available records, not a confirmed legal or contractual relationship.
- The individual is not automatically merged with the associated business.

## 3. Payments and invoice reconciliation

**Questions to confirm:**
- Which invoices are covered by payments that do not contain an invoice reference?
- Are any payments bulk payments, deposits, credits, or payments covering multiple invoices?
- Are there disputes, refunds, or adjustments not represented in the supplied data?

**Assumptions used:**
- Payments were matched to invoices when the available references provided sufficient evidence.
- Payments without clear invoice references were not arbitrarily allocated based only on similar amounts, names, or dates.
- Two invoices, INV-1090 and INV-1092, were identified as incorrectly marked unpaid because matching payments fully covered their balances.
- No confirmed amount owed by the studio was identified in the supplied payment records. This does not establish that no external obligations exist.

## 4. Overdue invoices

**Questions to confirm:**
- Do invoice statuses reflect the latest payment, credit, or dispute information?
- Are there unrecorded payments or arrangements with clients?

**Assumptions used:**
- October 6, 2026 is the reporting date.
- An invoice is considered overdue when its due date has passed and it has a positive remaining balance after confidently matched payments.
- The resulting overdue figure is 16 invoices totalling $15,500.
- Unmatched payments may affect some balances and should be reviewed before collection action.

## 5. Potentially never-billed bookings

**Questions to confirm:**
- Are completed bookings without an explicit invoice reference genuinely unbilled?
- Are some services covered by retainers, bundles, deposits, or recurring agreements?
- Are invoice references missing from the available records?

**Assumptions used:**
- A completed, positive-price booking without an explicit invoice match is classified as potentially never billed.
- This identifies 95 bookings with a combined listed value of $77,100.
- These amounts are not treated as confirmed unpaid debt.
- Zero-price completed retainer bookings are excluded from this total because their recorded price is zero; this does not establish that the work had no commercial value.

## 6. Lost requests and unconverted leads

**Questions to confirm:**
- Did an inquiry that has no associated booking actually result in a lost sale?
- Was the request declined, postponed, handled outside the recorded system, or simply not converted?
- Are missing first-response timestamps evidence of no response, or only incomplete recordkeeping?

**Assumptions and findings used:**
- A lead without a booking is not automatically classified as a lost request.
- A missing first-response timestamp does not prove that the lead was never contacted.
- No confirmed lost requests could be established from the available records.

**Examples reviewed:**

- **Leah Moore (L088), September 4:** Asked about a package for short clips from podcast episodes. The lead is marked New and has no recorded first-response timestamp. The contact details also match an existing Faith & Fire contact. The records do not establish whether this inquiry was answered or lost.
- **Parks Auto Spa (L085):** Asked about pricing for a reels package. The lead is marked Won and has associated bookings, so it is not classified as a lost request.
- **Brightwater (L061):** Asked about recurring monthly videos. The lead is marked Won and has associated bookings, so it is not classified as a lost request.

**Conclusion:**
- `lost_requests` is empty because no lost request was verified.
- `lost_requests_root_causes` is empty because there is no confirmed lost-request event from which to establish causes.
- `lost_requests_started_getting_worse_in` is recorded as not determinable because the available evidence does not establish a trend in lost requests.
- The unresolved L088 inquiry should be checked with the owner before drawing a conclusion.

## 7. Leads with no recorded first response

**Questions to confirm:**
- Were leads without a first-response timestamp contacted through phone, personal email, or another channel?
- Are the lead records complete?

**Assumptions used:**
- Eleven genuine leads were flagged because they have no recorded first-response timestamp.
- These are follow-up priorities, not confirmed ignored leads or lost sales.
- Spam, invalid leads, and records outside the reporting period were excluded.

## 8. Client retention and complaints

**Questions to confirm:**
- Were complaints resolved after the recorded messages?
- Did the client agree to continue after discussing the contract?
- Are there further conversations outside the supplied records?

**Assumptions used:**
- Romero Law Firm is treated as the strongest current retention risk because of repeated naming instructions, a subsequent complaint, and contract-related follow-ups.
- This is a risk assessment, not confirmation that the client has left.
- The recommended action is for the owner to contact Alana Romero personally and address the repeated naming issue.
- Complaint trends are not automatically treated as lost-sales trends.

## 9. Production status and delivery

**Questions to confirm:**
- What are the expected delivery deadlines for each video?
- Are the recorded production statuses up to date?
- Are unmatched production records connected to bookings that are missing references?

**Assumptions used:**
- Production status is based on the supplied records.
- Work without a recorded deadline is not classified as overdue.
- Editor-level revision and delivery statistics describe recorded workload and outcomes; they do not independently prove individual performance or fault.
- Unmatched production records require further reference reconciliation.

## 10. Costs and profitability

**Questions to confirm:**
- Are all editor hours, studio costs, and other operating expenses recorded?
- Are retainers and zero-price bookings covered by separate agreements?
- Are there additional overheads not included in the supplied cost data?

**Assumptions used:**
- Profitability calculations use the available service prices, editor rates, studio rates, and recorded hours.
- The resulting figures are estimates, not audited profit or complete business profitability.
- Missing prices, incomplete hours, and unmatched production records may affect the estimates.

## 11. Duplicate uploads and data quality

**Questions to confirm:**
- Were uploaded files intended to replace existing records or append new records?
- Are duplicate booking IDs caused by repeated uploads or source-system duplication?

**Assumptions used:**
- Duplicate booking records were observed after repeated uploads.
- The original cleaned dataset is used as the baseline for the relevant booking analysis rather than treating repeated uploaded rows as additional real bookings.
- Conflicting IDs and incomplete references should be reviewed before relying on upload-derived totals.

## 12. General limitations

- Analysis is limited to the files supplied for this challenge.
- Missing information is treated as missing evidence, not proof that an event did not happen.
- Shared contact details, similar names, and matching payment amounts are not sufficient by themselves to prove identity or payment allocation.
- Findings marked as potential, inferred, or provisional require owner confirmation before financial or client-facing action.
- The dashboard is intended to support owner review and decision-making, not automatically send messages, collect payments, or make irreversible business decisions.
