# Bank Agent Template - Customization Guide

This document explains how to customize this banking agent template for a new bank, language, or region.

**Related documentation:**
- [SCENARIOS.md](SCENARIOS.md) - Guide for designing customer journeys and test scenarios
- [README.md](README.md) - Project overview and quick start

## Quick Start

To customize this template for a new bank, you only need to edit **one file**:

```
app/config.py
```

All bank-specific values (name, colors, language, agent persona, etc.) are centralized in this file.

---

## Table of Contents

1. [Configuration File Overview](#configuration-file-overview)
2. [Basic Customization](#basic-customization)
3. [Language Support](#language-support)
4. [Brand Colors](#brand-colors)
5. [Agent Persona](#agent-persona)
6. [Card Types & Benefits](#card-types--benefits)
7. [Customer Scenarios](#customer-scenarios)
8. [Mock Data](#mock-data)
9. [Advanced Customization](#advanced-customization)
10. [Testing Your Changes](#testing-your-changes)

---

## Configuration File Overview

The `app/config.py` file is organized into sections:

```python
# =============================================================================
# BANK IDENTITY
# =============================================================================
BANK_NAME = "Cymball Bank"
BANK_COUNTRY = "España"
BANK_LANGUAGE = "es"  # es, en, pt
BANK_CURRENCY = "EUR"
BANK_CURRENCY_SYMBOL = "€"

# =============================================================================
# AGENT PERSONA
# =============================================================================
AGENT_NAME = "Laura"
AGENT_VOICE = "Leda"

# =============================================================================
# BRAND COLORS
# =============================================================================
BRAND_COLORS = {
    "primary": "#0066CC",
    ...
}
```

---

## Basic Customization

### Step 1: Change Bank Identity

Edit these values in `app/config.py`:

```python
BANK_NAME = "Your Bank Name"
BANK_COUNTRY = "Your Country"
BANK_LANGUAGE = "en"  # or "es", "pt"
BANK_CURRENCY = "USD"  # or "EUR", "BRL", etc.
BANK_CURRENCY_SYMBOL = "$"  # or "€", "R$", etc.
BANK_ID_DOCUMENT = "ID Card"  # or "DNI", "CPF", etc.
```

### Step 2: Change Agent Persona

```python
AGENT_NAME = "Sarah"  # The agent's name
AGENT_VOICE = "Kore"  # Gemini voice (see Voice Options below)
```

### Step 3: Change Brand Colors

```python
BRAND_COLORS = {
    "primary": "#FF0000",       # Your brand's primary color
    "primary_dark": "#CC0000",  # Darker shade
    "primary_light": "#FF6666", # Lighter shade
    "success": "#00A86B",
    "warning": "#FFB800",
    "error": "#FF4444",
    "text": "#191919",
}
```

### Step 4: Restart the Application

```bash
python -m uvicorn app.main:app --reload
```

---

## Language Support

The template supports three languages out of the box:

| Code | Language | Example Region |
|------|----------|----------------|
| `es` | Spanish  | Spain, Latin America |
| `en` | English  | USA, UK, Australia |
| `pt` | Portuguese | Brazil, Portugal |

To change the language:

```python
BANK_LANGUAGE = "en"  # Change to your language
```

The agent's system prompt automatically adapts to the selected language, including:
- Greeting phrases
- Courtesy expressions
- Empathy statements
- Farewell messages

### Adding a New Language

To add a new language, edit `app/agent/tools/prompts.py`:

1. Add expressions in `_get_language_expressions()`:

```python
"fr": {
    "greeting_time": "Bonjour",
    "affirmative": ["d'accord", "bien sûr", "pas de problème"],
    ...
}
```

2. Add a new prompt block in `build_system_instruction()`:

```python
elif BANK_LANGUAGE == "fr":
    return f"""
Vous êtes un agent de service client de {BANK_NAME}...
"""
```

---

## Brand Colors

The frontend automatically loads colors from the `/api/config` endpoint. Colors are applied using CSS variables:

| Variable | Used For |
|----------|----------|
| `--bank-primary` | Main brand color (buttons, headers) |
| `--bank-primary-dark` | Darker shade (hover states) |
| `--bank-primary-light` | Lighter shade (highlights) |
| `--bank-success` | Success messages, positive states |
| `--bank-warning` | Warning messages |
| `--bank-error` | Error messages, negative states |

---

## Agent Persona

### Voice Options

Available Gemini Live voices:

| Voice | Best For |
|-------|----------|
| `Leda` | Spanish, warm female voice |
| `Kore` | English, professional female voice |
| `Aoede` | Neutral, clear articulation |
| `Puck` | English, friendly male voice |
| `Charon` | Deep, authoritative voice |
| `Fenrir` | Energetic, youthful voice |
| `Orus` | Calm, reassuring voice |
| `Zephyr` | Light, approachable voice |

### Agent Description

The agent description appears in logs and debugging:

```python
AGENT_DESCRIPTION = f"Customer Service Agent - {BANK_NAME}, {BANK_COUNTRY}"
```

---

## Card Types & Benefits

Define your bank's card products in `app/config.py`:

```python
CARD_TYPES = {
    "visa_classic": {
        "nombre": "Visa Classic",
        "puntos_por_euro": 0,
        "pago_aplazado": True,
        "comercios_pago_aplazado": ["Store A", "Store B"],
        "plazos_pago_aplazado": [3, 6, 12],
        "seguro_viaje": False,
    },
    "visa_gold": {
        "nombre": "Visa Gold",
        "puntos_por_euro": 1.5,
        ...
    }
}
```

---

## Customer Scenarios

Define test scenarios for the demo:

```python
SCENARIOS = {
    "customer_001": {
        "name": "Collections (Early Delinquency)",
        "description": "Customer with overdue payment"
    },
    "customer_002": {
        "name": "Benefits Inquiry",
        "description": "Customer asking about card benefits"
    },
}
```

---

## Mock Data

Customer and transaction data is stored in `app/agent/data/mock_data.py`.

### Adding a New Customer

```python
CLIENTES = {
    "john_doe_001": {
        "nombre": "John Doe",
        "tiempo_cliente": "2 years",
        "dni": "123456789",
        "dni_ultimos_digitos": "789",
        "email": "john.d***@email.com",
        "telefono": "+1 555 *** 1234",
        "perfil": "good_payer",
        "tarjeta_terminacion": "4501",
        "tipo_tarjeta": "Visa Gold",
        "limite_credito": 5000.00,
        "limite_usado": 1200.00,
        ...
    }
}
```

### Adding Transactions

```python
TRANSACCIONES = {
    "txn_john_001": {
        "cliente_id": "john_doe_001",
        "valor": 85.00,
        "nombre_comercio": "Amazon",
        "categoria": "online_shopping",
        "fecha": "2026-01-18T16:30:00",
        "tipo": "online",
        "status": "approved"
    }
}
```

---

## Advanced Customization

### Custom Tools

To add new agent capabilities, edit `app/agent/tools/tools.py`:

```python
def my_custom_tool(cliente_id: str, param: str):
    """
    Description of what this tool does.

    Args:
        cliente_id: Customer ID.
        param: Description of parameter.
    """
    # Your logic here
    return {"result": "success"}

my_custom_tool_func = Tool(my_custom_tool)
```

Then register it in `app/agent/agent.py`:

```python
root_agent = Agent(
    ...
    tools=[
        ...,
        my_custom_tool_func,
    ],
)
```

### Custom Scenarios in Prompts

Edit `app/agent/tools/prompts.py` to add new customer journey scenarios in the playbook section.

---

## Testing Your Changes

### 1. Start the Server

```bash
# Using uvicorn directly
python -m uvicorn app.main:app --reload --port 8080

# Or using the module
cd /path/to/project
python -m app.main
```

### 2. Access the UI

Open http://localhost:8080 in your browser.

### 3. Verify Configuration

Check the API endpoint: http://localhost:8080/api/config

This should return your configuration:

```json
{
  "bank_name": "Your Bank Name",
  "bank_country": "Your Country",
  "currency": "USD",
  "currency_symbol": "$",
  "agent_name": "Sarah",
  "colors": {...},
  ...
}
```

### 4. Test Scenarios

Use the scenario selector in the left panel to test different customer journeys.

---

## File Structure Reference

```
app/
├── config.py                 # <-- EDIT THIS FILE
├── main.py                   # FastAPI server
├── agent/
│   ├── agent.py              # Agent configuration
│   ├── data/
│   │   └── mock_data.py      # Customer & transaction data
│   └── tools/
│       ├── prompts.py        # System instructions
│       └── tools.py          # Agent tools/functions
└── static/
    ├── index.html            # UI template
    └── js/
        └── app.js            # Frontend logic
```

---

## Checklist for New Bank Setup

- [ ] Edit `app/config.py`:
  - [ ] `BANK_NAME`
  - [ ] `BANK_COUNTRY`
  - [ ] `BANK_LANGUAGE`
  - [ ] `BANK_CURRENCY` and `BANK_CURRENCY_SYMBOL`
  - [ ] `BANK_ID_DOCUMENT`
  - [ ] `AGENT_NAME` and `AGENT_VOICE`
  - [ ] `BRAND_COLORS`
  - [ ] `CARD_TYPES`
  - [ ] `SCENARIOS`

- [ ] Update mock data (optional):
  - [ ] `app/agent/data/mock_data.py`

- [ ] Test the application:
  - [ ] Start server
  - [ ] Check `/api/config` endpoint
  - [ ] Test each scenario
  - [ ] Verify voice works correctly

---

## Troubleshooting

### Colors not updating?
- Hard refresh the browser (Ctrl+Shift+R)
- Check browser console for errors

### Agent speaks wrong language?
- Verify `BANK_LANGUAGE` in config.py
- Restart the server

### Tools not working?
- Check the Logs tab in the UI
- Look at server terminal for errors

### Voice not working?
- Ensure you clicked the "Voz" button
- Check browser microphone permissions
- Verify `AGENT_VOICE` is a valid voice name
