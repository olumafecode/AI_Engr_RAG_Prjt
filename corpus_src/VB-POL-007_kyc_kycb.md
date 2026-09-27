# Know Your Customer and Know Your Customer's Business Policy

| Field | Value |
|---|---|
| Document ID | VB-POL-007 |
| Version | 4.1 |
| Effective date | 2026-02-15 |
| Owner | Chief Compliance Officer (CCO) |
| Approved by | Board Risk Committee |
| Review cycle | Annual |
| Classification | Internal |

## 1. Purpose

Veridane Bank must know who its customers are and understand what they do before it serves them. This protects the bank and the financial system from money laundering, terrorist financing, fraud, and sanctions breaches. It also meets the requirements of the Central Monetary Authority (CMA) and the Financial Intelligence Bureau (FIB).

Know Your Customer (KYC) confirms a customer's identity. Know Your Customer's Business (KYCB) goes further. It builds an understanding of the customer's business, sources of funds, and expected account activity, so that unusual activity stands out.

## 2. Scope

This policy applies to every customer relationship in every segment and channel, including:

- individuals and businesses opening accounts in branches, at digital hubs, or through Veridane Mobile and Veridane Online;
- Veridane Wallet users;
- merchants onboarded for POS terminals and the e-commerce payment gateway;
- partners using the bank's production APIs;
- signatories, directors, beneficial owners, and guarantors connected to any of these.

## 3. Definitions

- **Customer due diligence (CDD):** identifying and verifying a customer and understanding the purpose of the relationship.
- **Enhanced due diligence (EDD):** additional checks applied to high-risk customers.
- **Beneficial owner:** a natural person who ultimately owns or controls 25% or more of a business customer's shares or voting rights, or who otherwise controls the business. For high-risk business customers the threshold is 10%.
- **Politically exposed person (PEP):** someone who holds or has held a prominent public function, such as a minister, senior judge, senior military officer, legislator, senior political party official, or senior executive of a state-owned company. Immediate family members and close associates are also treated as PEPs. A person remains a PEP for at least 24 months after leaving the position.
- **Suspicious Transaction Report (STR):** a report filed with the FIB when the bank suspects funds are linked to crime or terrorism.
- **Currency Transaction Report (CTR):** a report filed with the FIB for large cash transactions (section 13).

## 4. Roles and Responsibilities

- **Board Risk Committee:** approves this policy.
- **CCO:** owns this policy and approves all PEP relationships.
- **MLRO:** reviews internal suspicious activity reports, files STRs with the FIB, and is the bank's contact point with the FIB.
- **Central KYC Unit:** part of Operations under the COO. It verifies documents and approves the KYC record before any account is activated.
- **Branch staff, relationship officers, and DFS onboarding teams:** collect information and documents, see original documents, and complete the KYCB profile.
- **Branch Managers:** approve high-risk accounts opened in their branch, together with the MLRO.
- **DFS:** designs digital onboarding with the controls in section 8. Merchant Acquiring and Payments applies section 7 to merchants.
- **Compliance:** checks a random sample of at least 5% of the accounts opened each month.

## 5. Risk-Based Approach

Every customer receives a risk rating of Low, Medium, or High in CoreLink at onboarding. The rating considers:

- customer type, occupation, or industry;
- country of residence, nationality, and countries of operation;
- products and channels used;
- expected transaction volumes and use of cash;
- PEP status and adverse media.

These customers are always rated High:

- PEPs;
- cash-intensive businesses, such as bureaux de change, fuel stations, car dealers, and dealers in precious metals and stones;
- money service businesses and payment companies;
- non-resident customers;
- charities and non-profit organizations;
- customers with links to high-risk jurisdictions identified by the CCO.

## 6. Customer Due Diligence for Individuals

### 6.1 Information collected

Full name, date of birth, residential address, nationality, occupation and employer, phone number, email address, national ID number, expected source of funds, and expected monthly account activity.

### 6.2 Documents

- An original, valid, government-issued photo ID: national ID card, passport, or driver's license.
- Proof of address dated within the last 3 months: a utility bill, bank statement, or tenancy agreement.
- A photograph taken at onboarding.

### 6.3 Verification

- The national ID number is verified electronically against the national identity database.
- Branch staff must see original documents and stamp each copy "Original Sighted" with their name, the date, and their signature.
- A fingerprint is captured at branch onboarding. Fingerprints are biometric data and are classified as Restricted (VB-POL-003).

### 6.4 Customers under 18

Accounts for customers under 18 are opened only as youth savings accounts, with a parent or guardian as co-signatory. The parent or guardian completes full CDD.

## 7. Know Your Customer's Business (KYCB)

### 7.1 Business documents

- Certificate of incorporation or registration.
- Constitutional documents.
- Register of directors and shareholders, dated within the last 12 months.
- Board resolution authorizing the account and naming the signatories.
- Tax identification number.
- Proof of business address.

### 7.2 Connected individuals

Every director, signatory, and beneficial owner is identified and verified as an individual under section 6.

### 7.3 KYCB profile

The relationship officer completes a KYCB profile in CoreLink for every business customer. It records:

- the nature of the business, its products, and its main customers and suppliers;
- the countries where the business operates or trades;
- the source of funds, and for high-risk customers the source of wealth of the beneficial owners;
- expected monthly turnover, typical transaction types, and expected cash volumes.

The KYCB profile is the baseline that transaction monitoring uses to spot unusual activity. It must be updated whenever the business changes materially.

### 7.4 Site visits

The relationship officer visits the customer's premises and records a visit report with photographs in CoreLink:

- before the account is activated, for high-risk business customers;
- within 30 days of account opening, for all other SME and corporate customers;
- before any POS terminal is deployed, for merchants.

### 7.5 API partners

Registration on the developer portal is enough for access to the sandbox. Production API access is granted only after the partner has completed KYCB, passed the security assessment in VB-POL-001 (section 11), and signed a data processing agreement under VB-POL-003.

## 8. Tiered KYC for Digital Accounts and Veridane Wallet

| Tier | Requirements | Maximum balance | Daily transaction limit | Restrictions |
|---|---|---|---|---|
| 1 | Name, date of birth, phone number verified by one-time passcode, and national ID number verified electronically | USD 300 | USD 100 | No international transfers; no card |
| 2 | Tier 1 plus an uploaded photo ID and a selfie liveness check matched to the ID | USD 2,000 | USD 1,000 | No international transfers |
| 3 | Full CDD under section 6, completed in a branch or by video KYC at a digital hub | Standard account limits | Standard account limits | None beyond standard account terms |

- Tier 1 and Tier 2 accounts can be opened entirely in Veridane Mobile.
- Customers upgrade to Tier 3 by visiting a branch or completing a video KYC session at a digital hub.
- Only one Tier 1 or Tier 2 wallet is allowed per national ID number.
- Selfie images are biometric data covered by VB-POL-003.

## 9. Enhanced Due Diligence

For every high-risk customer, the bank must:

- obtain and verify the source of funds, and for PEPs and owners of high-risk businesses, the source of wealth;
- obtain approval before the relationship begins: the BM and the MLRO for high-risk customers, and the CCO for PEPs;
- apply enhanced transaction monitoring with lower alert thresholds;
- review the relationship at least every 12 months.

## 10. Prohibited Relationships

The bank must not open or keep:

- anonymous accounts or accounts in obviously fictitious names;
- accounts for shell banks;
- relationships with customers or beneficial owners on sanctions lists;
- accounts for unlicensed money service businesses, gambling operators, or virtual asset service providers;
- relationships where the customer refuses to provide required information or documents.

If CDD cannot be completed, the account must not be opened. For an existing customer, the relationship is restricted and the MLRO considers whether to file an STR.

## 11. Sanctions Screening

- Customers, directors, signatories, and beneficial owners are screened against sanctions lists at onboarding and every day after that.
- All payments are screened in real time before they are processed.
- Compliance reviews potential matches within 24 hours, and the payment is held in the meantime.
- For a confirmed match, the assets are frozen immediately and the match is reported to the FIB within 24 hours. The customer is not told.

## 12. Ongoing Monitoring and Periodic Review

### 12.1 Transaction monitoring

An automated system compares each customer's activity with their KYCB profile and risk rating. Compliance reviews alerts within 5 business days, or within 2 business days for high-risk customers.

### 12.2 Periodic review

| Risk rating | Review frequency |
|---|---|
| High | Every 12 months |
| Medium | Every 24 months |
| Low | Every 36 months |

### 12.3 Trigger events

A review is also required when ownership or control changes, when activity changes significantly without explanation, when adverse media appears, after an STR is filed, or when an ID document expires.

### 12.4 Expired identification

Customers are notified when their ID expires. If the ID has not been updated within 90 days after expiry, the account is placed on post-no-debit status, which allows credits only, until the customer provides a valid ID.

### 12.5 Dormant accounts

An account with no customer-initiated transaction for 12 months becomes dormant. To reactivate it, the customer must verify their identity in a branch or by video KYC at a digital hub, and their KYC record must be refreshed.

## 13. Cash Transactions

- A depositor must sign a source of funds declaration for cash deposits of USD 5,000 or more in one business day.
- Cash deposits or withdrawals totaling USD 10,000 or more by or for one customer in one business day are reported to the FIB in a CTR within 7 days. CoreLink aggregates the amounts automatically and Compliance files the report.
- Splitting cash transactions to stay below these thresholds, known as structuring, is a red flag and must be reported to the MLRO.

## 14. Reporting Suspicious Activity

### 14.1 Internal reporting

Any staff member who knows or suspects that a customer is involved in money laundering or terrorist financing must submit an Internal Suspicious Activity Report (ISAR) to the MLRO. ISARs go through the Compliance portal or to mlro@veridane.example, within 1 business day of forming the suspicion. Reporting to the MLRO satisfies the staff member's personal reporting duty. If the transaction has not yet been processed, the staff member should contact the MLRO before processing it where possible.

### 14.2 Red flags

Examples include:

- cash deposits just below USD 5,000 or USD 10,000;
- funds moving rapidly in and out of an account;
- activity inconsistent with the KYCB profile;
- reluctance to provide information;
- many wallets linked to one device;
- unrelated third parties repeatedly depositing into one account.

### 14.3 MLRO review and STR filing

The MLRO reviews every ISAR. If the suspicion is reasonable, the MLRO files an STR with the FIB within 24 hours of reaching that conclusion. The MLRO records the reasons for any decision not to file.

### 14.4 Tipping off

Staff must never tell the customer, or anyone not involved, that an ISAR or STR has been made or that an investigation is under way. Tipping off is a criminal offense and gross misconduct under VB-POL-004. ISAR and STR details are classified as Restricted (VB-POL-001).

## 15. Record Keeping

| Record | Retention period |
|---|---|
| KYC and KYCB documents, including site visit reports | 7 years after the customer relationship ends |
| Transaction records | 7 years after the transaction |
| ISARs, STRs, CTRs, and MLRO decision records | 7 years after filing or decision |

These periods match the retention schedule in VB-POL-003.

## 16. Training

All staff complete annual anti-money laundering and KYC training by 31 October each year. New staff complete it within 30 days of their start date. Staff who open accounts, work in DFS onboarding, or work in the Central KYC Unit also complete an advanced module each year.

## 17. Independent Testing and Enforcement

Internal Audit tests the controls in this policy every year and reports the results to the Board Audit Committee. Breaches of this policy are handled under VB-POL-004.

## 18. Related Documents

- VB-POL-001 Information Security Policy
- VB-POL-003 Data Protection and Privacy Policy
- VB-POL-004 Ethics and Code of Conduct Policy
- VB-POL-005 Whistleblowing Policy
- VB-POL-008 Branch Operations Policy

## Revision History

| Version | Date | Summary of changes |
|---|---|---|
| 4.1 | 2026-02-15 | Added tiered KYC limits for digital accounts and Veridane Wallet (section 8) and KYCB requirements for merchants and API partners. |
| 4.0 | 2025-03-01 | Beneficial ownership threshold for high-risk customers lowered from 25% to 10%. |
