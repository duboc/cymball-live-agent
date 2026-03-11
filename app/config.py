"""
ConsigPro Financeira - Agent Configuration
============================================

This is the ONLY file you need to edit to customize this template.
All specific values are centralized here.
"""

# =============================================================================
# COMPANY IDENTITY
# =============================================================================

BANK_NAME = "ConsigPro Financeira"
BANK_COUNTRY = "Brasil"
BANK_LANGUAGE = "pt"
BANK_CURRENCY = "BRL"
BANK_CURRENCY_SYMBOL = "R$"

BANK_ID_DOCUMENT = "CPF"
BANK_ID_DOCUMENT_FULL = "Cadastro de Pessoa Fisica"

# =============================================================================
# AGENT PERSONA
# =============================================================================

AGENT_NAME = "Sara"
AGENT_DESCRIPTION = f"Consultora Financeira - {BANK_NAME}, {BANK_COUNTRY}"

AGENT_VOICE = "Aoede"

# =============================================================================
# BRAND COLORS
# =============================================================================

BRAND_COLORS = {
    "primary": "#0D7C3D",
    "primary_dark": "#095C2C",
    "primary_light": "#2EAD5E",
    "success": "#00A86B",
    "warning": "#FFB800",
    "error": "#FF4444",
    "text": "#191919",
    "background": "#EFEFEF",
    "card_background": "#FFFFFF",
}

# =============================================================================
# PRODUCTS
# =============================================================================

CARD_TYPES = {
    "emprestimo_consignado": {
        "nome": "Emprestimo Consignado INSS",
        "descricao": "Credito com desconto direto no beneficio INSS",
    },
    "credito_pessoal": {
        "nome": "Credito Pessoal",
        "descricao": "Credito pessoal com parcelas fixas",
        "requisitos": "Portabilidade do beneficio para a ConsigPro Financeira",
    },
    "portabilidade": {
        "nome": "Portabilidade",
        "descricao": "Transferencia de contrato de outro banco com melhores condicoes",
    },
    "refinanciamento": {
        "nome": "Refinanciamento",
        "descricao": "Renegociacao de contrato existente com liberacao de valor adicional",
    },
}

# =============================================================================
# SCENARIOS
# =============================================================================

SCENARIOS = {
    "maria_santos_001": {
        "name": "Emprestimo Consignado",
        "description": "Aposentada quer contratar emprestimo consignado direto",
    },
    "jose_carlos_002": {
        "name": "Portabilidade + Credito",
        "description": "Aposentado quer portabilidade e credito pessoal (combo com requisitos)",
    },
    "ana_beatriz_003": {
        "name": "Refinanciamento",
        "description": "Pensionista quer refinanciar para aliviar parcela mensal",
    },
    "roberto_lima_004": {
        "name": "Pacote Completo",
        "description": "Aposentado com 4 propostas, quer entender tudo e escolher",
    },
    "francisca_oliveira_005": {
        "name": "Simulacao de Financiamento",
        "description": "Aposentada quer simular um novo emprestimo consignado (sem proposta pre-aprovada)",
    },
}

# =============================================================================
# UI TEXT
# =============================================================================

UI_TEXT = {
    "app_title": f"{BANK_NAME} - Propostas Pre-Aprovadas",
    "context_header": "Contexto do Cliente",
    "chat_status_connected": "Conectado",
    "chat_status_disconnected": "Desconectado",
    "scenario_label": "Cenario de Teste",
    "client_label": "Cliente",
    "available_limit_label": "Valor Pre-Aprovado",
    "minimum_payment_label": "Propostas",
    "customer_since_label": "Tempo como Cliente",
    "card_status_label": "Situacao",
    "typing_indicator": "A consultora esta digitando...",
    "input_placeholder": "Digite sua mensagem...",
    "send_button": "Enviar",
    "voice_button": "Voz",
    "stop_button": "Parar",
    "recording_indicator": "Gravando...",
    "transactions_tab": "Propostas",
    "logs_tab": "Logs",
    "loading_transactions": "Carregando propostas...",
    "tool_logs_placeholder": "As chamadas de ferramentas aparecerao aqui...",
    "help_title": "Como Testar os Cenarios",
    "help_step1": "Identificar-se",
    "help_step2": "Pergunte sobre as propostas",
    "help_step3": "Interaja",
    "voice_tip": "Use o modo voz para uma experiencia mais realista.",
}

# =============================================================================
# OPERATIONAL SETTINGS
# =============================================================================

TIMEFRAMES = {
    "proposta_aprovacao": "ate 24 horas uteis",
    "portabilidade_prazo": "5 a 10 dias uteis",
    "cartao_entrega": "7 a 10 dias uteis",
}

PAYMENT_CHANNELS = ["App", "Internet Banking", "Agencia"]
DELIVERY_OPTIONS = ["domicilio", "agencia"]
