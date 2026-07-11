# AgentPulse

**AgentPulse** is an explainable AI-powered liquidity forecasting, anomaly detection, and alert coordination platform for multi-provider mobile financial service agents.

It helps operations teams monitor shared physical cash and provider-specific balances, identify possible liquidity shortages, detect unusual transaction activity, and coordinate a human-controlled response through one dashboard.

> **Hackathon prototype:** AgentPulse uses synthetic or simulated data. It does not connect to real financial accounts, transfer money, freeze funds, block users, or declare fraud.

---

## Problem Statement

Mobile financial service agents may serve several providers, such as **bKash, Nagad, Rocket, Upay, and SureCash**, from the same outlet.

The outlet uses:

- one shared physical cash reserve,
- separate electronic balances for each provider,
- many cash-in and cash-out transactions, and
- different operational teams responsible for reviewing problems.

This creates several challenges:

- A provider balance may run low even when the outlet appears healthy overall.
- Operations teams may not know which provider is under the greatest pressure.
- Unusual transaction patterns may be missed or reviewed too late.
- Alerts may lack evidence, ownership, or a clear resolution history.
- Missing, delayed, or conflicting data may lead to unreliable decisions.

---

## Proposed Solution

AgentPulse brings liquidity monitoring, forecasting, anomaly review, explainable alerts, and case coordination into one Django-based web application.

The platform helps users answer five important questions:

1. Which provider is currently under the greatest liquidity pressure?
2. When could a shortage occur?
3. Why was an alert generated?
4. Who is responsible for reviewing it?
5. What safe human action should happen next?

---

## Main Features

### Unified operational dashboard

- Shared physical cash overview
- Provider-specific electronic balances
- Active alert summary
- Liquidity risk indicators
- Data-quality status
- Workflow and performance metrics

### Liquidity forecasting

- Forecasts provider balance over a selected time window
- Estimates predicted demand and projected balance
- Calculates shortage probability and confidence
- Estimates when the balance may fall below its safety threshold
- Adjusts confidence according to data quality

### Anomaly detection and review

- Unusually large transactions
- Transaction velocity spikes
- Repeated or similar transaction amounts
- Synthetic anomaly injection for evaluation
- Human review rather than automatic fraud accusation

### Explainable alert workflow

- Alert title, type, severity, and confidence
- Supporting evidence
- Recommended human-controlled action
- Assignment and ownership information
- Status updates and review notes
- Full alert history and timeline
- AI-assisted alert Q&A

### Workflow metrics

- Forecast accuracy indicators
- Shortage warning lead time
- Anomaly precision and recall
- False-positive rate
- Explanation coverage
- Alert ownership and response indicators
- System latency measurements

### Account and interface features

- Authentication and registration
- Password reset and OTP workflow
- User profile and settings
- Responsive dashboard interface
- Agent, transaction, alert, forecast, anomaly, metric, and data-quality pages

---

## Intended Users

### Operations Officer

Monitors agents, provider balances, forecasts, alerts, assignment, escalation, and resolution.

### Field or Territory Officer

Reviews assigned agents, contacts outlets, records operational action, and escalates unresolved issues.

### Risk or Compliance Reviewer

Examines unusual activity, supporting evidence, uncertainty, and possible false positives.

### Management User

Views read-only summaries, area-level risk, response performance, and validation metrics.

### Agent or Outlet User

Views the outlet's balances, transactions, alerts, and recommended next steps.

---

## System Workflow

```text
Synthetic transaction data enters the system
                    ↓
Balances and recent activity are analysed
                    ↓
Liquidity forecast is generated
                    ↓
Anomaly checks evaluate unusual patterns
                    ↓
Probability, confidence, and evidence are calculated
                    ↓
The shared alert service creates or updates an alert
                    ↓
A responsible user reviews and acknowledges the case
                    ↓
The user adds notes, escalates, resolves, or marks a false positive
                    ↓
The complete history remains available for audit and evaluation
```

---

## AI and Analytics Implementation

AgentPulse uses a two-layer approach.

### 1. Deterministic analytics layer

The Django backend calculates:

- current balance,
- recent cash-in and cash-out,
- net depletion rate,
- predicted demand,
- projected balance,
- safety-threshold risk,
- shortage probability,
- estimated shortage time,
- anomaly evidence, and
- data-quality confidence.

This keeps the core decision logic measurable and testable.

### 2. Explainable AI layer

The AI assistant converts structured alert evidence into a clear explanation and supports questions such as:

- Why was this alert created?
- Which evidence is most important?
- Is this confirmed fraud?
- What should the operations officer do next?
- Could this be a false positive?

The assistant must use only the supplied alert context, state uncertainty clearly, and recommend human verification.

---

## Responsible AI and Safety

AgentPulse follows these safety boundaries:

- Uses synthetic or anonymised data only
- Does not request customer PINs, OTPs, passwords, or private keys
- Keeps provider balances logically separate
- Does not automatically transfer funds
- Does not freeze or block customer accounts
- Does not declare that fraud has occurred
- Describes suspicious patterns as **unusual activity requiring human review**
- Shows evidence, confidence, uncertainty, and possible false-positive explanations
- Records assignment, acknowledgement, escalation, notes, and resolution history

---

## Technology Stack

- **Backend:** Python, Django
- **API support:** Django REST Framework
- **Database:** SQLite for the hackathon prototype
- **Frontend:** Django Templates, HTML, CSS, JavaScript
- **Analytics:** Python-based forecasting and anomaly logic
- **Authentication:** Django authentication system
- **Version control:** Git and GitHub

---

## Project Structure

```text
SUST_Hackathon/
├── accounts/       # Authentication, profiles, settings, OTP workflows
├── agents/         # Agents, areas, providers, and provider balances
├── ai_core/        # AI and decision-support logic
├── alerts/         # Alert models, services, evidence, history, and views
├── analytics/      # Forecasts, anomaly detection, metrics, data quality
├── config/         # Django project settings and root URLs
├── dashboard/      # Main operational dashboard
├── static/         # CSS and JavaScript
├── templates/      # Django HTML templates
├── transactions/   # Transactions and demo-data generation
├── manage.py
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/MuradAhmedTahmim/SUST_Hackathon.git
cd SUST_Hackathon
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS or Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install "Django>=6.0,<6.1" djangorestframework
```

A `requirements.txt` file should be generated before final submission:

```bash
pip freeze > requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Create an administrator account

```bash
python manage.py createsuperuser
```

### 6. Load realistic seed data

```bash
python manage.py seed_data
```

For the smaller synthetic transaction demonstration:

```bash
python manage.py generate_demo_data
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Django administration is available at:

```text
http://127.0.0.1:8000/admin/
```

---

## Main Application Pages

After signing in, the application provides access to:

- Dashboard overview
- Agent list and agent details
- Transactions
- Alerts and alert details
- Liquidity forecasts
- Anomaly review
- Metrics dashboard
- Data-quality dashboard
- Profile and settings

---

## Running Tests

Run the complete test suite:

```bash
python manage.py test
```

Run only the alert workflow tests:

```bash
python manage.py test alerts
```

Current workflow verification reported:

```text
9 alert tests run
2 transaction workflow tests run
0 failures
0 errors
```

Recommended additional tests include:

- Duplicate active-alert prevention
- Resolved alert followed by a new valid alert
- Probability normalization for both 0–1 and 0–100 values
- Alert status update and history creation
- Missing, delayed, and conflicting provider data
- Invalid status transitions
- Unauthorized alert updates
- AI-service failure and fallback explanation

---

## Suggested Live Demo

A strong presentation can follow this sequence:

1. Open the dashboard and show one outlet with shared cash and separate bKash, Nagad, and Rocket balances.
2. Generate or display recent transactions.
3. Show that Nagad cash-out demand is increasing.
4. Run a liquidity forecast.
5. Display the predicted shortage time, probability, and confidence.
6. Show an automatically generated liquidity alert.
7. Open the alert detail page and explain its evidence.
8. Ask the AI assistant why the alert was generated.
9. Assign and acknowledge the alert.
10. Add a review note and change its status.
11. Show the timeline history and updated workflow metrics.
12. Explain that the recommendation is advisory and requires human approval.

---

## Example Decision Output

```text
Provider: Nagad
Current balance: ৳18,000
Safety threshold: ৳10,000
Projected balance: ৳7,000
Estimated shortage time: 75 minutes
Shortage probability: 84%
Forecast confidence: 82%

Explanation:
Recent cash-out activity is higher than the normal level. Based on the
current depletion rate, the Nagad balance may fall below its configured
safety threshold within approximately 75 minutes.

Recommended action:
Verify the latest provider balance and contact the assigned field officer
to arrange approved liquidity support. This output is advisory and requires
human review.
```

---

## Data and Evaluation

The project uses synthetic records representing:

- provider balances,
- physical cash,
- cash-in and cash-out activity,
- normal transactions,
- injected anomalies,
- delayed or conflicting data,
- alerts, evidence, and workflow history.

Evaluation should be based on measured outputs rather than invented values. Useful metrics include:

- Forecast mean absolute error
- Average shortage warning lead time
- Anomaly precision
- Anomaly recall
- False-positive rate
- Average analysis latency
- Average acknowledgement time
- Average resolution time
- Percentage of alerts with complete explanations

---

## Current Implementation Status

- Connected forecast-to-alert workflow
- Shared alert creation service
- Probability normalization supporting 0–1 and legacy 0–100 values
- Duplicate active-alert handling
- Interactive alert status review
- History entry creation for alert updates
- Assignment information and evidence display
- Alert timeline history
- AI Q&A on alert details
- Workflow-level metrics
- Alert regression tests passing
- Admin support for users, groups, permissions, and profiles

---

## Project Documents

- [Architecture](ARCHITECTURE.md)
- [Data and Simulation](DATA_AND_SIMULATION.md)
- [Validation](VALIDATION.md)
- [Responsible AI](RESPONSIBLE_AI.md)
- [Limitations](LIMITATIONS.md)

---

## Limitations

- The project currently uses SQLite and is designed as a hackathon prototype.
- Provider data is synthetic and not connected to live provider APIs.
- Forecasting quality depends on the amount and freshness of transaction data.
- Anomaly detection identifies unusual patterns but cannot prove fraud.
- AI explanations depend on the quality of the structured evidence supplied to them.
- Production deployment requires stronger permission controls, secret management, monitoring, and database configuration.

---

## Production Security Checklist

Before deployment:

- Move `SECRET_KEY`, email credentials, and other secrets to environment variables.
- Remove all hardcoded passwords and app credentials from source control.
- Rotate any credential that has previously been committed.
- Set `DEBUG = False`.
- Configure `ALLOWED_HOSTS`.
- Use HTTPS and secure cookies.
- Use PostgreSQL or another production-ready database.
- Add role-based authorization and object-level permission checks.
- Configure static-file hosting and logging.
- Run Django's deployment check:

```bash
python manage.py check --deploy
```

---

## Future Improvements

- Role-based dashboards and object-level permissions
- Bengali and English AI explanations
- Context-aware false-positive analysis
- Real-time browser or email notifications
- Stronger transaction velocity and repeated-amount detection
- Automated evaluation against labelled synthetic scenarios
- Map-based agent risk view
- PostgreSQL deployment
- Provider API adapters using safe simulated interfaces
- Scheduled forecasting and alert generation

---

## Repository

GitHub: `MuradAhmedTahmim/SUST_Hackathon`

---

## Team

Add the names, roles, institution, and contact information of the hackathon team here.

Example:

```text
Team Name: [NEUB_hack]
Institution: North East University Bangladesh 

Members:
- [Joyashis Das] — Backend and analytics
- [Murad Ahmed Tahmim] — Frontend and UX
- [Khayrul Islam] — AI, testing, and presentation
```

---

## License

No license has been added yet. Add an appropriate open-source license before public reuse or distribution.