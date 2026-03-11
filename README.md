# Consignado Agent - ConsigPro Financeira

An AI-powered customer service agent for payroll loans (crédito consignado), built with Google ADK (Agent Development Kit) and Gemini Live API with native audio support.

## Features

- Voice and text conversation with customers
- Multi-language support (Portuguese, Spanish, English)
- Customizable branding (colors, company name, agent persona)
- 4 pre-built customer journey scenarios for consignado products
- 14 tools for loan simulation, portability, refinancing, and card management
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

## Customer Journey Scenarios

| # | Scenario | Client | Description |
|---|----------|--------|-------------|
| 1 | Loan Simulation | Joao Silva | Public servant wants to simulate a payroll loan |
| 2 | Portability | Maria Oliveira | Retiree wants to transfer loan from another bank |
| 3 | Refinancing | Carlos Santos | Federal servant wants to refinance to reduce payments |
| 4 | Consignado Card | Ana Paula Costa | Pensioner with questions about consignado credit card |

## Agent Tools

The agent has 14 tools for handling customer requests:

| Category | Tools |
|----------|-------|
| **General** | `identificar_cliente`, `consultar_historial_cliente` |
| **Simulation** | `consultar_margem`, `simular_consignado`, `consultar_taxas_vigentes` |
| **Portability** | `simular_portabilidade`, `registrar_proposta` |
| **Refinancing** | `consultar_contratos`, `simular_refinanciamento` |
| **Consignado Card** | `consultar_cartao_consignado`, `consultar_fatura_cartao`, `simular_saque_cartao` |
| **History** | `buscar_transacciones_recientes`, `consultar_transaccion` |

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
│       └── tools.py       # Consignado tools
└── static/
    ├── index.html         # UI with dynamic branding
    └── js/
        └── app.js         # Frontend logic
```

## Configuration

To customize, edit `app/config.py`:

```python
BANK_NAME = "ConsigPro Financeira"
BANK_COUNTRY = "Brasil"
BANK_LANGUAGE = "pt"
BANK_CURRENCY = "BRL"
BANK_CURRENCY_SYMBOL = "R$"
AGENT_NAME = "Ana"
AGENT_VOICE = "Aoede"
```

For complete customization instructions, see **[CUSTOMIZATION.md](CUSTOMIZATION.md)**.

For designing customer journeys and scenarios, see **[SCENARIOS.md](SCENARIOS.md)**.

## Voice Mode

The agent supports voice conversations using `gemini-live-2.5-flash-native-audio`. Available voices:

- **Aoede** - Clear articulation, good for Portuguese
- **Leda** - Spanish, warm female voice
- **Kore** - English, professional female voice
- **Puck** - English, friendly male voice

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Main UI |
| `GET /api/config` | Brand configuration |
| `GET /api/clientes` | List of test customers |
| `GET /api/cliente/{id}` | Customer details |
| `GET /api/transacciones/{id}` | Customer movements |
| `WS /ws/{session_id}` | WebSocket for chat/voice |

## Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **AI**: Google ADK, Gemini Live 2.5 Flash (native audio)
- **Frontend**: Vanilla JavaScript, CSS Variables
- **Deployment**: Docker, Google Cloud Run

## License

MIT
