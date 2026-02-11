# Tech Context: Nu-Live-Agent

## Technology Stack

### Backend Framework
- **FastAPI**: Modern Python web framework for API development
  - **WebSocket Support**: Native real-time communication
  - **Automatic Documentation**: OpenAPI/Swagger integration
  - **Type Hints**: Full Python typing support
  - **Async/Await**: Non-blocking request handling

### AI/ML Components
- **Google Gemini 2.5 Flash (Native Audio)**: Primary LLM
  - **Real-time Processing**: Streaming responses
  - **Multi-modal**: Text and audio input/output
  - **Portuguese Language**: Native PT-BR support with Leda voice
  - **ADK Framework**: Agent Development Kit for tool orchestration

### Frontend
- **Vanilla HTML/JS**: Simple, no framework dependencies
- **WebSocket Client**: Real-time bidirectional communication
- **Audio Worklets**: Browser-based audio processing
- **Nubank Theme**: Purple (#8A05BE) branded UI

---

## Development Environment

### Python Requirements
```python
# Key dependencies from requirements.txt
fastapi                    # Web framework
uvicorn                   # ASGI server
websockets                # WebSocket support
google-genai              # Gemini API integration
google-adk                # Agent Development Kit
python-dotenv            # Environment variable management
```

### Environment Configuration
```bash
# Required environment variables (.env)
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## Project Structure

```
nu-live-agent/
├── app/                           # Main application
│   ├── main.py                   # FastAPI server & WebSocket handling
│   ├── nubank/                   # Nubank banking module
│   │   ├── agent.py              # Xpeer agent configuration
│   │   ├── data/
│   │   │   └── mock_data.py      # Simulated clients, transactions, invoices
│   │   └── tools/
│   │       ├── prompts.py        # Xpeer persona & instructions (PT-BR)
│   │       └── tools.py          # 16 banking tools for 4 journeys
│   └── static/                   # Frontend assets
│       ├── index.html            # Nubank-themed UI (3-column layout)
│       └── js/
│           ├── app.js            # WebSocket client & UI logic
│           ├── audio-player.js   # Audio playback handling
│           ├── audio-recorder.js # Microphone capture
│           └── pcm-*-processor.js # Audio worklet processors
├── docs/                         # Documentation
│   ├── functional_specs.md
│   └── technical_specs.md
├── memory-bank/                  # Project context files
├── nubank.md                     # Detailed journey planning document
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container configuration
├── deploy.sh                     # Deployment script
└── setup_venv.sh                 # Local development setup
```

---

## Technical Constraints

### Mock-First Strategy
We are NOT connecting to a real banking core. All data is mocked in-memory:
- **Clients**: 4 mock customers (Lucas, Maria, João, Ana)
- **Transactions**: Sample transactions for fraud scenarios
- **Invoices**: Sample invoices for debt negotiation

### Audio Requirements
- **Language**: PT-BR native audio output/input
- **Voice**: Leda (Google Gemini voice)
- **Format**: PCM audio streaming over WebSocket
- **Latency**: Critical for "human-like" feel

### Real-time Performance
- **WebSocket**: Sub-100ms for text messages
- **Audio Latency**: Target <200ms end-to-end
- **Streaming**: Character-by-character text updates

---

## Agent Configuration

### Xpeer Agent Setup
```python
# app/nubank/agent.py
root_agent = Agent(
    model="gemini-live-2.5-flash-native-audio",
    name="XpeerNubank",
    description="Assistente Nubank Xpeer - Atendimento humanizado e eficiente",
    instruction=top_level_prompt,  # From prompts.py
    tools=[
        # General
        identificar_cliente_tool,
        consultar_historico_cliente_tool,
        # Fraud Journey
        consultar_transacao_tool,
        buscar_transacoes_recentes_tool,
        verificar_padrao_fraude_tool,
        aplicar_credito_confianca_tool,
        iniciar_disputa_bandeira_tool,
        # Debt Journey
        consultar_fatura_tool,
        calcular_parcelamento_tool,
        aplicar_taxa_diferenciada_tool,
        confirmar_acordo_tool,
        # Security Journey
        consultar_bloqueio_tool,
        validar_identidade_tool,
        desbloquear_cartao_tool,
        # Wow Journey
        solicitar_segunda_via_tool,
        criar_wow_moment_tool
    ],
)
```

### Audio Configuration
```python
# Speech settings for Portuguese voice
speech_config = types.SpeechConfig(
    voice_config=types.VoiceConfig(
        prebuilt_voice_config=types.PrebuiltVoiceConfig(
            voice_name="Leda"  # Natural PT-BR female voice
        )
    )
)
```

---

## API Endpoints

### Web Interface
- `GET /` → Main application interface (`static/index.html`)
- `GET /static/*` → Static file serving

### WebSocket Connection
- `WebSocket /ws/{session_id}?is_audio={true|false}` → Real-time communication

### Message Format

#### Client → Server Messages
```javascript
// Text message
{
    "mime_type": "text/plain",
    "data": "message content",
    "role": "user"
}

// Audio message (voice mode)
{
    "mime_type": "audio/pcm", 
    "data": "base64_encoded_audio_data",
    "role": "user"
}
```

#### Server → Client Messages
```javascript
// Text response (streaming)
{
    "mime_type": "text/plain",
    "data": "partial text chunk",
    "role": "model"
}

// Audio response (voice mode)
{
    "mime_type": "audio/pcm", 
    "data": "base64_encoded_audio_data",
    "role": "model"
}

// Turn complete signal
{
    "turn_complete": true,
    "interrupted": false
}

// Input transcription (user's speech → text)
{
    "type": "input_transcription",
    "data": "transcribed user speech",
    "role": "user"
}

// Output transcription (model's speech → text)
{
    "type": "output_transcription",
    "data": "transcribed model response",
    "role": "model"
}

// Tool usage notification (NEW)
{
    "type": "tool_use",
    "tool_name": "consultar_fatura",
    "tool_args": {"cliente_id": "maria_santos_002"},
    "role": "model"
}
```

---

## Development Commands

### Quick Start
```bash
# 1. Clone and setup
git clone https://github.com/duboc/nu-live-agent.git
cd nu-live-agent

# 2. Environment setup
chmod +x setup_venv.sh
./setup_venv.sh

# 3. Configure API key
cp .env.example .env
# Edit .env to add GOOGLE_API_KEY

# 4. Run development server
source venv/bin/activate
cd app
uvicorn main:app --reload

# 5. Access application
open http://localhost:8000
```

### Production Deployment
```bash
# Deploy to Google Cloud Run
./deploy.sh
```

---

## Integration Points

### Google Services
- **Gemini API**: Primary AI model integration
- **ADK Framework**: Agent development and tool management
- **Authentication**: API key-based

### Browser APIs
- **WebSocket API**: Real-time communication
- **Web Audio API**: Audio capture and playback
- **Audio Worklets**: High-performance audio processing
- **MediaDevices API**: Microphone access

---

## Performance Considerations

### Real-time Requirements
- **WebSocket Latency**: Sub-100ms for text
- **Audio Latency**: <200ms end-to-end
- **Streaming Response**: Character-by-character updates
- **Concurrent Sessions**: Multiple users via async

### Memory Management
- **In-memory State**: Mock data in Python dictionaries
- **Session Cleanup**: Automatic on disconnect
- **Audio Buffering**: Minimal for real-time

### Development vs Production
| Aspect | Development | Production |
|--------|-------------|------------|
| Server | Single, hot-reload | Cloud Run |
| Storage | In-memory | In-memory (mock) |
| Audio | Full duplex | Full duplex |
| Sessions | Single user | Multiple |
