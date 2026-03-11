# Scenario Design Guide - Consignado

This guide explains how to design customer journeys and test scenarios for the consignado agent. Use this as a companion to [CUSTOMIZATION.md](CUSTOMIZATION.md).

---

## Customer Journey Scenarios

### Journey 1: Loan Simulation (Simulacao de Consignado)

**Trigger**: Customer wants to know how much they can borrow and what the monthly payment would be.

**Customer Profile**:
```python
{
    "nome": "Joao Silva",
    "perfil": "servidor_publico",
    "vinculo": "Servidor Publico Estadual",
    "salario_bruto": 8500.00,
    "margem_disponivel": 850.00
}
```

**Conversation Flow**:
```
[CUSTOMER]: "Oi, meu nome e Joao Silva"

[TOOL]: identificar_cliente(termino_busca="Joao")

[CUSTOMER]: "Quero saber quanto posso pegar de emprestimo consignado"

[TOOL]: consultar_margem(cliente_id="joao_silva_001")

[AGENT]: "Joao, sua margem disponivel e de R$850,00.
Qual valor voce gostaria de simular e em quantos meses?"

[CUSTOMER]: "Quero simular 20 mil em 60 meses"

[TOOL]: simular_consignado(cliente_id="joao_silva_001", valor_emprestimo=20000, prazo_meses=60)

[AGENT]: "Aqui esta a simulacao:
- Valor: R$20.000,00
- Parcela: R$521,01/mes
- Taxa: 1,60% a.m. (21,00% a.a.)
- CET estimado: 22,50% a.a.
- Valor total: R$31.260,60
A parcela cabe na sua margem! Deseja registrar a proposta?"
```

---

### Journey 2: Portability (Portabilidade de Consignado)

**Trigger**: Customer has a loan at another bank and wants to transfer it to pay less.

**Customer Profile**:
```python
{
    "nome": "Maria Oliveira",
    "perfil": "aposentada_inss",
    "contrato_outro_banco": {
        "banco_origem": "Banco XYZ",
        "saldo_devedor": 11500.00,
        "taxa_mensal": 2.10
    }
}
```

**Conversation Flow**:
```
[CUSTOMER]: "Ola, sou Maria Oliveira"

[TOOL]: identificar_cliente(termino_busca="Maria")

[CUSTOMER]: "Tenho um emprestimo no Banco XYZ e quero trazer pra ca pra pagar menos"

[TOOL]: simular_portabilidade(cliente_id="maria_oliveira_002")

[AGENT]: "Maria, veja a comparacao:
- Banco XYZ: R$460,00/mes a 2,10% a.m.
- ConsigPro: R$426,91/mes a 1,66% a.m.
- Economia: R$33,09/mes (R$1.191,15 no total!)
O processo leva de 5 a 10 dias uteis. Deseja prosseguir?"
```

---

### Journey 3: Refinancing (Refinanciamento)

**Trigger**: Customer wants to refinance existing loans to reduce monthly payments or get additional cash.

**Customer Profile**:
```python
{
    "nome": "Carlos Santos",
    "perfil": "servidor_federal",
    "contratos_ativos": 2,
    "total_parcelas": 1300.00  # R$890 + R$410
}
```

**Conversation Flow**:
```
[CUSTOMER]: "Oi, sou Carlos Santos"

[TOOL]: identificar_cliente(termino_busca="Carlos")

[CUSTOMER]: "Quero refinanciar meus emprestimos pra diminuir a parcela"

[TOOL]: consultar_contratos(cliente_id="carlos_santos_003")

[AGENT]: "Carlos, voce tem 2 contratos ativos:
- CSG-2023-000789: R$890/mes (48 parcelas restantes)
- CSG-2024-002345: R$410/mes (30 parcelas restantes)
Total: R$1.300/mes. Qual prazo deseja para o refinanciamento?"

[CUSTOMER]: "Pode ser em 96 meses, e quero pegar 5 mil de troco"

[TOOL]: simular_refinanciamento(cliente_id="carlos_santos_003", novo_prazo_meses=96, valor_adicional=5000)

[AGENT]: "Refinanciamento simulado:
- Parcela atual: R$1.300/mes -> Nova parcela: R$812,60/mes
- Reducao de R$487,40/mes!
- Voce recebe R$5.000 na conta.
IMPORTANTE: Prazo maior = mais juros no total."
```

---

### Journey 4: Consignado Card (Cartao Consignado)

**Trigger**: Customer has questions about their consignado credit card (limit, bill, cash withdrawal).

**Customer Profile**:
```python
{
    "nome": "Ana Paula Costa",
    "perfil": "pensionista_inss",
    "cartao_consignado": {
        "limite_total": 2800.00,
        "limite_usado": 1950.00,
        "fatura_atual": 650.00
    }
}
```

**Conversation Flow**:
```
[CUSTOMER]: "Oi, sou Ana Paula Costa"

[TOOL]: identificar_cliente(termino_busca="Ana Paula")

[CUSTOMER]: "Quero saber como esta meu cartao consignado"

[TOOL]: consultar_cartao_consignado(cliente_id="ana_paula_costa_004")
[TOOL]: consultar_fatura_cartao(cliente_id="ana_paula_costa_004")

[AGENT]: "Ana Paula, seu cartao ****5566:
- Limite total: R$2.800
- Usado: R$1.950
- Disponivel: R$850
- Fatura atual: R$650 (vence 10/02)
- Pagamento minimo: R$175 (descontado automaticamente do beneficio)"

[CUSTOMER]: "Consigo fazer um saque de 500 reais?"

[TOOL]: simular_saque_cartao(cliente_id="ana_paula_costa_004", valor_saque=500)

[AGENT]: "Sim! Saque de R$500 disponivel.
- Tarifa: R$17,50 (3,5%)
- Juros: 2,50% a.m.
- Limite disponivel apos saque: R$350,00"
```

---

## Sample Test Prompts

| Journey | Test Prompt |
|---------|-------------|
| Simulation | "Oi, sou Joao Silva. Quero simular um emprestimo consignado" |
| Portability | "Ola, sou Maria Oliveira. Tenho um consignado no Banco XYZ e quero trazer pra ca" |
| Refinancing | "Oi, sou Carlos Santos. Quero refinanciar meus emprestimos" |
| Card | "Oi, sou Ana Paula Costa. Quero saber do meu cartao consignado" |

---

## Files to Modify for New Scenarios

| File | What to Add |
|------|-------------|
| `config.py` | Scenario name in `SCENARIOS` |
| `mock_data.py` | Customer profile and movements |
| `tools.py` | New tools if needed |
| `prompts.py` | Scenario playbook in system prompt |
