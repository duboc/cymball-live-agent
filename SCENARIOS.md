# Scenario Design Guide

This guide explains how to design customer journeys and test scenarios for your banking agent. Use this as a companion to [CUSTOMIZATION.md](CUSTOMIZATION.md).

## Table of Contents

1. [Scenario Design Philosophy](#scenario-design-philosophy)
2. [Anatomy of a Customer Journey](#anatomy-of-a-customer-journey)
3. [Creating Customer Profiles](#creating-customer-profiles)
4. [Designing Transactions](#designing-transactions)
5. [Writing Conversation Examples](#writing-conversation-examples)
6. [Implementing Tools](#implementing-tools)
7. [Example Journeys](#example-journeys)
8. [Agent Personality Guide](#agent-personality-guide)
9. [Testing Scenarios](#testing-scenarios)

---

## Scenario Design Philosophy

### Core Principles

| Principle | Description |
|-----------|-------------|
| **Empathy First** | Validate feelings before solving problems |
| **No Scripts** | Natural conversation, not robotic responses |
| **Transparency** | Explain processes clearly |
| **Proactive Investigation** | Resolve before escalating |
| **Error Tolerance** | Never judge the customer |
| **Personalized Closings** | Reference conversation context |

### Traditional vs. Modern Approach

| Aspect | Traditional Bank | Modern Approach |
|--------|------------------|-----------------|
| Greeting | "Dear Sir/Madam..." | Use customer's name |
| Focus | Policy enforcement | Problem solving |
| Tone | Formal, distant | Friendly, professional |
| Errors | Customer blamed | "This happens often!" |
| Flexibility | Fixed menu options | Agent has authority |
| Goal | Complete transaction | Build relationship |

---

## Anatomy of a Customer Journey

Each journey follows this flow:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. TRIGGER     │───►│  2. EMOTION     │───►│  3. ANALYSIS    │
│  What happened? │    │  How do they    │    │  Agent gathers  │
│                 │    │  feel?          │    │  information    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
         ┌────────────────────────────────────────────┘
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  4. ACTION      │───►│  5. RESOLUTION  │───►│  6. FOLLOW-UP   │
│  Use tools to   │    │  Solve the      │    │  Anything else? │
│  help           │    │  problem        │    │  Education      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Journey Components

1. **Trigger**: What initiated the customer contact
2. **Emotion**: Customer's emotional state (frustrated, worried, confused)
3. **Analysis**: Information gathering using tools
4. **Action**: Steps taken to resolve
5. **Resolution**: Problem solved + explanation
6. **Follow-up**: Additional help, tips, personalized closing

---

## Creating Customer Profiles

### Profile Template

```python
"customer_id_001": {
    # Basic Information
    "nombre": "Customer Name",
    "tiempo_cliente": "2 years and 3 months",
    "dni": "12345678A",
    "dni_ultimos_digitos": "78A",
    "email": "customer.n***@email.com",  # Partially masked
    "telefono": "+1 555 *** 1234",        # Partially masked

    # Customer Profile
    "perfil": "good_payer",  # good_payer, new_customer, premium, at_risk

    # Card Information
    "tarjeta_terminacion": "4501",
    "tipo_tarjeta": "Visa Gold",
    "limite_credito": 5000.00,
    "limite_usado": 1200.00,
    "tarjeta_status": "active",  # active, blocked, blocked_travel

    # Scenario-Specific Fields
    "dias_mora": 0,              # Days overdue (for collections)
    "pago_minimo": 0.00,         # Minimum payment due
    "puntos_programa": 2350,     # Loyalty points (for benefits)
    "aviso_viaje": False,        # Travel notice (for security)

    # Context
    "ultima_interaccion": "2026-01-20"
}
```

### Profile Types by Journey

| Journey | Profile Characteristics |
|---------|------------------------|
| Collections | `dias_mora > 0`, `pago_minimo > 0`, good payment history |
| Benefits | `puntos_programa > 0`, premium card, active promotions |
| Security | `tarjeta_status: "blocked"`, travel context |
| Disputes | Recent suspicious transaction, good customer history |

---

## Designing Transactions

### Transaction Template

```python
"txn_customer_001": {
    "cliente_id": "customer_id_001",
    "valor": 85.00,
    "nombre_comercio": "Store Name",
    "categoria": "restaurant",  # restaurant, supermarket, online, travel
    "fecha": "2026-01-18T16:30:00",
    "tipo": "presencial",  # presencial, online
    "status": "approved",  # approved, declined, disputed

    # Optional fields for specific scenarios
    "pais": "Portugal",           # For travel scenarios
    "motivo_rechazo": "no_travel_notice",  # For declined transactions
    "cargo_no_reconocido": True,  # For dispute scenarios
    "puntos_generados": 85,       # For benefits scenarios
    "pago_aplazado": True,        # For deferred payment
    "cuotas": 6                   # Number of installments
}
```

### Transaction Patterns by Journey

| Journey | Transaction Characteristics |
|---------|----------------------------|
| Collections | Regular transactions, nothing suspicious |
| Benefits | Mix of regular and deferred payments |
| Security | Transaction in foreign country, `status: "declined"` |
| Disputes | `cargo_no_reconocido: True`, unusual merchant |

---

## Writing Conversation Examples

### Conversation Structure

```
[CUSTOMER] - Initial contact (often emotional)
[AGENT] - Greeting + empathy + reassurance
[CUSTOMER] - More details
[AGENT] - Uses tool to investigate
[AGENT] - Explains findings
[CUSTOMER] - Response/questions
[AGENT] - Resolution + education
[AGENT] - Personalized closing
```

### Emotional States and Responses

| Customer Emotion | Agent Response Strategy |
|------------------|------------------------|
| Panicked | "I can imagine the scare!" + immediate reassurance |
| Frustrated | "I'm sorry for this headache" + fast action |
| Confused | Clear explanation, no jargon |
| Embarrassed | "This happens all the time!" + normalize |
| Angry | Acknowledge, don't defend, solve fast |

### Key Phrases by Situation

| Situation | Phrase |
|-----------|--------|
| Fear | "I can imagine how scary that was!" |
| Frustration | "I'm so sorry about this inconvenience" |
| Reassurance | "No one is going to lose money here, okay?" |
| Customer Error | "This happens a lot, don't worry!" |
| Security Block | "We prefer to be cautious to protect your money" |
| Empathy | "Can I ask what happened?" |
| Closing | Reference something personal from the conversation |

---

## Implementing Tools

### Tool Template

```python
def my_tool(cliente_id: str, other_param: str):
    """
    Clear description of what this tool does.

    Args:
        cliente_id: Customer ID (e.g., "roberto_garcia_001").
        other_param: Description of parameter.

    Returns:
        Dictionary with results.
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Customer not found."}

    # Tool logic here

    return {
        "success": True,
        "message": "Action completed.",
        "details": {...}
    }

my_tool_func = Tool(my_tool)
```

### Tools by Journey Type

#### General Tools
| Tool | Purpose |
|------|---------|
| `identificar_cliente` | Find customer by name or ID |
| `consultar_historial_cliente` | Get full customer profile |

#### Collections Journey
| Tool | Purpose |
|------|---------|
| `consultar_mora` | Check overdue status |
| `registrar_pago_prometido` | Log payment commitment |

#### Benefits Journey
| Tool | Purpose |
|------|---------|
| `consultar_beneficios_tarjeta` | Card benefits |
| `consultar_puntos` | Points balance |
| `consultar_disponible` | Available credit |

#### Security Journey
| Tool | Purpose |
|------|---------|
| `validar_identidad` | Verify customer identity |
| `autorizar_transaccion` | Approve declined transaction |
| `registrar_aviso_viaje` | Register travel notice |

#### Dispute Journey
| Tool | Purpose |
|------|---------|
| `buscar_transacciones_recientes` | List recent transactions |
| `bloquear_tarjeta` | Block card preventively |
| `registrar_reclamacion` | Create dispute case |
| `solicitar_reposicion` | Request card replacement |

---

## Example Journeys

### Journey 1: Collections (Early Delinquency)

**Trigger**: Customer's minimum payment is 5 days overdue

**Customer Profile**:
```python
{
    "nombre": "Roberto Garcia",
    "perfil": "good_payer",
    "dias_mora": 5,
    "pago_minimo": 150.00,
    "tiempo_cliente": "3 years"
}
```

**Conversation Flow**:
```
[CUSTOMER]: "Hi, I know I'm late on my payment..."

[AGENT]: "Hi Roberto! I can see your payment. Before we discuss options,
can I ask - did something unexpected happen this month?"

[TOOL]: consultar_mora(cliente_id="roberto_garcia_001")

[AGENT]: "I see you've been with us 3 years with no issues.
The minimum is $150. Would you like to pay via app,
online banking, or at a branch?"

[CUSTOMER]: "I can pay Friday via app."

[TOOL]: registrar_pago_prometido(cliente_id="...", monto=150, fecha="Friday")

[AGENT]: "Perfect! I've noted that. You'll get a reminder Thursday.
Anything else I can help with?"
```

**Key Techniques**:
- Ask "what happened" instead of "when will you pay"
- Acknowledge good history
- Offer options, don't demand
- Confirm and set expectations

---

### Journey 2: Benefits Inquiry

**Trigger**: Customer asks about card benefits

**Customer Profile**:
```python
{
    "nombre": "Carolina Martinez",
    "tipo_tarjeta": "Visa Premium",
    "puntos_programa": 2350,
    "promociones_activas": ["Deferred Payment - Store A", "Store B"]
}
```

**Conversation Flow**:
```
[CUSTOMER]: "I want to know about deferred payments and points"

[TOOL]: consultar_beneficios_tarjeta(cliente_id="carolina_martinez_002")

[AGENT]: "Great question! Your Visa Premium has:
- Deferred Payment at Store A, B, C (3, 6, or 12 months)
- 1 point per dollar on regular purchases

Important: Deferred purchases don't earn points
(the benefit is the interest-free financing).
Regular purchases do earn 1 point per dollar."

[TOOL]: consultar_puntos(cliente_id="...")

[AGENT]: "You currently have 2,350 points.
500 expire June 30th. Want tips on using them?"
```

**Key Techniques**:
- Proactively clarify common confusion (points on deferred)
- Mention expiring points
- Offer additional value

---

### Journey 3: Security / Travel Block

**Trigger**: Card declined abroad

**Customer Profile**:
```python
{
    "nombre": "Javier Fernandez",
    "tarjeta_status": "blocked_travel",
    "pais_actual": "Portugal",
    "aviso_viaje": False
}
```

**Transaction**:
```python
{
    "valor": 400.00,
    "nombre_comercio": "Hotel Pestana Lisboa",
    "status": "declined",
    "motivo_rechazo": "no_travel_notice"
}
```

**Conversation Flow**:
```
[CUSTOMER]: "MY CARD WAS DECLINED AT THE HOTEL!!"

[AGENT]: "Javier, I understand and I'm solving this RIGHT NOW.
Quick security check - last 4 digits of your ID and hotel name?"

[CUSTOMER]: "1234. Hotel Pestana."

[TOOL]: validar_identidad(cliente_id="...", metodo="datos_confirmativos")
[TOOL]: registrar_aviso_viaje(cliente_id="...", pais="Portugal", fecha_regreso="...")

[AGENT]: "Done! Card unblocked. You can try again in 2 minutes.
The block happened because there was no travel notice -
we prefer to be cautious than let fraud through.
Want me to also enable your debit card for Portugal?"
```

**Key Techniques**:
- Speed is critical - solve first, explain after
- Reframe: "cautious" not "blocked you"
- Offer additional help (debit card)

---

### Journey 4: Dispute / Fraud

**Trigger**: Unrecognized charge

**Customer Profile**:
```python
{
    "nombre": "Maria Elena Lopez",
    "perfil": "good_payer"
}
```

**Transaction**:
```python
{
    "valor": 85.00,
    "nombre_comercio": "Netflix",  # But customer only pays $15/month
    "cargo_no_reconocido": True
}
```

**Conversation Flow**:
```
[CUSTOMER]: "There's a Netflix charge for $85 but I only pay $15!"

[AGENT]: "Let's investigate this immediately to protect your money."

[TOOL]: buscar_transacciones_recientes(cliente_id="...")

[AGENT]: "I see two Netflix charges - your regular $15 on the 5th,
and this $85 on the 29th at 3:15 AM.
That time is suspicious. I recommend:
1. Block the card preventively
2. Open a dispute case
The $85 won't be charged while we investigate."

[TOOL]: bloquear_tarjeta(cliente_id="...", motivo="Unrecognized charge")
[TOOL]: registrar_reclamacion(cliente_id="...", transaccion_id="...")

[AGENT]: "Done! Case #8892 opened. Resolution in 30-45 business days.
New card arrives in 3-5 days. To your home or office?"

[TOOL]: solicitar_reposicion(cliente_id="...", destino="home")
```

**Key Techniques**:
- "Protect your money" messaging
- Explain what happens during dispute
- Proactively offer card replacement
- Give case number for reference

---

## Agent Personality Guide

### Do's

- Use customer's name
- Validate emotions first
- Personalize closings (reference conversation)
- Explain the "why"
- Normalize customer mistakes
- Be proactive in investigation
- Teach app features

### Don'ts

- Use formal titles (Sir/Madam)
- Say "it's bank policy"
- Use technical jargon
- Transfer without trying to solve
- Judge financial decisions
- Be impersonal
- Follow rigid scripts

---

## Testing Scenarios

### Test Checklist

For each journey, verify:

- [ ] Agent greets by name
- [ ] Empathy shown before problem-solving
- [ ] Correct tools called
- [ ] Clear explanation given
- [ ] Resolution confirmed
- [ ] Follow-up offered
- [ ] Personalized closing

### Sample Test Prompts

| Journey | Test Prompt |
|---------|-------------|
| Collections | "Hi, I'm Roberto Garcia, I think I'm late on my payment" |
| Benefits | "I'm Carolina Martinez, how do points and deferred payments work?" |
| Security | "I'm Javier Fernandez and my card was just declined in Portugal!" |
| Dispute | "I'm Maria Elena Lopez and I see a charge I don't recognize" |

### Metrics to Track

| Metric | Description | Target |
|--------|-------------|--------|
| CSAT | Customer satisfaction | > 4.5/5 |
| FCR | First contact resolution | > 85% |
| AHT | Average handle time | < 5 min |
| Tool Success | Tools called correctly | > 95% |

---

## Quick Reference Card

### Creating a New Journey

1. **Define the trigger** - What brings the customer to call?
2. **Create a customer profile** - Add to `mock_data.py`
3. **Create relevant transactions** - Add to `TRANSACCIONES`
4. **Identify needed tools** - What actions can the agent take?
5. **Write conversation example** - Document expected flow
6. **Add to prompts** - Update `prompts.py` with scenario
7. **Add to config** - Add scenario to `SCENARIOS` in `config.py`
8. **Test** - Run through the conversation

### Files to Modify

| File | What to Add |
|------|-------------|
| `config.py` | Scenario name in `SCENARIOS` |
| `mock_data.py` | Customer profile and transactions |
| `tools.py` | New tools if needed |
| `prompts.py` | Scenario playbook in system prompt |
