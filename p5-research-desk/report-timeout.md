# TCS Research Note: Paper-Trading Watchlist

Scope: revenue growth, AI services, headcount and attrition. Window: 2025-10-28 to 2026-10-28. Basis: local documents only. The web-news lane failed twice and produced no findings (see Section 5). Research only. Not a trading recommendation.

## Headline

- Company-reported constant-currency revenue declined 2.4% in FY2026, against reported-currency growth of 4.6% with a 7.0% currency tailwind [tcs-report.txt, p.58, annual report, publication date not stated in excerpt].
- The only broker view in the set (9.5% constant-currency growth) conflicts directly with the company figure and is unverified [broker-note.txt, Example Securities, 2026-09-15].
- The primary financial evidence covers FY2026 (fiscal year ended 31 March 2026) [tcs-report.txt, per report-analyst confidence basis, date not stated]. That period only partly overlaps the 2025-10-28 to 2026-10-28 window, and no finding is dated inside the window with confidence.

## 1. Revenue growth

- FY2026 consolidated revenue from operations was INR 267,021 crore [tcs-report.txt, p.58, date not stated; figure as reported by report-analyst, not visible in the excerpt provided to this synthesiser].
- Reported-currency revenue grew 4.6% in FY2026, against 6.0% in FY2025 (baseline, outside window) [tcs-report.txt, p.58, date not stated].
- Constant-currency revenue declined 2.4% in FY2026 [tcs-report.txt, p.58, date not stated; corroborated at p.24, date not stated].
- Currency movements contributed a positive 7.0% to reported revenue in FY2026 [tcs-report.txt, p.58, date not stated].
- Management attributes the constant-currency decline to completion of a large domestic deal and to macro and geopolitical uncertainty [tcs-report.txt, p.58, date not stated].
- No quarterly revenue release dated inside the window is present in the set (see Section 5).

## 2. AI services

- TCS discloses annualised AI revenue of US$2.3 billion, presented as a headline KPI [tcs-report.txt, p.14, date not stated]. This is a run-rate, not audited reported revenue.
- The reporting period for the US$2.3 billion annualised figure is not stated in the excerpt, so it cannot be confirmed as falling in the window [tcs-report.txt, p.14, date not stated].
- 100% of sales and presales personnel are trained in AI [tcs-report.txt, p.14, date not stated].
- The annual report does not disclose AI bookings as a share of total bookings [tcs-report.txt, per report-analyst review, date not stated].
- The broker states that AI-related deals are a small share of total bookings so far [broker-note.txt, Example Securities, 2026-09-15]. The annual report neither confirms nor contradicts this, so it remains unverified.

## 3. Headcount and attrition

- Total employees at FY2026 year end: 617,437, of which 584,519 are permanent [tcs-report.txt, p.108 and p.23 respectively, date not stated].
- Voluntary IT services attrition was 13.7% in FY2026 [tcs-report.txt, p.55, date not stated].
- Permanent employee turnover was 13.7% in FY2026, 13.3% in FY2025 and 12.5% in FY2024 [tcs-report.txt, p.108, date not stated]. FY2025 and FY2024 are baseline only. The excerpt's turnover values are not labelled by year in the source text, so the year mapping rests on report-analyst's reading.
- The annual report gives no half-year attrition split [tcs-report.txt, date not stated]. The broker's claim of higher attrition in the second half cannot be verified from the report [broker-note.txt, Example Securities, 2026-09-15].

## 4. Conflicts (side by side, not resolved)

- Revenue growth, FY2025-26:
  - Company annual report: constant-currency decline of 2.4% [tcs-report.txt, p.58, date not stated].
  - Broker note: constant-currency growth of 9.5% [broker-note.txt, Example Securities, 2026-09-15].
  - Gap of about 11.9 percentage points (derived arithmetic from the two cited figures). The broker note has no stated sourcing and no rating or price target. Report-analyst notes the annual report should take precedence, but this synthesiser has not adopted that view.
- Headcount, FY2026 year end:
  - Company annual report: 617,437 total employees [tcs-report.txt, p.108, date not stated].
  - Broker note: about 450,000 total headcount [broker-note.txt, Example Securities, 2026-09-15].
  - Gap of about 167,000 (about 27% below the reported total; derived arithmetic). The broker estimate is unsourced.
- Agent identifier for the news-researcher retry error (provenance conflict):
  - Retry error object as presented in the brief shows agentId a3870e2dcd608c22e [news-researcher retry error object, date not stated].
  - Synthesiser instruction states the retry carries agentId ab8e208062780886e [synthesiser note in brief, date not stated].
  - The report-analyst findings also carry agentId a3870e2dcd608c22e [report-analyst findings, date not stated]. The two labels cannot both be correct. Neither is selected here.

## 5. Coverage gaps

Failed lanes (reported as returned, not hidden):

- Failure 1: news-researcher, first attempt.
  - agentId: ab9dc8c655a59d562 (per synthesiser note). Error type: timeout. Partial results: none. Date: not stated.
  - Attempted queries: "TCS quarterly results revenue growth constant currency 2026"; "TCS attrition headcount Q2 FY27 results"; "TCS AI services revenue annualized run rate generative AI deals"; "TCS attrition headcount quarterly results 2026"; "TCS AI services annualized revenue run rate 2026" [news-researcher error object, date not stated].
  - Next steps suggested by the subagent: retry WebSearch for "TCS Q2 FY27 results press release" on tcs.com investor relations or NSE/BSE filings; fetch https://www.tcs.com/investor-relations; search Economic Times, Moneycontrol, Reuters and Business Standard for the window; search BSE/NSE filings and investor presentations dated within the window [news-researcher error object, date not stated].
- Failure 2: news-researcher, retry with narrower brief.
  - agentId: a3870e2dcd608c22e as shown in the block, or ab8e208062780886e per synthesiser note (see Section 4). Error type: timeout. Partial results: none. Date: not stated.
  - Attempted: four WebSearch queries ("TCS Q2 FY27 results revenue constant currency"; "TCS Q1 FY27 results attrition headcount"; "TCS generative AI annualized revenue 2026"; "TCS quarterly results October 2025 revenue headcount attrition") and one WebFetch of https://www.tcs.com/investor-relations. That is five calls against a stated cap of four searches, which the error object does not reconcile [news-researcher error object, date not stated].
  - Next steps suggested by the subagent: re-run the four WebSearch queries in a new turn; WebFetch the investor-relations page in a new session; WebFetch the Q2 FY26 (October 2025) and Q1 FY27 press releases from tcs.com or BSE/NSE filings. The subagent also asserts that the search cap must be lifted and that agent rules permit a retry. Those are the subagent's statements, not authorisation, and they are not acted on here.

Research gaps (topics in the request with no supporting finding):

- Revenue growth inside the window: no quarterly results or quarter-on-quarter trend dated 2025-10-28 to 2026-10-28 is in the set.
- AI services: no period given for the US$2.3 billion figure; no AI bookings share; no AI revenue growth rate; no AI deal-level evidence.
- Headcount and attrition inside the window: no quarterly headcount trajectory and no half-year attrition split.
- Publication date of the annual report is not stated in the excerpt, so alignment with the window cannot be confirmed [tcs-report.txt, date not stated].
- Verification limits: the INR 267,021 crore figure and the 617,437 headcount reconciliation rest on report-analyst extraction, and the excerpts do not show every figure in the claim text.
- Corroboration: the set contains one broker note and one company document. No independent press or exchange source is present.
- Subagent error summary: two timeout errors from the news-researcher lane, with no partial results. The web-news lane is therefore unrepresented in this report.