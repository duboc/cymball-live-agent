# Banking Agent Template

A customizable AI-powered customer service agent for banks, built with Google ADK (Agent Development Kit) and Gemini Live API with native audio support.

**Easily adaptable** for different banks, languages, and regions by editing a single configuration file.

## Features

- Voice and text conversation with customers
- Multi-language support (Spanish, English, Portuguese)
- Customizable branding (colors, bank name, agent persona)
- 4 pre-built customer journey scenarios
- 15 banking tools for common operations
- Real-time transcription for voice mode
- Cloud Run deployment ready

## Quick Start

### Requirements

- Python 3.11+
- Google API Key with Gemini access

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo "GOOGLE_API_KEY=your-key-here" > .env
```

### Run Locally

```bash
uvicorn app.main:app --reload --port 8080
```

Open http://localhost:8080 in your browser.

### Deploy to Cloud Run

```bash
./deploy.sh
```

## Customization

To customize this template for your bank, edit **one file**:

```
app/config.py
```

### Example Configuration

```python
# Bank Identity
BANK_NAME = "Your Bank Name"
BANK_COUNTRY = "United States"
BANK_LANGUAGE = "en"  # es, en, or pt
BANK_CURRENCY = "USD"
BANK_CURRENCY_SYMBOL = "$"

# Agent Persona
AGENT_NAME = "Sarah"
AGENT_VOICE = "Kore"  # Gemini voice

# Brand Colors
BRAND_COLORS = {
    "primary": "#1E40AF",
    "primary_dark": "#1E3A8A",
    ...
}
```

For complete customization instructions, see **[CUSTOMIZATION.md](CUSTOMIZATION.md)**.

For designing customer journeys and scenarios, see **[SCENARIOS.md](SCENARIOS.md)**.

## Customer Journey Scenarios

| # | Scenario | Description |
|---|----------|-------------|
| 1 | Collections | Early delinquency - overdue minimum payment |
| 2 | Benefits Inquiry | Points program and deferred payment options |
| 3 | Travel Security | Card blocked abroad, travel notice registration |
| 4 | Dispute/Claim | Unrecognized charge, fraud prevention |

## Agent Tools

The agent has 15 tools for handling customer requests:

| Category | Tools |
|----------|-------|
| **General** | `identificar_cliente`, `consultar_historial_cliente` |
| **Collections** | `consultar_mora`, `registrar_pago_prometido` |
| **Benefits** | `consultar_beneficios_tarjeta`, `consultar_puntos`, `consultar_disponible` |
| **Security** | `validar_identidad`, `autorizar_transaccion`, `registrar_aviso_viaje` |
| **Disputes** | `buscar_transacciones_recientes`, `bloquear_tarjeta`, `registrar_reclamacion`, `solicitar_reposicion`, `consultar_transaccion` |

## Project Structure

```
app/
├── config.py              # <-- EDIT THIS FILE FOR CUSTOMIZATION
├── main.py                # FastAPI server + WebSocket
├── agent/
│   ├── agent.py           # Agent configuration
│   ├── data/
│   │   └── mock_data.py   # Sample customer data
│   └── tools/
│       ├── prompts.py     # Multi-language system prompts
│       └── tools.py       # Banking tools
└── static/
    ├── index.html         # UI with dynamic branding
    └── js/
        └── app.js         # Frontend logic
```

## Language Support

| Language | Code | Voice |
|----------|------|-------|
| Spanish | `es` | Leda |
| English | `en` | Kore |
| Portuguese | `pt` | Aoede |

Set the language in `config.py`:

```python
BANK_LANGUAGE = "en"
```

## Voice Mode

The agent supports voice conversations using `gemini-live-2.5-flash-native-audio`. Available voices:

- **Leda** - Spanish, warm female voice
- **Kore** - English, professional female voice
- **Aoede** - Neutral, clear articulation
- **Puck** - English, friendly male voice
- **Charon**, **Fenrir**, **Orus**, **Zephyr** - Additional options

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Main UI |
| `GET /api/config` | Brand configuration |
| `GET /api/clientes` | List of test customers |
| `GET /api/cliente/{id}` | Customer details |
| `GET /api/transacciones/{id}` | Customer transactions |
| `WS /ws/{session_id}` | WebSocket for chat/voice |

## Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **AI**: Google ADK, Gemini Live 2.5 Flash (native audio)
- **Frontend**: Vanilla JavaScript, CSS Variables
- **Deployment**: Docker, Google Cloud Run

## License

MIT
