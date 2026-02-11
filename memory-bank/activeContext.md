# Active Context: Nu-Live-Agent

## Current Work Focus

The Nubank Xpeer implementation is **COMPLETE** with enhanced UI features. All 4 customer journeys are implemented with:
- Full prompt/persona definition
- 16 banking tools
- Mock data for 4 test scenarios
- Nubank-themed UI with dynamic panels
- Voice support (PT-BR with Leda voice)
- Real-time tool logging

## Recent Enhancements ✅

### Documentation Updates (Jan 2026)
- **nubank.md**: Added technical features section (Greeting, Tool Tracking, Transcription)
- **techContext.md**: Updated WebSocket message format with all event types
- **systemPatterns.md**: Added Tool Call Tracking and Greeting patterns

### UI Enhancements (Jan 2026)
- **Scenario Selector**: Dropdown to switch between Lucas/Maria/João/Ana
- **Dynamic Context Panel**: Updates based on selected client
- **Tool Logs Panel**: Real-time visibility of tool calls
- **Tabs**: Toggle between Transactions and Logs views

### API Endpoints Added
- `GET /api/clientes` - List all mock clients
- `GET /api/cliente/{id}` - Get client profile
- `GET /api/transacoes/{cliente_id}` - Get client transactions
- `GET /api/fatura/{cliente_id}` - Get client invoice

## Active Decisions

### Persona: "Xpeer"
- **Tone**: Informal, empathetic, transparent
- **Language**: Portuguese (PT-BR)
- **Principles**: Zero Bancanês, Radical Empathy, Proactivity
- **Emojis**: 💜 🕵️‍♀️ 🙌 🔐 ✨ (used sparingly)
- **Greeting**: Auto-greets customer at conversation start

### Mock-First Strategy
- All banking data is simulated in-memory
- No external banking system integration (yet)
- Focus on UX and persona quality first

### Voice Configuration
- **Model**: gemini-live-2.5-flash-native-audio
- **Voice**: Leda (natural PT-BR female voice)
- **Audio**: PCM streaming with transcription

## Current Test Scenarios

| Client | Journey | Scenario | UI Indicators |
|--------|---------|----------|---------------|
| Lucas Silva | Fraud | PAG*LISTARJ confusion | Ativo, Gold |
| Maria Santos | Debt | R$ 1,680 overdue | ⚠️ 10 dias atraso |
| João Costa | Block | R$ 3,000 at Fasano 23h | Bloqueado 🔐 |
| Ana Oliveira | Wow | Dog ate card | Ativo, Pet 🐕 |

## Known Working Features

- ✅ Text chat (WebSocket)
- ✅ Voice mode (PT-BR)
- ✅ Streaming responses
- ✅ Tool execution
- ✅ Nubank UI theme
- ✅ 3-column layout
- ✅ Scenario selector
- ✅ Dynamic context panel
- ✅ Tool logs panel
- ✅ Automatic greeting

## How to Test

1. Open http://localhost:8000
2. Select a scenario from the dropdown (left panel)
3. Context panel updates automatically
4. Chat with Xpeer (agent greets first)
5. Watch tool calls in the Logs tab (right panel)

### Test Prompts by Scenario

| Scenario | Suggested First Message |
|----------|------------------------|
| Lucas | "Não reconheço a compra de PAGLISTARJ" |
| Maria | "Preciso parcelar minha fatura atrasada" |
| João | "Meu cartão foi bloqueado no restaurante!" |
| Ana | "Meu cachorro comeu meu cartão roxo" |

## Next Steps

1. [ ] Test all 4 journeys end-to-end
2. [ ] Fine-tune Xpeer responses based on testing
3. [ ] Add more edge case scenarios
4. [ ] Implement metrics/logging
5. [ ] Prepare for demo/presentation
