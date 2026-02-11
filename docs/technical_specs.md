# Technical Specifications - Nu-Live-Agent

## Architecture Overview
The system follows a modular agentic architecture using Google's GenAI tools.

### Directory Structure (`app/banking`)
-   `journeys/`: Contains the logic for each specific journey.
    -   `fraud/`: `dispute_manager.py`, `risk_engine.py`
    -   `debt/`: `negotiation_engine.py`, `payment_planner.py`
    -   `security/`: `block_manager.py`, `identity_verifier.py`
    -   `wow/`: `gift_manager.py`, `sentiment_analyzer.py`
-   `core/`: Shared components.
    -   `customer.py`: Customer profile mock.
    -   `ledger.py`: Transaction history mock.
    -   `session.py`: Session state management.

## Data Models (Mock)

### Customer
```python
@dataclass
class Customer:
    id: str
    name: str
    risk_profile: str  # low, medium, high
    ltv_segment: str   # gold, platinum, uv
    pet_name: Optional[str] = None
```

### Transaction
```python
@dataclass
class Transaction:
    id: str
    amount: float
    merchant: str
    timestamp: datetime
    status: str  # approved, declined, pending
    is_suspicious: bool
```

## Tool Interfaces

### Fraud Tools
-   `analyze_transaction(tx_id) -> RiskScore`
-   `initiate_dispute(tx_id, reason) -> DisputeTicket`
-   `apply_trust_credit(tx_id) -> bool`

### Debt Tools
-   `get_overdue_bills(cust_id) -> List[Bill]`
-   `simulate_negotiation(bill_id, down_payment, installments) -> Proposal`

## Integration with Gemini
-   The "Xpeer" persona will be injected via the System Instruction.
-   Tools will be function-called by the model based on user intent.
-   State will be maintained in-memory for the session (simulating backend).
