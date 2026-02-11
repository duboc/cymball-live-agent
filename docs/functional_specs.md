# Nubank "Xpeer" Agent - Functional Specifications

## 1. Jornada de Contestação de Compra (A "Dor de Cabeça")
**Objective**: Resolve unauthorized transaction reports with empathy and speed, minimizing customer anxiety.

### Trigger
- Customer notification of an unrecognized purchase (e.g., R$ 500.00).
- User Intent: "Não reconheço essa compra", "Clonaram meu cartão".

### Flow
1.  **App Interaction**: User selects transaction -> "Reportar problema" -> Reason: "Golpe/Fraude".
2.  **Agent Analysis (Automated)**:
    -   Check transaction anomaly score.
    -   Check device location vs. transaction location.
    -   Check if chip was read physically or online.
3.  **Xpeer Intervention (Agent)**:
    -   **Persona**: Empathetic, reassuring. "Fica tranquilo, vamos resolver."
    -   **Action**: Initiate dispute process.
    -   **Trust Credit**: If eligible, offer immediate provisional refund ("Crédito de Confiança") so the bill doesn't close in the red.
    -   **Block**: Suggest temporary block if card details are compromised.

### Mocks Needed
-   `Transaction` model (amount, merchant, time, method).
-   `FraudCheck` tool (returns risk score).
-   `Dispute` tool (starts dispute, issues credit).

## 2. Jornada de Negociação de Dívida (A Empatia Financeira)
**Objective**: Recover debt while maintaining the relationship, offering personalized and humane options.

### Trigger
-   Bill overdue > 10 days.
-   User Intent: "Não consigo pagar", "Juros abusivos", "Quero parcelar".

### Flow
1.  **Standard Offer**: Bot offers standard installment plans (User often rejects: "Entrada muito alta").
2.  **Humanized Handover (Xpeer)**:
    -   **Persona**: Understanding, non-judgmental. Listen to context ("Perdi o emprego", "Emergência").
    -   **Action**: Offer "Unlisted" negotiation options (lower interest, lower down payment) based on LTV (Life Time Value).
    -   **Goal**: Long-term retention > Short-term collection.

### Mocks Needed
-   `Debt` model (amount, days_overdue, interest_rate).
-   `NegotiationOptions` tool (returns standard vs. specialized options).

## 3. Jornada de Bloqueio Preventivo (A Segurança Ativa)
**Objective**: Transform a friction point (declined card) into a "feeling of safety".

### Trigger
-   Transaction declined due to suspicious pattern (e.g., high value, unusual time).
-   User Intent: "Meu cartão não passou", "Estou passando vergonha".

### Flow
1.  **Friction**: Card declined. User contacts support angry.
2.  **Validation (Xpeer)**:
    -   **Persona**: Efficient, surgical, protective.
    -   **Action**: Quick identity validation (Selfie/Code).
    -   **Resolution**: Immediate unblock. "Bloqueamos para sua segurança. Pode passar agora."

### Mocks Needed
-   `CardLock` status.
-   `IdentityVerification` tool (mock boolean success).
-   `UnblockCard` tool.

## 4. Jornada "Wow" (O Encantamento)
**Objective**: Surprise users by connecting with their personal stories, creating brand love.

### Trigger
-   Casual mention of personal life during support (e.g., "Cachorro comeu meu cartão").
-   User Intent: usually functional (request new card), but context provides opportunity.

### Flow
1.  **Detection**: Xpeer notices the "hook" (dog ate card).
2.  **Functional Resolution**: Issue 2nd copy of card.
3.  **Wow Action**:
    -   **Persona**: Observant, empowered/autonomous.
    -   **Action**: Send a gift related to the story (Purple toy for dog + Handwritten note).

### Mocks Needed
-   `GiftInventory` (toys, stickers, letters).
-   `SendGift` tool.
