# Antigravity Implementation Guide & Workflow
**Project:** Veridian Corp Internal IT Support Agent  

Follow this step-by-step guide to implement and run this agent in the **Antigravity** environment.

---

## Phase 1: Environment Setup & Project Initialization

### Step 1: Initialize Project Directory
Run the following commands in your terminal:
```bash
mkdir veridian-it-agent
cd veridian-it-agent
mkdir -p data src tests
```

### Step 2: Define Dependencies (`requirements.txt`)
Create a `requirements.txt` file with the following packages:
```text
antigravity-sdk>=0.4.0
pydantic>=2.0
python-dotenv>=1.0.0
streamlit>=1.28.0
pytest>=7.4.0
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

---

## Phase 2: Data Grounding Layer

### Step 3: Implement Grounded Data Store (`data/data_pack.json`)
Store the Knowledge Base, Policy rules, Requests, and Historical Tickets in a structured JSON file under `data/data_pack.json`.

---

## Phase 3: Building the Antigravity Agent Workflow

### Step 4: Define Tools (`src/tools.py`)
Implement Python functions for agent actions:
- `unlock_user_account(user_email)`
- `renew_vpn_credentials(user_email)`
- `route_ticket(ticket_id, target_department, justification)`
- `send_security_alert(user_email, details)`

### Step 5: Implement Agent Workflow (`src/agent.py`)
Build the core Antigravity graph:
1. **Input State Node**: Ingests `request_id`.
2. **Context Retrieval Node**: Loads request details + matches KB policies.
3. **Decision Node**: Evaluates conditions deterministically.
4. **Action Node**: Executes tools or outputs routing parameters.

---

## Phase 4: User Interface & Evaluation

### Step 6: Create Interactive Testing Interface (`src/main.py`)
Build a Streamlit app to test all 15 requests interactively and visualize the decision trace, matched KB rules, and execution outcomes.

Run the app locally with:
```bash
streamlit run src/main.py
```
