# System Patterns: Nu-Live-Agent Architecture

## Core Architecture

### High-Level Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │◄──►│  FastAPI Server │◄──►│ Google Gemini   │
│   (Frontend)    │    │   (Backend)     │    │ + ADK           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         └──────────────►│  Tool System    │◄────────────┘
                        │  (16 Functions) │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │  Mock Data      │
                        │  (In-Memory)    │
                        └─────────────────┘
```

### Communication Flow

```
User Message → WebSocket → Agent Session → Tool Execution → Streaming Response → UI Update
```

---

## Design Patterns

### 1. Journey-Based Tool Architecture

Each of the 4 customer journeys has dedicated tools:

```python
# Journey 1: Fraud Dispute
consultar_transacao_tool        # Get transaction details
buscar_transacoes_recentes_tool # List recent transactions
verificar_padrao_fraude_tool    # Run risk analysis
aplicar_credito_confianca_tool  # Apply provisional credit
iniciar_disputa_bandeira_tool   # Start Mastercard/Visa dispute

# Journey 2: Debt Negotiation
consultar_fatura_tool           # Get invoice details
calcular_parcelamento_tool      # Calculate payment plans
aplicar_taxa_diferenciada_tool  # Apply special rate (Xpeer authority)
confirmar_acordo_tool           # Confirm agreement

# Journey 3: Security Block
consultar_bloqueio_tool         # Check block status
validar_identidade_tool         # Validate identity
desbloquear_cartao_tool         # Unblock card

# Journey 4: Wow Moments
solicitar_segunda_via_tool      # Request new card
criar_wow_moment_tool           # Authorize gift sending
```

**Benefits**:
- Clear separation by business domain
- Easy to test and maintain
- Modular expansion

### 2. Persona-Driven System Instructions

The Xpeer persona is defined in `prompts.py` with strict behavioral guidelines:

```python
SYSTEM_INSTRUCTION = """
Você é o Xpeer, o assistente virtual do Nubank...

## 💜 Filosofia Nubank (Sua Personalidade)
1. Zero Bancanês
2. Empatia Radical
3. Transparência
4. Proatividade
5. Emojis
6. Cultura do Erro

## 🛠️ Suas Jornadas Principais (Playbook)
1. Contestação de Compra
2. Negociação de Dívida
3. Bloqueio Preventivo
4. Wow Moment

## 🧭 Regras de Ouro
- Identificação
- Despedida personalizada
- Nunca transfira
"""
```

**Pattern**: Instructions act as both persona definition AND behavioral constraints.

### 3. Mock-First Data Strategy

All banking data is simulated in-memory:

```python
# app/nubank/data/mock_data.py

CLIENTES_NUBANK = {
    "lucas_silva_001": {...},  # Fraud scenario
    "maria_santos_002": {...}, # Debt scenario
    "joao_costa_003": {...},   # Block scenario
    "ana_oliveira_004": {...}  # Wow scenario
}

TRANSACOES = {
    "txn_20260119_001": {...}, # PAG*LISTARJ confusion
    "txn_blocked_001": {...}   # Blocked transaction
}

FATURAS = {
    "fatura_maria_001": {...}  # Overdue invoice
}
```

**Benefits**:
- Rapid prototyping of UX
- No external dependencies
- Controlled scenarios for testing

### 4. WebSocket Session Management

Each user gets an independent session:

```python
async def start_agent_session(session_id, is_audio=False):
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=root_agent,
    )
    
    session = await runner.session_service.create_session(...)
    
    run_config = RunConfig(
        response_modalities=[modality],
        speech_config=speech_config,
        input_audio_transcription=...,
        output_audio_transcription=...
    )
    
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue
```

### 5. Dual-Mode Communication

Support for both text and audio modes:

| Mode | Input | Output | Use Case |
|------|-------|--------|----------|
| Text | JSON text | Streaming text | Web interface |
| Audio | PCM audio | PCM audio + transcription | Voice interface |

### 6. Tool Call Tracking Pattern (NEW)

Real-time visibility into agent tool usage:

```python
# main.py - Tool call tracking
if part.function_call:
    fc = part.function_call
    message = {
        "type": "tool_use",
        "tool_name": fc.name,
        "tool_args": fc.args,
        "role": "model"
    }
    await websocket.send_text(json.dumps(message))
    logger.info(f"[TOOL USE]: {fc.name} args={fc.args}")
```

**Benefits**:
- Debug visibility into agent reasoning
- Real-time logging for demos
- Understanding of which tools are triggered by which inputs

### 7. Greeting Prompt Pattern (NEW)

Agent automatically initiates conversation:

```python
## 🚀 INSTRUÇÃO INICIAL (Greeting)
Assim que a conversa iniciar, saúde o cliente com entusiasmo, 
diga seu nome (Xpeer) e pergunte como pode ajudar hoje.
```

**Implementation**: Part of system instructions, triggered when session starts
**Effect**: User doesn't need to say "Olá" first - agent greets proactively

---

## Data Flow Patterns

### 1. Fraud Investigation Flow

```
User: "Não reconheço essa compra!"
           │
           ▼
    ┌─────────────────┐
    │ consultar_      │─────► Returns transaction details
    │ transacao_tool  │       (Razão Social, location, device)
    └─────────────────┘
           │
           ▼
    ┌─────────────────┐
    │ verificar_      │─────► Returns risk score
    │ padrao_fraude   │       LOW = Name confusion
    └─────────────────┘       HIGH = Real fraud
           │
      ┌────┴────┐
      ▼         ▼
    [LOW]     [HIGH]
      │         │
      ▼         ▼
  Educate   Apply Trust Credit
  Client    + Start Dispute
```

### 2. Debt Negotiation Flow

```
User: "Preciso parcelar minha fatura"
           │
           ▼
    ┌─────────────────┐
    │ consultar_      │─────► Invoice details + options
    │ fatura_tool     │
    └─────────────────┘
           │
           ▼
    ┌─────────────────┐
    │ calcular_       │─────► Standard payment plans
    │ parcelamento    │
    └─────────────────┘
           │
    Client struggles?
      ┌────┴────┐
      ▼         ▼
    [No]      [Yes]
      │         │
      ▼         ▼
  Standard   ┌─────────────────┐
  Options    │ aplicar_taxa_   │─────► Special rate (1.5% vs 3.9%)
             │ diferenciada    │
             └─────────────────┘
```

### 3. Security Block Flow

```
User: "MEU CARTÃO NÃO PASSA!!!"
           │
           ▼
    ┌─────────────────┐
    │ consultar_      │─────► Block reason
    │ bloqueio_tool   │
    └─────────────────┘
           │
           ▼
    ┌─────────────────┐
    │ validar_        │─────► Quick identity check
    │ identidade      │       (CPF + context)
    └─────────────────┘
           │
           ▼
    ┌─────────────────┐
    │ desbloquear_    │─────► Card active again
    │ cartao_tool     │
    └─────────────────┘
           │
           ▼
    Reframe: "Proteção ativa"
```

### 4. Wow Moment Flow

```
User: "Meu cachorro comeu o cartão 😅"
           │
           ▼
    ┌─────────────────┐
    │ solicitar_      │─────► New card ordered
    │ segunda_via     │
    └─────────────────┘
           │
    Opportunity detected!
           │
           ▼
    ┌─────────────────┐
    │ criar_wow_      │─────► Gift authorized
    │ moment_tool     │       (Purple pet toy + card)
    └─────────────────┘
           │
           ▼
    Personalized farewell
    "Manda um oi pro Rex! 🐕"
```

---

## Key Technical Decisions

### 1. Native Audio Model
**Decision**: Use `gemini-live-2.5-flash-native-audio` instead of half-cascade
**Rationale**: Native models have better PT-BR intonation and lower latency
**Trade-off**: Audio-only output modality (no mixed text+audio)

### 2. Tool-Use for Actions, Not Just Info
**Decision**: Tools perform actions (block card, send gift), not just retrieve data
**Rationale**: Gives user sense of resolution, not just information
**Example**: `desbloquear_cartao_tool` actually "unblocks" (simulated)

### 3. Persona as Constraint System
**Decision**: System instructions define both personality AND behavioral rules
**Rationale**: LLM naturally follows persona while staying within guardrails
**Implementation**: Journeys defined as "Playbook" with specific steps

### 4. Three-Column UI
**Decision**: Context | Chat | Transactions layout
**Rationale**: Mimics real agent workstation, shows customer info at glance
**Benefit**: Xpeer has context without asking customer

---

## Error Handling Patterns

### Graceful Degradation
```python
def consultar_transacao(transacao_id: str):
    if transacao_id in TRANSACOES:
        return TRANSACOES[transacao_id]
    return {"erro": "Transação não encontrada."}
```

### Client Validation
```python
def _get_cliente_by_cpf_or_name(termo: str) -> Optional[str]:
    termo = termo.lower().strip()
    for cid, data in CLIENTES_NUBANK.items():
        if termo in data["nome"].lower() or termo in data["cpf_ultimos_digitos"]:
            return cid
    return None
```

### Risk Scoring Logic
```python
def verificar_padrao_fraude(transacao_id: str):
    txn = TRANSACOES.get(transacao_id)
    
    # Known device + name confusion = LOW risk
    if "LISTARJ" in txn["nome_fatura"] and txn["device_conhecido"]:
        return {"risco": "BAIXO", "recomendacao": "Educar cliente"}
    
    # High value + late night = HIGH risk
    if txn["valor"] > 2000 and "23:" in txn["horario"]:
        return {"risco": "ALTO", "recomendacao": "Manter bloqueio"}
    
    return {"risco": "MEDIO", "recomendacao": "Confirmar com titular"}
```

---

## Future Architecture Considerations

### Scalability Path
1. **Database**: Replace in-memory with PostgreSQL/MongoDB
2. **Sessions**: Redis for distributed session storage
3. **Load Balancing**: Multiple Cloud Run instances
4. **Metrics**: Prometheus + Grafana for monitoring

### Integration Path
1. **Real Banking Core**: Replace mock data with actual APIs
2. **CRM Integration**: Customer history from real systems
3. **Fraud System**: Connect to actual risk scoring
4. **Shipping System**: Real gift fulfillment for Wow moments
