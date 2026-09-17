# System Architecture & Control Flow Blueprint
**Project:** Veridian Corp Internal IT Support Agent  
**Environment / Engine:** Antigravity Agent Framework  
**Simulated Period:** 21 Sep 2026 – 25 Sep 2026  

---

## 1. High-Level Architecture Overview

The Veridian IT Support Agent uses a **Deterministic Hybrid Control Pipeline**. To ensure 100% policy compliance and zero hallucination, LLMs are not allowed to make ungrounded decisions. Instead, the system uses LLMs for entity extraction, semantic intent parsing, and natural response generation, while business logic execution is strictly handled by a deterministic State Engine.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            USER INPUT REQUEST                            │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       NODE 1: INTENT & ENTITY PARSER                     │
│  - Extracts Intent Category (Hardware, Access, Software, Security, etc.) │
│  - Extracts Entities (Device age, error details, user role, etc.)       │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      NODE 2: GROUNDED CONTEXT RETRIEVAL                  │
│  - Queries Knowledge Base (KB-01 to KB-10)                               │
│  - Fetches Asset Management Policy (4-year refresh rule)                  │
│  - Inspects Historical Ticket Queue (TK-1042 to TK-1051) for precedent   │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       NODE 3: POLICY DECISION ENGINE                     │
│  - Evaluates explicit conditions (Tenure check, Security escalation)     │
│  - Assigns System State: RESOLVE | APPROVE | ROUTE | CLARIFY             │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       NODE 4: ACTION EXECUTION HOOKS                     │
│  - Triggers automated tasks (Account Unlock, Security Alert, Ticket Routing)│
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       NODE 5: RESPONSE GENERATION                        │
│  - Generates polished, empathetic, policy-grounded user response          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core State Schema

The entire state machine operates on a unified, strongly typed JSON state object passed between Antigravity nodes:

```json
{
  "request_id": "REQ-01",
  "employee": {
    "name": "Aditi Sharma",
    "email": "aditi.sharma@veridian-corp.example",
    "is_contractor": false
  },
  "intent_category": "HARDWARE_LAPTOP",
  "extracted_entities": {
    "device_age_years": 3.5,
    "issue_type": "hardware_failure",
    "is_completely_dead": true
  },
  "matched_kb_rules": ["KB-03", "Asset Management Policy"],
  "decision": {
    "status": "APPROVED",
    "action_type": "INITIATE_REPLACEMENT",
    "requires_manager_approval": false,
    "requires_finance_approval": false,
    "routing_target": "IT_HARDWARE_DISPATCH"
  },
  "audit_trail": {
    "policy_reasoning": "Laptop is 3.5 years old (>3 years KB-03 threshold) and experiencing verified hardware failure."
  }
}
```

---

## 3. Decision Matrix & Action Taxonomy

| Intent Category | Direct Rule / KB Reference | System Action State | Routing Target / Tool Call |
| :--- | :--- | :--- | :--- |
| **Password Locked Out** | KB-01 (Manual unlock after 5 fails) | `RESOLVE` | `unlock_user_account()` |
| **VPN (Full-time)** | KB-02 (Auto-grant / 90-day renewal) | `RESOLVE` | `renew_vpn_credentials()` |
| **VPN (Contractor)** | KB-02 (Manager approval required) | `ROUTE` | `route_to_manager()` |
| **Laptop (>3 yrs OR failure)**| KB-03 / Asset Policy | `APPROVE` | `dispatch_replacement_laptop()` |
| **Laptop (<3 yrs, minor issue)**| KB-03 / Asset Policy | `ROUTE` | `route_to_hardware_repair()` |
| **Non-Catalog Software** | KB-04 (3–5 day Security review) | `ROUTE` | `escalate_to_security_review()` |
| **Printer Issue** | KB-05 (Spooler restart -> Asset Tag) | `RESOLVE` / `ROUTE` | `restart_spooler()` |
| **Mailbox Over Quota** | KB-06 (Archive or Manager approval >25GB)| `ROUTE` | `request_quota_approval()` |
| **Guest Wi-Fi** | KB-07 (Self-service front desk kiosk) | `RESOLVE` | `provide_kiosk_instructions()` |
| **Expense Tool** | KB-08 (Owned by Finance, not IT) | `ROUTE` | `redirect_to_finance()` |
| **Phishing / Threat** | KB-09 (Immediate alert, do NOT forward) | `ROUTE` | `escalate_phishing_alert()` |
| **WFH Equipment** | KB-10 (>3 days WFH, Manager + Finance) | `ROUTE` | `route_to_finance_and_manager()` |
| **Ambiguous Request** | Baseline Security Protocol | `CLARIFY` | `request_employee_clarification()` |
