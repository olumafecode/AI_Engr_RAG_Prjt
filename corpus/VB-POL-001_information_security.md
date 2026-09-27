---
doc_id: VB-POL-001
title: Information Security Policy
version: "4.2"
effective_date: 2026-02-01
owner: Chief Information Security Officer (CISO)
approved_by: Board Risk Committee
review_cycle: Annual
classification: Internal
---

# Information Security Policy

## 1. Purpose

This policy sets the minimum requirements Veridane Bank uses to protect the confidentiality, integrity, and availability of its information and systems. Customers trust the bank with their money and their personal data, and the Central Monetary Authority expects the bank to protect both. Every staff member shares that responsibility.

## 2. Scope

This policy applies to:

- all staff members, contractors, vendors, and interns;
- all information owned or held by the bank, in any form (electronic, paper, or spoken);
- all bank systems, networks, devices, and cloud services, including personal devices enrolled for bank use under the Remote and Flexible Work Policy (VB-POL-013).

## 3. Roles and Responsibilities

- **Board Risk Committee:** approves this policy and receives a security report from the CISO every quarter.
- **CISO:** owns this policy, runs the information security program and the Security Operations Center (SOC), and approves exceptions jointly with the CRO.
- **Information owners:** the Band B head of the department that creates or is accountable for a set of information. They classify it and approve who may access it.
- **Line managers:** make sure their staff complete security training, approve access requests, and complete access reviews on time.
- **CIO/CTO and IT Operations:** the CIO/CTO is accountable for the security of the technology infrastructure. IT Operations, part of the Technology Division, implements technical controls, including patching, backups, and endpoint protection.
- **Chief Digital Officer:** makes sure DFS channels, including ATMs, cards, POS terminals, wallets, and APIs, meet the requirements of this policy.
- **All staff:** follow this policy, protect the information they handle, and report security incidents within one hour.

## 4. Information Classification

All information must be classified at one of four levels. Information without a label is treated as Confidential until the information owner classifies it.

| Level | Meaning | Examples | Handling rules |
|---|---|---|---|
| Public | Approved for release outside the bank | Published interest rates, press releases, website content | No restrictions once approved. Only Corporate Communications may release new public information. |
| Internal | For staff use; limited harm if disclosed | Policies, staff directory, training material, internal memos | Do not share outside the bank without the information owner's approval. |
| Confidential | Significant harm to the bank or its customers if disclosed | Customer account details, loan files, staff records, internal audit reports | Share only on a need-to-know basis. Encrypt when sending outside the bank. Never store in personal email or personal cloud storage. |
| Restricted | Severe harm, legal liability, or regulatory action if disclosed | Full card numbers, passwords and encryption keys, board papers before release, suspicious transaction report details | Access only by named individuals approved by the information owner and the CISO. Encrypted at rest and in transit. Print only on secure-release printers. Paper copies must not leave bank premises. |

Staff label documents in the header or footer. Emails are labeled by putting the level in square brackets at the start of the subject line, for example "[CONFIDENTIAL] Q3 loan review".

## 5. Acceptable Use

### 5.1 Personal use

Bank systems are provided for bank business. Limited personal use of email and the internet is allowed if it does not interfere with work, does not breach any bank policy, and never involves Confidential or Restricted information.

### 5.2 Prohibited activities

Staff must not:

- install software that IT has not approved;
- use personal email or personal cloud storage for bank information, or forward bank email to a personal account;
- connect unapproved devices to the bank network;
- disable, bypass, or tamper with any security control;
- look up customer or staff records without a business reason, including their own accounts or those of family and friends;
- enter Confidential or Restricted information into any generative AI tool. The bank's approved assistant, Veridane Assist, may be used with Public and Internal information only, unless the CISO has approved a tool for a higher level in writing.

### 5.3 Monitoring

The bank monitors the use of its systems, email, and networks to protect customers and meet regulatory obligations. Staff should have no expectation of privacy when using bank systems, subject to applicable law and the Data Protection and Privacy Policy (VB-POL-003).

## 6. Access Control

Access to information and systems follows the principles of least privilege and need-to-know. Detailed rules for passwords, multi-factor authentication, access requests, access reviews, and removal of access when staff leave are in the Password and Access Control Policy (VB-POL-002). Segregation of duties rules are in the Internal Control Policy (VB-POL-006).

## 7. Endpoint and Device Security

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

## 8. Network and Remote Access

- Remote access to bank systems is only through the bank VPN with multi-factor authentication.
- Staff may use public Wi-Fi only with the VPN connected. Shared or public computers, such as those in hotels or internet cafes, must never be used to access bank systems.
- Branch networks are segmented. ATMs, CCTV, and building systems run on separate network segments from staff workstations.
- The head office guest Wi-Fi is isolated from the bank network. Staff must not connect bank devices to it.

## 9. Email, Phishing, and Social Engineering

- Emails from outside the bank are marked [EXTERNAL] in the subject line.
- Report suspicious emails with the Report Phish button in the email client, or forward them to phishing@veridane.example. Do not click links, open attachments, or reply.
- An emailed request to change payment details, beneficiary accounts, or supplier bank details must be verified by calling the requester on a phone number already held on file, never a number given in the email. The Internal Control Policy (VB-POL-006) contains the same requirement.
- IT staff will never ask for your password or MFA code. Any such request, however it arrives, must be reported to the SOC.
- The Information Security team runs a simulated phishing exercise every quarter. A staff member who fails two simulations in a row must complete remedial training within 10 business days. A third consecutive failure is referred to the line manager and HR.

## 10. Clean Desk and Clear Screen

- Confidential and Restricted papers must be locked away whenever a desk is unattended and at the end of each day.
- Print jobs must be collected immediately. Confidential and Restricted documents must be printed with secure-release printing.
- Confidential and Restricted paper goes in locked shred bins, never in general waste.
- Whiteboards and flip charts must be cleared after meetings.
- At branch counters, customer documents must not be left on the counter or where other customers can see them (see VB-POL-008).

## 11. Third-Party Security

- A vendor that will access Confidential or Restricted information, or connect to the bank network, must pass a security assessment by the Information Security team before the contract is signed.
- Vendor contracts must include confidentiality obligations, the bank's right to audit, notice to the bank of any security breach within 24 hours, and return or destruction of bank data when the contract ends.
- High-risk vendors are reassessed every year. Other vendors are reassessed every two years.
- Vendor remote access goes through the privileged access management system, is time-limited, and is recorded.

## 12. Security Incident Management

### 12.1 What counts as an incident

A security incident is any event that actually or potentially compromises the confidentiality, integrity, or availability of bank information or systems. Examples include malware, a lost device, an email containing customer data sent to the wrong person, unauthorized access, and suspected fraud involving bank systems.

### 12.2 Reporting

All staff must report an actual or suspected incident to the SOC (ext. 4911 or soc@veridane.example) within one hour of discovering it. Staff must not investigate on their own, delete evidence, or discuss the incident outside the response team.

### 12.3 Severity levels

| Severity | Examples | Escalation |
|---|---|---|
| 1, Critical | Ransomware, confirmed breach of Restricted data, attack causing a CoreLink outage | CISO informs the CEO within 1 hour. CMA notified within 24 hours. |
| 2, High | Compromised staff account, malware on several devices | CISO informed within 4 hours. |
| 3, Medium | Malware on a single device, loss of an encrypted laptop | Handled by the SOC and included in the monthly security report. |
| 4, Low | Blocked phishing email, spam | Logged by the SOC. |

### 12.4 Personal data breaches

If an incident involves personal data, the SOC informs the Data Protection Officer immediately. The DPO decides whether the breach must be notified to the Data Protection Commission or to affected customers, following VB-POL-003.

### 12.5 Post-incident review

The CISO leads a post-incident review within 10 business days of closing any Severity 1 or Severity 2 incident. Lessons learned are reported to the Board Risk Committee.

## 13. Logging and Monitoring

The SOC collects security logs from servers, network devices, and critical applications in one central system. Logs are kept for 12 months online and a further 6 years in archive, 7 years in total. Activity performed with privileged accounts is logged and reviewed every week.

## 14. Backup and Recovery

- CoreLink, payment systems, and email are backed up daily. An immutable offline copy is taken every week.
- Restores are tested every quarter.
- CoreLink recovery objectives: recovery time objective (RTO) of 4 hours and recovery point objective (RPO) of 15 minutes.

## 15. Security Awareness Training

- New staff complete the Information Security Essentials course within 30 days of their start date.
- All staff complete the annual refresher by 30 June each year.
- Staff more than 14 days overdue are reported to their line manager and the CHRO. Staff more than 30 days overdue have their system access suspended until they complete the course.

## 16. Compliance and Enforcement

Breaches of this policy are handled under the disciplinary procedure in the Ethics and Code of Conduct Policy (VB-POL-004) and may lead to dismissal. Suspected criminal activity is referred to the relevant authorities. Internal Audit reviews compliance with this policy at least once a year.

## 17. Exceptions

Exceptions follow the Policy Exception Request process in VB-ORG-001, section 8.3. They are approved jointly by the CISO and the CRO and last no longer than 6 months.

## 18. Related Documents

- VB-ORG-001 Company Profile and Policy Framework
- VB-POL-002 Password and Access Control Policy
- VB-POL-003 Data Protection and Privacy Policy
- VB-POL-004 Ethics and Code of Conduct Policy
- VB-POL-006 Internal Control Policy
- VB-POL-008 Branch Operations Policy
- VB-POL-013 Remote and Flexible Work Policy

## Revision History

| Version | Date | Summary of changes |
|---|---|---|
| 4.2 | 2026-02-01 | Added generative AI rules (section 5.2). Critical patch window reduced from 14 days to 7 days. |
| 4.1 | 2025-03-01 | Added phishing simulation remediation steps. |
| 4.0 | 2024-01-15 | Full rewrite. Introduced the four-level classification scheme. |
