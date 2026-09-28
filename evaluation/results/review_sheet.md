# Judge validation sheet

For each question, read the excerpts, then record in `hand_labels.csv`:
- **grounded**: is every statement in the answer supported by the excerpts? (yes/no)
- **citations correct**: does each citation point to an excerpt that supports its statement? (yes/no)
- **correctness**: compared with the reference answer: full, partial, or incorrect

## q01: How many days of annual leave does a Band D officer get?

**Reference answer:** 22 business days a year (plus 3 more after 10 years of continuous service).

**System answer:** Band D officers receive 22 annual leave days per year. [1]

**Citations:**
```
[1] -> S1 (VB-POL-009, 4. Annual Leave > 4.1 Entitlement)
```

**Excerpts the system was given:**
```
[S1] Leave and Public Holidays Policy (VB-POL-009), 4. Annual Leave > 4.1 Entitlement
Band | Annual leave (business days)
A | 30
B | 28
C | 25
D | 22
E | 20
Staff who have completed 10 years of continuous service receive 3 additional days of annual leave each year.

[S2] Leave and Public Holidays Policy (VB-POL-009), 4. Annual Leave > 4.2 New joiners and leavers
Annual leave accrues monthly from the start date. Staff who join or leave during the year receive a pro rata entitlement. New staff may take annual leave once they have completed 3 months of service. The line manager may approve earlier leave in an emergency.

[S3] Staff Separation and Termination Policy (VB-POL-010), 4. Notice Periods
Situation | Notice required from either side
During probation (first 6 months) | 2 weeks
Band A | 3 months
Band B | 2 months
Bands C and D | 1 month
Band E | 2 weeks
- The bank may pay salary in lieu of all or part of the notice period.
- The bank may place a staff member on garden leave for all or part of the notice period. During garden leave the staff member remains employed and paid but does not come to work or access bank systems.
- Staff in the sensitive roles listed in VB-POL-006 are moved to non-sensitive duties, or placed on garden leave, from the day their resignation is accepted or notice is given. During the notice period they do not handle cash, hold vault combinations, or authorize payments.

[S4] Company Profile and Policy Framework (VB-ORG-001), 5. Staff Bands
Band | Level | Examples
A | Executive | CEO, Chief Officers (including the CDO and CIO/CTO), General Counsel
B | Senior Management | Heads of Department, DFS business heads, Regional Managers, MLRO, DPO, Head of Fraud Risk Management
C | Management | Branch Managers, Branch Operations Managers, Team Managers
D | Officers | Tellers, Customer Service Officers, Relationship Officers, Analysts
E | Support | Drivers, Facilities Assistants, Records Clerks
A staff member's band determines their leave entitlement, travel class, and expense limits, as set out in the relevant policies.

[S5] Leave and Public Holidays Policy (VB-POL-009), 4. Annual Leave > 4.4 Carry-over
Up to 5 unused days may be carried into the next leave year and must be used by 31 March. Days above that limit are forfeited unless the CHRO approves a larger carry-over because business needs prevented the staff member from taking leave. Unused leave cannot be exchanged for pay, except when a staff member leaves the bank (VB-POL-010).
```

## q04: What was the critical patch window before the latest change to the Information Security Policy?

**Reference answer:** 14 days; version 4.2 reduced it to 7 days.

**System answer:** The critical patch window was 14 days before the latest change to the Information Security Policy. [1]

**Citations:**
```
[1] -> S1 (VB-POL-001, Revision History)
```

**Excerpts the system was given:**
```
[S1] Information Security Policy (VB-POL-001), Revision History
Version | Date | Summary of changes
4.2 | 2026-02-01 | Added generative AI rules (section 5.2). Critical patch window reduced from 14 days to 7 days.
4.1 | 2025-03-01 | Added phishing simulation remediation steps.
4.0 | 2024-01-15 | Full rewrite. Introduced the four-level classification scheme.

[S2] Information Security Policy (VB-POL-001), 7. Endpoint and Device Security
- Only bank-issued devices, or personal devices enrolled under VB-POL-013, may access bank systems.
- All laptops, desktops, and mobile devices must use full-disk encryption.
- Screens lock automatically after 5 minutes of inactivity. Staff must lock their screen manually whenever they leave their device.
- USB storage devices are blocked by default. The CISO may approve an encrypted, bank-issued USB drive for up to 90 days at a time.
- Endpoint protection software must stay installed and running at all times.
- Security patches must be installed within these limits after release:
- Critical: 7 days
- High: 30 days
- Medium and low: the next monthly patch cycle
- A device more than 14 days out of patch compliance is quarantined from the network until it is updated.
- A lost or stolen device must be reported to the SOC immediately, and no later than one hour after the loss is discovered, so it can be wiped remotely.

[S3] Information Security Policy (VB-POL-001), Document information
Document ID: VB-POL-001
Title: Information Security Policy
Version: 4.2
Effective date: 2026-02-01
Owner: Chief Information Security Officer (CISO)
Approved by: Board Risk Committee
Review cycle: Annual
Classification: Internal

[S4] Information Security Policy (VB-POL-001), 15. Security Awareness Training
- New staff complete the Information Security Essentials course within 30 days of their start date.
- All staff complete the annual refresher by 30 June each year.
- Staff more than 14 days overdue are reported to their line manager and the CHRO. Staff more than 30 days overdue have their system access suspended until they complete the course.

[S5] Information Security Policy (VB-POL-001), 12. Security Incident Management > 12.3 Severity levels
Severity | Examples | Escalation
1, Critical | Ransomware, confirmed breach of Restricted data, attack causing a CoreLink outage | CISO informs the CEO within 1 hour. CMA notified within 24 hours.
2, High | Compromised staff account, malware on several devices | CISO informed within 4 hours.
3, Medium | Malware on a single device, loss of an encrypted laptop | Handled by the SOC and included in the monthly security report.
4, Low | Blocked phishing email, spam | Logged by the SOC.
```

## q05: What is the minimum password length for a privileged account?

**Reference answer:** 16 characters.

**System answer:** The minimum password length for a privileged account is 16 characters. [1]

**Citations:**
```
[1] -> S1 (VB-POL-002, 4. Password Requirements > 4.1 Minimum requirements by account type)
```

**Excerpts the system was given:**
```
[S1] Password and Access Control Policy (VB-POL-002), 4. Password Requirements > 4.1 Minimum requirements by account type
Standard accounts
- Minimum length: 14 characters
- Change: every 180 days, and immediately if compromise is suspected
- History: the last 12 passwords cannot be reused
Privileged accounts
- Minimum length: 16 characters
- Change: every 60 days, and automatically after each PAM vault checkout
- History: the last 24 passwords cannot be reused
Service accounts
- Minimum length: 25 characters, generated by the PAM vault
- Change: every 12 months, and within 5 business days after anyone who knew the password leaves the bank or changes role

[S2] Password and Access Control Policy (VB-POL-002), 15. Revision History
Version 3.1, 2026-02-01: Minimum length for standard accounts raised from 12 to 14 characters. SMS fallback for MFA limited to 7 days.
Version 3.0, 2025-01-10: Introduced PAM vault checkout rules. Dormant account limit reduced from 60 to 45 days.

[S3] Password and Access Control Policy (VB-POL-002), 3. Definitions
Standard account: an account used by one person for everyday work.
Privileged account: an account with administrative rights on a system, database, or network device, or the ability to change security settings or other users' access.
Service account: a non-human account used by an application or scheduled process.
Multi-factor authentication (MFA): sign-in that requires something you know (a password) plus something you have (an enrolled phone or a hardware token).
PAM vault: the bank's privileged access management system. It stores privileged credentials, issues them for limited periods, and records their use.

[S4] Password and Access Control Policy (VB-POL-002), 10. Privileged Access
10.1 Administrators use a separate privileged account for administrative work. Privileged accounts must never be used for email or web browsing.
10.2 Privileged credentials are checked out from the PAM vault for no more than 8 hours at a time. Sessions are recorded, and the password changes automatically when the credential is checked back in.
10.3 Emergency ("break-glass") accounts are sealed in the PAM vault. Using one requires approval from the CISO, or from the CRO if the CISO is unavailable. Each use is reviewed within 1 business day.

[S5] Password and Access Control Policy (VB-POL-002), 5. Multi-factor Authentication > 5.1 Where MFA is required
- VPN and all other remote access
- All privileged accounts
- Email and collaboration tools when used outside the bank network
- CoreLink supervisor overrides and payment authorizations
- Any cloud service that holds Confidential or Restricted information
```

## q08: Can tellers work from home?

**Reference answer:** No. All branch-based roles, including tellers, are not eligible for regular remote work.

**System answer:** No. Tellers are branch‑based roles that must be performed on bank premises and are not eligible for regular remote work. [1]

**Citations:**
```
[1] -> S3 (VB-POL-013, 4. Eligibility > 4.2 Roles that are not eligible)
```

**Excerpts the system was given:**
```
[S1] Remote and Flexible Work Policy (VB-POL-013), 9. Equipment, Allowance, and Health and Safety
- The bank provides a laptop and headset. Staff with an approved hybrid arrangement may also request a monitor and keyboard. Equipment staff buy themselves is not reimbursed unless the line manager approved it in advance.
- Staff with an approved hybrid arrangement receive a remote work allowance of USD 30 per month through payroll, to cover home internet and utility costs. These costs cannot be claimed as expenses (VB-POL-012).
- Work-related injuries at home must be reported to HR within 2 business days.
- Bank equipment is returned when the arrangement ends or the staff member leaves the bank.

[S2] Branch Operations Policy (VB-POL-008), 7. Counter Services > 7.4 Teller conduct
- Tellers must never work on another teller's CoreLink session. They lock or log out of their terminal and lock their cash drawer whenever they leave the counter, even briefly (VB-POL-002).
- Personal mobile phones are kept in staff lockers during counter duty.
- Tellers must not process transactions on their own accounts or those of relatives or close associates (VB-POL-004).
- Staff must never ask a customer for their card PIN, a one-time passcode, or an online banking password.

[S3] Remote and Flexible Work Policy (VB-POL-013), 4. Eligibility > 4.2 Roles that are not eligible
These roles must be performed on bank premises and are not eligible for regular remote work:
- all branch-based roles, including BMs, BOMs, tellers, and CSOs;
- vault custodians and Cash Center staff;
- Treasury dealers, who must trade from the dealing room on recorded lines;
- DFS Contact Center, Fraud Desk, and SOC staff, except under section 4.4.

[S4] Remote and Flexible Work Policy (VB-POL-013), 3. Definitions
- Remote work: work performed away from bank premises, usually at home.
- Hybrid arrangement: an approved pattern of regular remote days each week.
- Enrolled personal device: a staff member's own phone or tablet registered in the bank's mobile device management (MDM) system so it can be used for bank email and collaboration apps.
- Selective wipe: removal of bank apps and data from an enrolled personal device without touching the owner's personal data.

[S5] Remote and Flexible Work Policy (VB-POL-013), 6. Work Location
- Remote work is normally done at the home address registered with HR. Working from another location in the country requires the line manager's approval.
- Working from abroad is limited to 10 business days per calendar year. It requires approval from the line manager and the CISO, requested at least 10 business days in advance, and only the bank laptop may be used. Remote work is never allowed from a sanctioned country or from a high-risk country identified by the CCO (VB-POL-007).
- Staff must not work in public places such as cafes or public transport, where screens can be seen or calls overheard, except to read Public or Internal information.
```

## q09: What is the international per diem for a Band C employee?

**Reference answer:** USD 90 per day.

**System answer:** The international per diem for a Band C employee is USD 90 per day. [1]

**Citations:**
```
[1] -> S1 (VB-POL-012, 9. Meals and Incidentals (Per Diem))
```

**Excerpts the system was given:**
```
[S1] Expense and Business Travel Policy (VB-POL-012), 9. Meals and Incidentals (Per Diem)
A daily per diem covers meals, tips, and small incidental costs. No receipts are needed for the per diem.
Band | Domestic per day (USD) | International per day (USD)
A | 80 | 120
B | 70 | 100
C | 60 | 90
D and E | 50 | 80
- A day trip of more than 8 hours away from the usual workplace earns 50% of the domestic per diem.
- The per diem is reduced by 30% for each meal provided free during the day, for example by a conference or as part of the hotel rate.
- Alcohol is not reimbursed except as part of approved client entertainment (section 10).

[S2] Expense and Business Travel Policy (VB-POL-012), 10. Client Entertainment and Gifts
- Band B and more senior staff may host business meals with customers or prospective customers, up to USD 75 per person. Band C staff need the Head of Department's approval in advance.
- Amounts above USD 75 per person require approval from a Band A executive in advance.
- Every entertainment claim lists the attendees, their organizations, and the business purpose.
- Entertaining or giving gifts to public officials, including regulators, requires the CCO's written approval in advance (VB-POL-004, section 6.6).
- Gifts to customers are limited to bank-branded items worth no more than USD 50 per recipient and are recorded in the Gifts and Hospitality Register (VB-POL-004).
- Team celebrations are limited to USD 25 per person, no more than twice a year per team, with the Head of Department's approval.

[S3] Expense and Business Travel Policy (VB-POL-012), Revision History
Version | Date | Summary of changes
2.2 | 2026-02-01 | Added the per diem reduction for meals provided free. Allowance for staying with friends or family raised from USD 20 to USD 30 per night.
2.1 | 2025-01-15 | Business class for Band B limited to flights over 6 hours.

[S4] Expense and Business Travel Policy (VB-POL-012), 11. Corporate Cards
- Staff in Bands A to C who travel or entertain regularly may be issued a Veridane corporate card, provided by DFS Cards.
- Monthly limits: Band A USD 10,000; Band B USD 5,000; Band C USD 2,500.
- The card is for business expenses only. An accidental personal charge must be reported to the line manager and repaid within 5 business days.
- Cash withdrawals are allowed only when traveling abroad, up to USD 300 per trip.
- Cardholders reconcile each statement in the Veridane Expense Portal within 10 business days of the statement date. A card whose statement has not been reconciled after 30 days is suspended.
- A lost or stolen corporate card must be reported immediately to the Fraud Desk (0800 555 0177) or the DFS Contact Center, and to the line manager.

[S5] Expense and Business Travel Policy (VB-POL-012), 13. Cash Advances
Where a corporate card is not available, staff may request a travel cash advance of up to 80% of the expected per diem for the trip. The advance must be accounted for within 10 business days after returning. Any amount still outstanding after 30 days is deducted from salary.
```

## q11: What are the balance and daily transaction limits for a Tier 2 Veridane Wallet?

**Reference answer:** A maximum balance of USD 2,000 and a daily transaction limit of USD 1,000, with no international transfers.

**System answer:** The Tier 2 Veridane Wallet allows a maximum balance of USD 2,000 and a daily transaction limit of USD 1,000. [1]

**Citations:**
```
[1] -> S1 (VB-POL-007, 8. Tiered KYC for Digital Accounts and Veridane Wallet)
```

**Excerpts the system was given:**
```
[S1] Know Your Customer and Know Your Customer's Business Policy (VB-POL-007), 8. Tiered KYC for Digital Accounts and Veridane Wallet
Tier | Requirements | Maximum balance | Daily transaction limit | Restrictions
1 | Name, date of birth, phone number verified by one-time passcode, and national ID number verified electronically | USD 300 | USD 100 | No international transfers; no card
2 | Tier 1 plus an uploaded photo ID and a selfie liveness check matched to the ID | USD 2,000 | USD 1,000 | No international transfers
3 | Full CDD under section 6, completed in a branch or by video KYC at a digital hub | Standard account limits | Standard account limits | None beyond standard account terms
- Tier 1 and Tier 2 accounts can be opened entirely in Veridane Mobile.
- Customers upgrade to Tier 3 by visiting a branch or completing a video KYC session at a digital hub.
- Only one Tier 1 or Tier 2 wallet is allowed per national ID number.
- Selfie images are biometric data covered by VB-POL-003.

[S2] Company Profile and Policy Framework (VB-ORG-001), 7. Key Contacts
Service | Contact | Hours
IT Service Desk | Ext. 4000, servicedesk@veridane.example, Veridane Service Portal | 7:00 a.m. to 9:00 p.m. daily
Security Operations Center (SOC) | Ext. 4911, soc@veridane.example | 24/7
DFS Contact Center (customers: cards, ATMs, mobile and online banking, wallet) | 0800 555 0140 and 0800 555 0141 (toll-free), dfs.support@veridane.example | 24/7
DFS Staff Helpdesk (branch and head office staff) | Ext. 4300, dfs.helpdesk@veridane.example | 7:00 a.m. to 10:00 p.m. daily
DFS API Partner Support | api.support@veridane.example | Business days
Fraud Desk (report suspected fraud, block cards, fraud enquiries) | 0800 555 0177 and 0800 555 0178 (toll-free), fraud@veridane.example, staff ext. 4777 | 24/7
HR Service Center | Ext. 4200, hr@veridane.example | Business days, 8:00 a.m. to 5:00 p.m.
Data Protection Office | dpo@veridane.example | Business days
Compliance | compliance@veridane.example | Business days
Speak Up Line (whistleblowing) | 0800 555 0199 (toll-free), speakup.veridane.example | 24/7, run independently by ClearLine Assurance
Corporate Communications | media@veridane.example | Business days
Use the Fraud Desk for suspected fraud on a customer account, card, or wallet, including lost or stolen cards. Use the Speak Up Line for concerns about wrongdoing by staff or anyone else connected to the bank, especially if you want to stay anonymous (see VB-POL-005).

[S3] Know Your Customer and Know Your Customer's Business Policy (VB-POL-007), Revision History
Version | Date | Summary of changes
4.1 | 2026-02-15 | Added tiered KYC limits for digital accounts and Veridane Wallet (section 8) and KYCB requirements for merchants and API partners.
4.0 | 2025-03-01 | Beneficial ownership threshold for high-risk customers lowered from 25% to 10%.

[S4] Company Profile and Policy Framework (VB-ORG-001), 6. Working Hours
- Head office and regional offices: Monday to Friday, 8:00 a.m. to 5:00 p.m.
- Branch banking halls: Monday to Friday, 8:00 a.m. to 4:00 p.m. Nine designated Saturday branches also open from 9:00 a.m. to 1:00 p.m.
- Branch staff report by 7:30 a.m. so opening procedures are complete before customers arrive (see VB-POL-008).
- Digital hubs: 7:00 a.m. to 10:00 p.m. daily.
- Digital channels (Veridane Mobile, Veridane Online, Veridane Wallet, cards, ATMs, and POS) are available 24/7. Veridane Online and Veridane Mobile may be unavailable during planned maintenance on Sundays from 1:00 a.m. to 3:00 a.m. Card, ATM, and POS services stay available during this window.
A business day is any Monday to Friday that is not a public holiday listed in the Leave and Public Holidays Policy (VB-POL-009).

[S5] Company Profile and Policy Framework (VB-ORG-001), 1. About Veridane Bank > 1.2 Digital Financial Services
DFS is led by the Chief Digital Officer (CDO), who reports directly to the CEO. Five business heads report to the CDO:
DFS unit | Led by | Responsibilities
Digital Banking | Head, Digital Banking | Veridane Online (internet banking) and Veridane Mobile (mobile banking app)
Cards | Head, Cards | Debit, credit, and prepaid cards, including issuance, limits, and card disputes
Merchant Acquiring and Payments | Head, Merchant Acquiring and Payments | POS terminals, merchant onboarding, and the e-commerce payment gateway
Self-Service Channels | Head, Self-Service Channels | ATMs, cash deposit machines, and digital hubs
Wallets and Open Banking | Head, Wallets and Open Banking | Veridane Wallet, API services for partners, and the developer sandbox
As of January 2026 the bank operates 410 ATMs, of which 180 accept cash deposits, 18 digital hubs, and about 9,500 POS terminals at merchant locations. Digital hubs are self-service lounges with ATMs, cash deposit machines, account-opening kiosks, and video banking with contact center agents. Twelve hubs are inside branches and six are in shopping malls and on university campuses.
DFS also owns any new channel or digital touchpoint the bank introduces, unless EXCO assigns it elsewhere.
```

## q12: When does a cash deposit need a source of funds declaration, and when is a Currency Transaction Report filed?

**Reference answer:** A signed source of funds declaration is needed for cash deposits of USD 5,000 or more in one business day. A CTR is filed with the FIB within 7 days when a customer's cash transactions total USD 10,000 or more in one business day.

**System answer:** A cash deposit of USD 5,000 or more in one business day requires the depositor to sign a source‑of‑funds declaration [1], [2]. 
A Currency Transaction Report (CTR) is filed automatically by CoreLink when a customer’s cash transactions total USD 10,000 or more in one business day; the report is then submitted to the FIB within seven days [1], [2].

**Citations:**
```
[1] -> S1 (VB-POL-008, 7. Counter Services > 7.2 Cash deposits)
[2] -> S2 (VB-POL-007, 13. Cash Transactions)
```

**Excerpts the system was given:**
```
[S1] Branch Operations Policy (VB-POL-008), 7. Counter Services > 7.2 Cash deposits
- Cash deposits of USD 5,000 or more in one business day need a signed source of funds declaration from the depositor.
- CoreLink automatically produces a Currency Transaction Report when a customer's cash transactions total USD 10,000 or more in one business day.
- Staff who notice deposits that seem to be split to stay below these amounts must submit an Internal Suspicious Activity Report to the MLRO (VB-POL-007, section 14).

[S2] Know Your Customer and Know Your Customer's Business Policy (VB-POL-007), 13. Cash Transactions
- A depositor must sign a source of funds declaration for cash deposits of USD 5,000 or more in one business day.
- Cash deposits or withdrawals totaling USD 10,000 or more by or for one customer in one business day are reported to the FIB in a CTR within 7 days. CoreLink aggregates the amounts automatically and Compliance files the report.
- Splitting cash transactions to stay below these thresholds, known as structuring, is a red flag and must be reported to the MLRO.

[S3] Know Your Customer and Know Your Customer's Business Policy (VB-POL-007), 14. Reporting Suspicious Activity > 14.2 Red flags
Examples include:
- cash deposits just below USD 5,000 or USD 10,000;
- funds moving rapidly in and out of an account;
- activity inconsistent with the KYCB profile;
- reluctance to provide information;
- many wallets linked to one device;
- unrelated third parties repeatedly depositing into one account.

[S4] Internal Control Policy (VB-POL-006), 6. Key Control Requirements > 6.7 Reconciliations
Account or process | Frequency | Responsible
Branch cash and vault | Daily | BOM
ATM and cash deposit machine cash | Daily | Branch or Cash Center, with DFS Self-Service Channels
Card and POS settlement accounts | Daily | DFS Cards, and Merchant Acquiring and Payments
Nostro accounts | Daily | Treasury Operations
Suspense and sundry accounts | Daily | Department that owns the account
All other general ledger accounts | Monthly | Department that owns the account
Each reconciliation is prepared by one person and reviewed by another. Unreconciled items open for more than 30 days are reported to the CFO every month. Items open for more than 90 days are reported to the Board Audit Committee every quarter.

[S5] Branch Operations Policy (VB-POL-008), 6. Cash Management > 6.5 Cash differences
- A teller who finds a shortage or overage must report it to the BOM immediately. The difference is recorded in the CoreLink cash difference register.
- Overages are credited to the branch suspense account. A teller must never keep an overage.
- The BOM investigates any shortage above USD 100 and reports the findings to the BM within 1 business day.
- A teller with three shortages in any 3-month period is referred to HR under VB-POL-004.
```

## q20: Who is allowed to speak to the media about a digital channel outage?

**Reference answer:** The Chief Digital Officer (CDO).

**System answer:** The only person authorized to speak to the media about a digital channel outage is the Chief Digital Officer (CDO). [1]

**Citations:**
```
[1] -> S1 (VB-POL-011, 4. Authorized Spokespersons)
```

**Excerpts the system was given:**
```
[S1] Internal and Corporate Communication Policy (VB-POL-011), 4. Authorized Spokespersons
Only the people below may speak to the media or make public statements for the bank, and only on the topics listed.
Topic | Authorized spokesperson
Bank strategy, performance, and major incidents | CEO
Financial results | CEO and CFO
Digital channels, digital products, and digital outages | CDO
Security incidents and data breaches | CEO, supported by the CISO and the DPO
Branch and regional matters | Regional Manager, with HCC approval for each engagement
All other media enquiries | HCC
The CIO/CTO, the CISO, and the DPO speak to the media only with the CEO's approval. Spokespersons complete media training every 2 years.

[S2] Internal and Corporate Communication Policy (VB-POL-011), 9. Crisis Communications > 9.2 When the team is activated
- Severity 1 security incidents (VB-POL-001, section 12.3)
- Robberies or other serious incidents at branches
- Digital channel outages lasting more than 2 hours
- Fraud or data breaches likely to become public
- Any other event likely to attract significant media attention

[S3] Whistleblowing Policy (VB-POL-005), 5. How to Report > 5.1 Reporting channels
Channel | Details
Speak Up Line (phone) | 0800 555 0199, toll-free, 24/7, run independently by ClearLine Assurance
Speak Up web portal | speakup.veridane.example, 24/7
Email | whistleblowing@veridane.example, received by the Whistleblowing Unit in Compliance
Letter | Chief Compliance Officer, 14 Admiralty Crescent, Port Halden, marked "Strictly Private and Confidential"
Board Audit Committee Chair | bac.chair@veridane.example

[S4] Internal and Corporate Communication Policy (VB-POL-011), 7. Customer Communications > 7.1 Notices and timelines
Situation | Requirement
Changes to fees, charges, or account terms | Customers notified at least 30 days before the change takes effect
Emergency branch closure | Notice at the branch door, a Veridane Mobile notification, and a website update within 1 hour of the RM's approval
Planned maintenance outside the standard Sunday window (1:00 a.m. to 3:00 a.m.) | At least 48 hours' notice in Veridane Mobile, Veridane Online, and on the website
Unplanned digital channel outage lasting more than 30 minutes | First update on the website and official social media within 30 minutes of confirming the outage, then updates every 60 minutes until service is restored
Personal data breach affecting customers | Notice drafted by the DPO with Corporate Communications and approved by the CEO (VB-POL-003)

[S5] Ethics and Code of Conduct Policy (VB-POL-004), 11. Public Statements and Social Media
Only authorized spokespersons may speak for the bank to the media. Staff must not disclose confidential information or comment on customers, colleagues, or bank matters on social media. Detailed rules are in the Internal and Corporate Communication Policy (VB-POL-011).
```

## q22: Who do I call to report a lost or stolen card?

**Reference answer:** The Fraud Desk, 24/7, on 0800 555 0177 or 0800 555 0178 (staff ext. 4777, fraud@veridane.example).

**System answer:** Call the Fraud Desk immediately (0800 555 0177 or 0800 555 0178) or the DFS Contact Center, and inform your line manager. [1] [2]

**Citations:**
```
[1] -> S2 (VB-POL-012, 11. Corporate Cards)
[2] -> S3 (VB-ORG-001, 7. Key Contacts)
```

**Excerpts the system was given:**
```
[S1] Remote and Flexible Work Policy (VB-POL-013), 8. Security Requirements > 8.5 Lost devices and incidents
A lost or stolen bank laptop or enrolled device, and any other security incident, must be reported to the SOC within one hour (VB-POL-001, section 12).

[S2] Expense and Business Travel Policy (VB-POL-012), 11. Corporate Cards
- Staff in Bands A to C who travel or entertain regularly may be issued a Veridane corporate card, provided by DFS Cards.
- Monthly limits: Band A USD 10,000; Band B USD 5,000; Band C USD 2,500.
- The card is for business expenses only. An accidental personal charge must be reported to the line manager and repaid within 5 business days.
- Cash withdrawals are allowed only when traveling abroad, up to USD 300 per trip.
- Cardholders reconcile each statement in the Veridane Expense Portal within 10 business days of the statement date. A card whose statement has not been reconciled after 30 days is suspended.
- A lost or stolen corporate card must be reported immediately to the Fraud Desk (0800 555 0177) or the DFS Contact Center, and to the line manager.

[S3] Company Profile and Policy Framework (VB-ORG-001), 7. Key Contacts
Service | Contact | Hours
IT Service Desk | Ext. 4000, servicedesk@veridane.example, Veridane Service Portal | 7:00 a.m. to 9:00 p.m. daily
Security Operations Center (SOC) | Ext. 4911, soc@veridane.example | 24/7
DFS Contact Center (customers: cards, ATMs, mobile and online banking, wallet) | 0800 555 0140 and 0800 555 0141 (toll-free), dfs.support@veridane.example | 24/7
DFS Staff Helpdesk (branch and head office staff) | Ext. 4300, dfs.helpdesk@veridane.example | 7:00 a.m. to 10:00 p.m. daily
DFS API Partner Support | api.support@veridane.example | Business days
Fraud Desk (report suspected fraud, block cards, fraud enquiries) | 0800 555 0177 and 0800 555 0178 (toll-free), fraud@veridane.example, staff ext. 4777 | 24/7
HR Service Center | Ext. 4200, hr@veridane.example | Business days, 8:00 a.m. to 5:00 p.m.
Data Protection Office | dpo@veridane.example | Business days
Compliance | compliance@veridane.example | Business days
Speak Up Line (whistleblowing) | 0800 555 0199 (toll-free), speakup.veridane.example | 24/7, run independently by ClearLine Assurance
Corporate Communications | media@veridane.example | Business days
Use the Fraud Desk for suspected fraud on a customer account, card, or wallet, including lost or stolen cards. Use the Speak Up Line for concerns about wrongdoing by staff or anyone else connected to the bank, especially if you want to stay anonymous (see VB-POL-005).

[S4] Whistleblowing Policy (VB-POL-005), 3. What to Report > 3.1 What this policy is not for
Issue | Where to go
A personal grievance about pay, performance ratings, or working conditions | The HR grievance procedure, through the HR Service Center (ext. 4200)
Issue | Where to go
A customer complaint about service | The complaints procedure in a branch or through the DFS Contact Center
A suspicious transaction on a customer's own card, wallet, or account | The Fraud Desk, 24/7, on 0800 555 0177 or 0800 555 0178
If a grievance or complaint also reveals wrongdoing, for example a manager falsifying records, it should be reported under this policy.

[S5] Branch Operations Policy (VB-POL-008), 10. ATMs and Digital Hubs
- DFS Self-Service Channels owns ATMs, cash deposit machines, and digital hub equipment. The BM is responsible for their physical security and for a daily visual check for damage or skimming devices.
- If staff suspect a skimming device, they take the ATM out of service, leave the device in place, and call the Fraud Desk (staff ext. 4777) and the Bank Security Control Room.
- ATMs are replenished under dual control, and ATM cash is reconciled daily (VB-POL-006).
- Captured cards are removed under dual control, recorded in the captured card register, and kept in the vault for 5 business days. A card is returned only to the cardholder, on presentation of original ID. Unclaimed cards are destroyed under dual control on the sixth business day, and the customer is notified by SMS.
- In-branch digital hubs have their own entrance and are physically separated from the banking hall and back office, so they can stay open from 7:00 a.m. to 10:00 p.m. after the banking hall closes.
```

## q23: What changed in the latest version of the Password and Access Control Policy?

**Reference answer:** Version 3.1 raised the minimum length for standard accounts from 12 to 14 characters and limited the SMS fallback for MFA to 7 days.

**System answer:** The latest version (3.1) of the Password and Access Control Policy introduced two changes: the minimum password length for standard accounts was increased from 12 to 14 characters, and the use of SMS as a fallback for multi‑factor authentication was limited to 7 days. [1]

**Citations:**
```
[1] -> S6 (VB-POL-002, 15. Revision History)
```

**Excerpts the system was given:**
```
[S1] Password and Access Control Policy (VB-POL-002), Document information
Document ID: VB-POL-002
Title: Password and Access Control Policy
Version: 3.1
Effective date: 2026-02-01
Owner: Chief Information Security Officer (CISO)
Approved by: Board Risk Committee
Review cycle: Annual
Classification: Internal

[S2] Information Security Policy (VB-POL-001), 6. Access Control
Access to information and systems follows the principles of least privilege and need-to-know. Detailed rules for passwords, multi-factor authentication, access requests, access reviews, and removal of access when staff leave are in the Password and Access Control Policy (VB-POL-002). Segregation of duties rules are in the Internal Control Policy (VB-POL-006).

[S3] Password and Access Control Policy (VB-POL-002), 1. Purpose
This policy sets the rules for passwords, multi-factor authentication, and the granting, review, and removal of access to Veridane Bank systems. It supports the Information Security Policy (VB-POL-001).

[S4] Password and Access Control Policy (VB-POL-002), 4. Password Requirements > 4.4 Initial and reset passwords
Passwords issued by the IT Service Desk for a new account or a reset are one-time passwords. They must be changed at first sign-in and expire 72 hours after issue if not used. The password is always sent through a different channel from the username.

[S5] Password and Access Control Policy (VB-POL-002), 12. Compliance and Enforcement
Breaches of this policy are handled under the disciplinary procedure in the Ethics and Code of Conduct Policy (VB-POL-004). Knowingly sharing a password or MFA code, or using another person's credentials, is treated as gross misconduct.

[S6] Password and Access Control Policy (VB-POL-002), 15. Revision History
Version 3.1, 2026-02-01: Minimum length for standard accounts raised from 12 to 14 characters. SMS fallback for MFA limited to 7 days.
Version 3.0, 2025-01-10: Introduced PAM vault checkout rules. Dormant account limit reduced from 60 to 45 days.
```
