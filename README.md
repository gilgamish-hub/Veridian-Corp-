# 🛡️ Veridian Corp — Internal IT Support Agent

An enterprise-grade, **Deterministic-First Hybrid Control Pipeline** built for the Veridian Corp Internal IT Support Agent under the **Antigravity Agent Framework**.

---

## 🌟 Architectural Overview

The agent handles internal IT support requests using a 5-Node Control Pipeline to ensure **100% policy compliance** and zero hallucination:

1. **Node 1 — Intent & Entity Parser**: Parses intent categories (`HARDWARE`, `ACCESS`, `SOFTWARE`, `SECURITY`) and extracts key entities (laptop age, failure severity, mailbox size, asset tags).
2. **Node 2 — Grounded Context & Precedent Retrieval**: Queries Knowledge Base rules (`KB-01` to `KB-10`) and retrieves historical ticket precedents (`TK-1042` to `TK-1051`).
3. **Node 3 — Policy Decision Engine**: Evaluates strict business logic deterministically across outcomes (`APPROVED`, `RESOLVE`, `ROUTE`, `CLARIFY`, `UNALLOWABLE`).
4. **Node 4 — Action Execution Hooks**: Dispatches executable action tools (`unlock_user_account`, `renew_vpn_credentials`, `dispatch_replacement_laptop`, `send_security_alert`, `restart_spooler_and_dispatch`).
5. **Node 5 — Response Generation**: Formulates clear, empathetic, policy-grounded user responses citing KB rules and ticket precedents.

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/gilgamish-hub/Veridian-Corp-.git
cd Veridian-Corp-
pip install -r requirements.txt
```

### 2. Run Interactive Web Dashboard
Launch the Streamlit dashboard:
```bash
streamlit run src/app.py
```

### 3. Run Automated Unit Tests
Execute the 17-test verification suite:
```bash
pytest tests/test_agent.py
```

---

## 📊 Evaluation & Benchmarking

The Streamlit UI includes a **Batch Evaluation Benchmark** tab that executes all 15 grounded test cases deterministically in 1 click, yielding a **100% Policy Compliance Accuracy** scorecard with JSON/CSV audit log export.

---

## 📁 Repository Structure

```text
├── data/
│   └── data_pack.json         # Knowledge Base, Requests, & Historical Precedents
├── src/
│   ├── app.py                 # Streamlit Web Application Dashboard
│   ├── engine.py              # 5-Node Deterministic Control Pipeline Engine
│   ├── schemas.py             # Pydantic State Schemas
│   └── tools.py               # Executable Action Hooks & Export Utilities
├── tests/
│   └── test_agent.py          # Pytest Automated Verification Suite
├── requirements.txt           # Project Dependencies
├── README.md                  # Project Documentation
└── PROJECT_EXPLAINED_SIMPLE.md # Non-Technical Project Guide
```
