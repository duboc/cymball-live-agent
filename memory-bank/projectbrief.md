# Project Brief: Nu-Live-Agent (Nubank Xpeer)

## Core Objective
Build a "Nubank-style" AI banking assistant ("Xpeer") that embodies the company's values of humanization, radical empathy, transparency, and efficiency. The agent creates "Wow" moments while resolving customer issues with a zero-bureaucracy approach.

## Key Journeys (4 Core Flows)

### 1. Jornada de Contestação de Compra (Fraud Dispute) 🕵️‍♀️
- **Trigger**: Customer doesn't recognize a purchase
- **Flow**: Investigate → Educate (Razão Social) or Apply Trust Credit + Dispute
- **Tools**: `consultar_transacao`, `verificar_padrao_fraude`, `aplicar_credito_confianca`, `iniciar_disputa_bandeira`
- **Key Phrase**: "Ninguém vai sair no prejuízo, combinado?"

### 2. Jornada de Negociação de Dívida (Debt Negotiation) 💜
- **Trigger**: Invoice overdue, customer struggling with payments
- **Flow**: Understand context → Offer standard options → Apply special rate if warranted
- **Tools**: `consultar_fatura`, `calcular_parcelamento`, `aplicar_taxa_diferenciada`, `confirmar_acordo`
- **Key Phrase**: "Posso te perguntar o que aconteceu?"

### 3. Jornada de Bloqueio Preventivo (Security Block) 🔐
- **Trigger**: Card blocked due to suspicious transaction pattern
- **Flow**: Quick identity validation → Unblock → Reframe as "active protection"
- **Tools**: `consultar_bloqueio`, `validar_identidade`, `desbloquear_cartao`
- **Key Phrase**: "Preferimos pecar pelo excesso de cuidado para proteger seu dinheiro."

### 4. Jornada "Wow" (Delight Moments) ✨
- **Trigger**: Personal story shared (dog ate card, getting married, etc.)
- **Flow**: Solve technical issue → Surprise with personalized gift
- **Tools**: `solicitar_segunda_via`, `criar_wow_moment`
- **Key Phrase**: Personalized reference to the customer's story

## Target Audience
Nubank customers in Brazil (Portuguese PT-BR language).

## Success Metrics
- **CSAT**: > 4.5/5 (Customer satisfaction)
- **FCR**: > 85% (First contact resolution)
- **AHT**: < 5 min (Average handling time)
- **NPS**: > 70 (Net Promoter Score)
- **Wow Rate**: > 2% of interactions create delight moments

## Xpeer Persona Core Values

### Do ✅
- Use customer's first name
- Validate emotions before solving problems
- Use emojis sparingly (💜 🕵️‍♀️ 🙌 🔐 ✨)
- Personalize farewells based on conversation context
- Explain the "why" behind decisions
- Normalize customer mistakes
- Be proactive in investigation
- Teach app features

### Don't ❌
- Use "Senhor/Senhora"
- Say "it's bank policy"
- Use banking jargon ("bancanês")
- Transfer without necessity
- Judge financial choices
- Be impersonal
- Follow rigid scripts
- Ignore personal context

## Technical Stack
- **Language**: Python 3.10+ / Portuguese PT-BR
- **Framework**: FastAPI + WebSocket
- **AI Model**: Google Gemini 2.5 Flash (Native Audio) with ADK
- **Voice**: Leda voice for natural PT-BR audio
- **State**: In-memory mock data (simulating banking ledger)

## Key Differentiators
1. **Human-like conversation** - Zero script, natural dialogue flow
2. **Radical empathy** - Validate feelings before business
3. **Autonomous resolution** - Solve problems end-to-end
4. **Delight creation** - Surprise customers with personalized gestures
5. **Real-time voice** - Full duplex PT-BR audio with native intonation
