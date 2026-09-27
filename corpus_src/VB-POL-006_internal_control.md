# Internal Control Policy

| Field | Value |
|---|---|
| Document ID | VB-POL-006 |
| Version | 3.0 |
| Effective date | 2026-02-01 |
| Owner | Chief Risk Officer (CRO) |
| Approved by | Board Audit Committee |
| Review cycle | Annual |
| Classification | Internal |

## 1. Purpose

Internal controls are the checks that keep the bank's operations safe, its records accurate, and its activities within the law. This policy sets the framework for designing, operating, testing, and reporting on internal controls across Veridane Bank.

## 2. Scope

This policy applies to all business segments, branches, DFS channels, the Technology Division, and head office functions. It applies to all staff members and to third parties performing activities on the bank's behalf.

## 3. Control Objectives

The bank's internal control system is designed to give reasonable assurance that:

- operations are effective and efficient, and assets are protected against loss, theft, and fraud;
- financial and regulatory reports are complete, accurate, and on time;
- the bank complies with laws, regulations, and its own policies.

The framework has five components: the control environment (the tone from the top, values, and accountability set out in VB-POL-004), risk assessment, control activities, information and communication, and monitoring.

## 4. Three Lines of Defense

| Line | Who | Role in internal control |
|---|---|---|
| First | Business units, branches, DFS, Technology, and support functions | Own their risks, design and operate day-to-day controls, and complete self-assessments |
| Second | Risk Management (including the Internal Control Unit and Fraud Risk Management) and Compliance | Set control standards, maintain the segregation of duties matrix, test key controls, and challenge the first line |
| Third | Internal Audit, led by the Chief Audit Executive | Gives the Board Audit Committee independent assurance that controls are well designed and working |

## 5. Roles and Responsibilities

- **Board Audit Committee:** approves this policy, receives the CRO's quarterly internal control report and all Internal Audit reports, and tracks overdue high-rated issues.
- **CRO:** owns this policy and the internal control framework, and approves compensating controls for segregation of duties conflicts.
- **Internal Control Unit (ICU):** part of Risk Management, reporting to the CRO. The ICU maintains the segregation of duties matrix, tests key controls, and employs Regional Internal Control Officers who carry out unannounced branch checks.
- **Heads of Department, Regional Managers, and Branch Managers:** are accountable for the controls in their areas, including fixing weaknesses on time.
- **Head of Fraud Risk Management:** leads fraud prevention, detection, and investigation, working with Internal Audit on suspected internal fraud.
- **All staff:** follow controls, never bypass them, and report control failures.

## 6. Key Control Requirements

### 6.1 Segregation of duties

No single person may control every stage of a transaction. The ICU maintains the segregation of duties (SoD) conflict matrix, reviews it every year, and has it applied automatically when access is granted (VB-POL-002, section 7.5). Conflicting duties include:

- initiating and authorizing the same payment or transfer;
- creating a customer record and approving that customer's account opening;
- holding cash and recording cash transactions in the general ledger;
- maintaining vendor master data and approving payments to vendors;
- writing software code and deploying it to production.

Where a small team makes full segregation impossible, the CRO may approve the conflict only with a documented compensating control, such as a daily independent review of the person's transactions. These approvals last no longer than 6 months, in line with the exception process in VB-ORG-001.

### 6.2 Dual control

These activities always need two authorized people acting together: opening and closing the branch vault, replenishing ATMs and cash deposit machines, handling captured cards, changing vault combinations, and destroying cards or PIN mailers. Branch procedures for dual control are in VB-POL-008.

### 6.3 Authorization limits

No one may authorize a transaction they initiated.

| Transaction | Authorization limits |
|---|---|
| Cash withdrawal at a branch counter | Teller up to USD 5,000; BOM from USD 5,001 to USD 50,000; BM above USD 50,000 |
| Staff-initiated transfer or payment in CoreLink | Team Manager or BOM up to USD 100,000; BM or Head of Department from USD 100,001 to USD 1,000,000; two Band B authorizers above USD 1,000,000 |
| Reversal or correction of a posted transaction | BOM up to USD 5,000; BM above USD 5,000 |
| Fee or charge waiver | BM up to USD 100 per customer per month; Regional Manager above that |
| Vendor invoice payment | Head of Finance up to USD 50,000; CFO above USD 50,000 |

### 6.4 Callback verification

The following must be verified by calling the requester on a phone number already held on file:

- any request to change payment instructions, beneficiary accounts, or supplier bank details;
- any customer instruction received by email for a transfer above USD 5,000.

A phone number given in the request itself must never be used. The callback must be made by someone other than the person who received the request. The result must be recorded in CoreLink or the vendor file before the change is made or the payment is processed.

### 6.5 Mandatory block leave

Staff in sensitive roles must take at least 10 consecutive business days of leave once in each calendar year. While they are away, a colleague performs their duties, which helps expose irregularities that might otherwise stay hidden.

- **Sensitive roles:** tellers, BOMs, vault custodians, Treasury dealers, Treasury Operations staff, payment operations staff, DFS card operations staff, loan disbursement officers, and staff with privileged IT access.
- The leave must be scheduled by 31 January and taken by 30 November. HR places anyone who has not taken it by 30 November on leave in December.
- During the leave, the staff member's CoreLink and payment system access is suspended (VB-POL-002, section 11).
- Staff on mandatory block leave must not be contacted about work or recalled, except with the CRO's approval.
- The leave counts toward the annual leave entitlement in VB-POL-009.

### 6.6 Job rotation

BOMs and vault custodians rotate to another branch or role at least every 3 years. Tellers rotate between counter duties at least every 12 months.

### 6.7 Reconciliations

| Account or process | Frequency | Responsible |
|---|---|---|
| Branch cash and vault | Daily | BOM |
| ATM and cash deposit machine cash | Daily | Branch or Cash Center, with DFS Self-Service Channels |
| Card and POS settlement accounts | Daily | DFS Cards, and Merchant Acquiring and Payments |
| Nostro accounts | Daily | Treasury Operations |
| Suspense and sundry accounts | Daily | Department that owns the account |
| All other general ledger accounts | Monthly | Department that owns the account |

Each reconciliation is prepared by one person and reviewed by another. Unreconciled items open for more than 30 days are reported to the CFO every month. Items open for more than 90 days are reported to the Board Audit Committee every quarter.

### 6.8 Surprise cash counts and branch checks

The BM performs a surprise cash count of each teller at least once a month and of the vault at least once a quarter. Regional Internal Control Officers carry out an unannounced check of every branch at least once a quarter.

### 6.9 Technology change control

Changes to production systems, including CoreLink and DFS apps and APIs, must be approved by the Change Advisory Board (CAB), which meets every Thursday. Developers do not have access to production systems. Every release of Veridane Mobile, Veridane Online, or Veridane Wallet must pass security testing before it goes live. Emergency changes may be made with the CIO/CTO's approval and must be reviewed by the CAB within 2 business days.

## 7. Risk and Control Self-Assessment

Every department, branch, and DFS unit completes a Risk and Control Self-Assessment (RCSA) in the Veridane GRC system each quarter. The RCSA is due within 15 business days after the end of the quarter. It records the unit's key risks, how well its controls worked, and any control failures during the quarter. The ICU reviews and challenges the results.

## 8. Control Issues and Remediation

Control weaknesses found by the ICU, Internal Audit, regulators, or self-assessment are rated and must be fixed within these deadlines:

| Rating | Remediation deadline |
|---|---|
| High | 30 days |
| Medium | 90 days |
| Low | 180 days |

The CRO may approve one extension per issue. Overdue high-rated issues are reported to the Board Audit Committee at its next meeting.

## 9. Fraud and Operational Loss Events

- Suspected fraud must be reported to the Fraud Desk (staff ext. 4777) immediately, and no later than one hour after it is discovered. Concerns about fraud by staff may also be raised through the Speak Up Line (VB-POL-005).
- The Head of Fraud Risk Management investigates suspected internal fraud together with Internal Audit.
- Every operational loss of USD 1,000 or more is recorded in the operational loss database within 5 business days of discovery. Near misses are recorded too.
- Losses above USD 50,000 are reported to the CRO within 24 hours and to the Board Risk Committee at its next meeting.
- The Head of Fraud Risk Management submits the monthly frauds and forgeries return to the CMA by the 10th day of the following month.

## 10. Monitoring and Assurance

- The ICU tests key controls every quarter against a plan approved by the CRO.
- Internal Audit follows a risk-based audit plan approved each year by the Board Audit Committee. High-risk branches are audited every year, and all other branches at least every 24 months.
- The CRO presents a quarterly internal control report to the Board Audit Committee and the Board Risk Committee.

## 11. Compliance and Enforcement

Bypassing a control, falsifying a reconciliation, or authorizing one's own transaction is handled under the disciplinary procedure in VB-POL-004 and may be treated as gross misconduct.

## 12. Related Documents

- VB-ORG-001 Company Profile and Policy Framework
- VB-POL-002 Password and Access Control Policy
- VB-POL-004 Ethics and Code of Conduct Policy
- VB-POL-005 Whistleblowing Policy
- VB-POL-008 Branch Operations Policy
- VB-POL-009 Leave and Public Holidays Policy

## Revision History

| Version | Date | Summary of changes |
|---|---|---|
| 3.0 | 2026-02-01 | Added daily reconciliation of card and POS settlement accounts. Change control extended to DFS apps and APIs. Mandatory block leave extended to DFS card operations staff. |
| 2.2 | 2025-01-15 | Callback threshold for customer email instructions lowered from USD 10,000 to USD 5,000. |
