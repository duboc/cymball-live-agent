# Plano de Migração: Banking Agent → Consignado Agent

## Contexto
Migrar a demo atual (Cymball Bank - banco genérico espanhol com cenários de cobrança, benefícios, segurança e disputas) para uma **financeira fictícia brasileira de crédito consignado e produtos financeiros consignados**.

## Empresa Fictícia
- **Nome**: ConsigPro Financeira
- **País**: Brasil
- **Idioma**: pt (Português Brasileiro)
- **Moeda**: BRL / R$
- **Documento**: CPF
- **Agente**: Ana (voz: Aoede)

---

## Resumo das Mudanças

### O que NÃO muda (infraestrutura preservada)
- Arquitetura FastAPI + WebSocket + Gemini Live API
- Estrutura de diretórios (`app/`, `agent/`, `tools/`, `data/`, `static/`)
- Fluxo de áudio (PCM, transcrição, barge-in)
- Frontend JS (`app.js`, audio worklets)
- Integração Asterisk/FreePBX (docs de integração)
- Mecanismo de config dinâmica via `/api/config`
- Lógica de WebSocket em `main.py` (mantida 100%)
- `deploy.sh`, `Dockerfile`, `requirements.txt`

### O que MUDA (conteúdo/domínio)

---

## Arquivos a Modificar

### 1. `app/config.py` — Identidade e Cenários
**Mudanças**:
- `BANK_NAME` → `"ConsigPro Financeira"`
- `BANK_COUNTRY` → `"Brasil"`
- `BANK_LANGUAGE` → `"pt"`
- `BANK_CURRENCY` → `"BRL"` / `BANK_CURRENCY_SYMBOL` → `"R$"`
- `BANK_ID_DOCUMENT` → `"CPF"` / `BANK_ID_DOCUMENT_FULL` → `"Cadastro de Pessoa Física"`
- `AGENT_NAME` → `"Ana"` / `AGENT_VOICE` → `"Aoede"`
- `BRAND_COLORS` → paleta verde/dourada (financeira)
- `CARD_TYPES` → substituir por `PRODUTOS_CONSIGNADO` (tipos de empréstimo consignado)
- `SCENARIOS` → 4 novos cenários de consignado
- `UI_TEXT` → traduzir para português com termos de consignado
- `PAYMENT_CHANNELS` → `["App", "Internet Banking", "Agência"]`

**Novos cenários**:
| # | Cenário | Cliente | Descrição |
|---|---------|---------|-----------|
| 1 | Simulação de Consignado | João Silva | Servidor público quer simular empréstimo consignado |
| 2 | Portabilidade de Consignado | Maria Oliveira | Quer trazer consignado de outra instituição |
| 3 | Refinanciamento | Carlos Santos | Quer refinanciar consignado existente para reduzir parcela |
| 4 | Cartão Consignado | Ana Paula Costa | Dúvidas sobre cartão de crédito consignado (limite, fatura) |

**Novos produtos** (substitui `CARD_TYPES`):
```python
PRODUTOS_CONSIGNADO = {
    "consignado_inss": {
        "nome": "Consignado INSS",
        "taxa_mensal": 1.66,  # % ao mês (teto regulatório)
        "prazo_maximo": 84,   # meses
        "margem_consignavel": 35,  # % do benefício
        "margem_cartao": 5,   # % adicional para cartão
        "publico": "Aposentados e pensionistas INSS"
    },
    "consignado_servidor": {
        "nome": "Consignado Servidor Público",
        "taxa_mensal": 1.50,
        "prazo_maximo": 96,
        "margem_consignavel": 35,
        "margem_cartao": 5,
        "publico": "Servidores públicos federais, estaduais e municipais"
    },
    "consignado_privado": {
        "nome": "Consignado CLT",
        "taxa_mensal": 2.20,
        "prazo_maximo": 48,
        "margem_consignavel": 30,
        "margem_cartao": 0,
        "publico": "Trabalhadores CLT de empresas conveniadas"
    },
    "cartao_consignado": {
        "nome": "Cartão Consignado",
        "taxa_mensal": 2.50,
        "limite_sobre_margem": "até 1.6x da margem",
        "anuidade": 0,
        "saque": True,
        "publico": "Aposentados, pensionistas e servidores"
    }
}
```

---

### 2. `app/agent/data/mock_data.py` — Dados Fictícios
**Mudanças**: Substituir completamente clientes e transações.

**Novos clientes**:
```python
CLIENTES = {
    "joao_silva_001": {
        "nome": "João Silva",
        "cpf": "123.456.789-00",
        "cpf_ultimos_digitos": "9-00",
        "vinculo": "Servidor Público Estadual",
        "orgao": "Secretaria de Educação - SP",
        "salario_bruto": 8500.00,
        "margem_disponivel": 850.00,  # 35% - consignações atuais
        "margem_cartao_disponivel": 425.00,
        "contratos_ativos": 1,
        "contrato_atual": {
            "numero": "CSG-2024-001234",
            "valor_emprestado": 25000.00,
            "parcela_mensal": 520.00,
            "parcelas_pagas": 18,
            "parcelas_restantes": 42,
            "saldo_devedor": 18200.00,
            "taxa_mensal": 1.80
        },
        "perfil": "servidor_publico",
        "tempo_cliente": "2 anos",
        "email": "joao.s***@gmail.com",
        "telefono": "+55 11 9**** 4567"
    },
    "maria_oliveira_002": {
        "nome": "Maria Oliveira",
        "cpf": "987.654.321-00",
        "cpf_ultimos_digitos": "1-00",
        "vinculo": "Aposentada INSS",
        "beneficio_inss": "123.456.789-0",
        "salario_bruto": 4200.00,
        "margem_disponivel": 1470.00,  # margem total (sem consignação ativa)
        "margem_cartao_disponivel": 210.00,
        "contratos_ativos": 1,
        "contrato_outro_banco": {
            "banco_origem": "Banco XYZ",
            "numero": "XYZ-2023-5678",
            "valor_emprestado": 15000.00,
            "parcela_mensal": 380.00,
            "parcelas_restantes": 36,
            "saldo_devedor": 11500.00,
            "taxa_mensal": 2.10
        },
        "perfil": "aposentada_inss",
        "tempo_cliente": "Novo cliente (portabilidade)",
        "email": "maria.o***@hotmail.com",
        "telefono": "+55 21 9**** 8901"
    },
    "carlos_santos_003": {
        "nome": "Carlos Santos",
        "cpf": "456.789.123-00",
        "cpf_ultimos_digitos": "3-00",
        "vinculo": "Servidor Público Federal",
        "orgao": "Ministério da Saúde",
        "salario_bruto": 12000.00,
        "margem_disponivel": 200.00,  # margem quase esgotada
        "margem_cartao_disponivel": 600.00,
        "contratos_ativos": 2,
        "contratos": [
            {
                "numero": "CSG-2023-000789",
                "valor_emprestado": 40000.00,
                "parcela_mensal": 890.00,
                "parcelas_pagas": 24,
                "parcelas_restantes": 48,
                "saldo_devedor": 28000.00,
                "taxa_mensal": 2.00
            },
            {
                "numero": "CSG-2024-002345",
                "valor_emprestado": 15000.00,
                "parcela_mensal": 410.00,
                "parcelas_pagas": 6,
                "parcelas_restantes": 30,
                "saldo_devedor": 13200.00,
                "taxa_mensal": 1.90
            }
        ],
        "perfil": "servidor_federal",
        "tempo_cliente": "3 anos e 2 meses",
        "email": "carlos.s***@gmail.com",
        "telefono": "+55 61 9**** 2345"
    },
    "ana_paula_costa_004": {
        "nome": "Ana Paula Costa",
        "cpf": "321.654.987-00",
        "cpf_ultimos_digitos": "7-00",
        "vinculo": "Pensionista INSS",
        "beneficio_inss": "987.654.321-0",
        "salario_bruto": 3500.00,
        "margem_disponivel": 525.00,
        "margem_cartao_disponivel": 175.00,
        "cartao_consignado": {
            "numero_cartao": "****5566",
            "limite_total": 2800.00,
            "limite_usado": 1950.00,
            "fatura_atual": 650.00,
            "vencimento_fatura": "2026-02-10",
            "pagamento_minimo": 175.00,  # desconto em folha
            "status": "ativa"
        },
        "perfil": "pensionista_inss",
        "tempo_cliente": "1 ano e 5 meses",
        "email": "ana.p***@yahoo.com.br",
        "telefono": "+55 31 9**** 6789"
    }
}
```

**Novos "transações"** → renomear para `MOVIMENTACOES` (parcelas, saques, portabilidades):
```python
MOVIMENTACOES = {
    # João - Parcelas do consignado
    "mov_joao_001": { "cliente_id": "joao_silva_001", "tipo": "parcela", "valor": 520.00, "descricao": "Parcela 18/60 - CSG-2024-001234", "data": "2026-01-05", "status": "paga" },
    "mov_joao_002": { "cliente_id": "joao_silva_001", "tipo": "parcela", "valor": 520.00, "descricao": "Parcela 19/60 - CSG-2024-001234", "data": "2026-02-05", "status": "pendente" },
    # ... mais movimentações para cada cliente
}
```

**Remover**: `ESTADOS_CUENTA`, `BENEFICIOS_TARJETAS`
**Adicionar**: `SIMULACOES_CACHE` (para ferramenta de simulação)

---

### 3. `app/agent/tools/tools.py` — Ferramentas do Agente
**Remover** ferramentas bancárias atuais (15 tools).
**Criar** novas ferramentas de consignado:

| Tool | Descrição |
|------|-----------|
| `identificar_cliente` | Busca cliente por nome ou CPF (mantém lógica similar) |
| `consultar_margem` | Consulta margem consignável disponível |
| `simular_consignado` | Simula empréstimo (valor, prazo, taxa, parcela) |
| `consultar_contratos` | Lista contratos ativos do cliente |
| `simular_portabilidade` | Simula portabilidade de outro banco (economia mensal) |
| `registrar_proposta` | Registra proposta de empréstimo/portabilidade |
| `simular_refinanciamento` | Simula refinanciamento com novo prazo/valor |
| `consultar_cartao_consignado` | Consulta dados do cartão consignado (limite, fatura) |
| `consultar_fatura_cartao` | Consulta fatura atual do cartão consignado |
| `simular_saque_cartao` | Simula saque no cartão consignado |
| `consultar_taxas_vigentes` | Retorna taxas atuais por produto |
| `consultar_historico_pagamentos` | Histórico de parcelas pagas/pendentes |

---

### 4. `app/agent/tools/prompts.py` — Prompt do Sistema
**Mudanças**: Reescrever o bloco `pt` completamente para o contexto de consignado.

**Novo prompt** (resumo da estrutura):
- Persona: Ana, consultora financeira da ConsigPro
- Tom: Consultivo, educativo, transparente com taxas e condições
- Cenário 1: Simulação → usa `simular_consignado`, explica CET, margem
- Cenário 2: Portabilidade → usa `simular_portabilidade`, compara taxas
- Cenário 3: Refinanciamento → usa `simular_refinanciamento`, explica tradeoffs
- Cenário 4: Cartão Consignado → usa `consultar_cartao_consignado`, explica limite/fatura
- Regras de ouro: sempre informar CET, prazo, taxa, valor total pago

---

### 5. `app/agent/agent.py` — Registro de Ferramentas
**Mudanças**: Atualizar imports para as novas ferramentas de consignado.

---

### 6. `app/static/index.html` — Interface
**Mudanças**:
- Traduzir todo texto hardcoded para PT-BR
- Atualizar cenários no seletor e modal de ajuda
- Trocar nomes de clientes e frases-guia dos cenários
- Substituir "DNI" por "CPF"
- Ajustar labels: "Limite Disponível" → "Margem Disponível", "Pago Mínimo" → "Parcela Atual", etc.
- Trocar ícone 🏦 por 💰 ou similar

---

### 7. `app/main.py` — Endpoints da API
**Mudanças mínimas**:
- Endpoint `/api/transacciones` → `/api/movimentacoes` (ou manter e adaptar)
- Endpoint `/api/estado-cuenta` → `/api/contratos`
- Manter compatibilidade do WebSocket (sem mudanças)

---

### 8. Documentação (`README.md`, `CUSTOMIZATION.md`, `SCENARIOS.md`)
- Atualizar exemplos e descrições para o contexto de consignado
- Manter estrutura dos docs

### 9. `docs/functional_specs.md` e `docs/technical_specs.md`
- Reescrever para refletir o novo domínio

---

## Ordem de Execução

1. **`config.py`** — Base de tudo, define identidade e produtos
2. **`mock_data.py`** — Dados dos clientes e movimentações
3. **`tools.py`** — Ferramentas do agente (dependem do mock_data)
4. **`prompts.py`** — Prompt do sistema (depende do config)
5. **`agent.py`** — Registrar novas ferramentas
6. **`main.py`** — Ajustar endpoints de API
7. **`index.html`** — Interface atualizada
8. **Docs** — README, SCENARIOS, CUSTOMIZATION

---

## Validação Pós-Mudança

- [ ] `uvicorn app.main:app --reload` inicia sem erros
- [ ] `/api/config` retorna nova identidade (ConsigPro, BRL, pt)
- [ ] `/api/clientes` lista os 4 novos clientes
- [ ] Cenário 1: Simular consignado para João funciona
- [ ] Cenário 2: Portabilidade para Maria funciona
- [ ] Cenário 3: Refinanciamento para Carlos funciona
- [ ] Cenário 4: Cartão consignado para Ana Paula funciona
- [ ] Modo voz funciona com respostas em português
- [ ] Ferramentas aparecem nos logs corretamente

---

## Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Quebrar WebSocket/áudio | Não alterar `main.py` (fluxo WS), apenas endpoints REST |
| Prompt muito longo | Manter tamanho similar ao atual (~250 linhas) |
| Ferramentas com bugs | Manter padrão de mock data (sem lógica complexa) |
| UI quebrada | Testar cada cenário no navegador após mudança |
