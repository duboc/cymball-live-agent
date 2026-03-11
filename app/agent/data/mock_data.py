"""
Mock Data - ConsigPro Financeira - Propostas Pre-Aprovadas
===========================================================

4 clients, each with different pre-approved proposals for distinct scenarios.
"""

try:
    from ...config import CARD_TYPES
except ImportError:
    from config import CARD_TYPES

BENEFICIOS_TARJETAS = CARD_TYPES

# =============================================================================
# CUSTOMERS
# =============================================================================

CLIENTES = {
    # =========================================================================
    # CENARIO 1: Maria Santos - Emprestimo Consignado (venda direta)
    # =========================================================================
    "maria_santos_001": {
        "nome": "Maria Santos",
        "tempo_cliente": "2 anos e 8 meses",
        "dni": "111.222.333-44",
        "dni_ultimos_digitos": "3-44",
        "cpf": "111.222.333-44",
        "cpf_ultimos_digitos": "3-44",
        "email": "maria.s***@gmail.com",
        "telefono": "+55 11 9**** 5678",
        "perfil": "aposentada_inss",
        "vinculo": "Aposentada INSS",
        "beneficio_inss": "****3201",
        "salario_bruto": 2800.00,
        "banco_atual": {
            "banco": "CAIXA ECONOMICA FEDERAL",
            "codigo_banco": "104",
            "agencia": "1234",
            "conta": "****567-2",
        },
        "propostas_pre_aprovadas": {
            "emprestimo_consignado": {
                "numero_proposta": "570013160",
                "tipo": "Emprestimo Consignado INSS",
                "valor_liberado": 8500.00,
                "parcelas": 84,
                "valor_parcela": 198.45,
                "status": "pre_aprovada",
                "ativa": True,
            },
        },
        "valor_total_pre_aprovado": 8500.00,
        "tarjeta_terminacion": "N/A",
        "tipo_tarjeta": "Emprestimo Consignado",
        "limite_credito": 8500.00,
        "limite_usado": 0.00,
        "tarjeta_status": "ativo",
        "ultima_interaccion": "2026-03-10",
        "margem_total": 980.00,
        "margem_disponivel": 8500.00,
        "margem_cartao_disponivel": 0.00,
        "contratos_ativos": 0,
        "simulacao": {
            "margem_consignavel_35": 980.00,
            "taxa_mensal": 1.80,
            "taxa_anual": 23.87,
            "cet_mensal": 1.95,
            "cet_anual": 26.08,
            "iof_percentual": 0.38,
            "iof_adicional_diario": 0.0082,
            "prazo_maximo_meses": 84,
            "sistema_amortizacao": "Tabela Price",
        },
    },

    # =========================================================================
    # CENARIO 2: Jose Carlos - Portabilidade + Credito Pessoal
    # =========================================================================
    "jose_carlos_002": {
        "nome": "Jose Carlos",
        "tempo_cliente": "4 anos e 3 meses",
        "dni": "234.567.890-11",
        "dni_ultimos_digitos": "0-11",
        "cpf": "234.567.890-11",
        "cpf_ultimos_digitos": "0-11",
        "email": "jose.c***@gmail.com",
        "telefono": "+55 31 9**** 1234",
        "perfil": "aposentado_inss",
        "vinculo": "Aposentado INSS",
        "beneficio_inss": "****6261",
        "salario_bruto": 3200.00,
        "banco_atual": {
            "banco": "BANCO DO BRASIL",
            "codigo_banco": "1",
            "agencia": "1",
            "conta": "****443-8",
        },
        "propostas_pre_aprovadas": {
            "portabilidade": {
                "numero_proposta": "570013155",
                "tipo": "Portabilidade",
                "valor_liberado": 0.00,
                "parcelas": 38,
                "valor_parcela": 299.30,
                "status": "pre_aprovada",
                "ativa": True,
            },
            "credito_pessoal": {
                "numero_proposta": "570013153",
                "tipo": "Credito Pessoal",
                "valor_liberado": 1400.00,
                "parcelas": 18,
                "valor_parcela": 299.31,
                "status": "pre_aprovada",
                "ativa": True,
                "requisitos": [
                    "Portabilidade do beneficio para a ConsigPro Financeira",
                    "Abertura de conta corrente na ConsigPro Financeira",
                    "Cadastro de transferencia automatica para receber valores no banco atual",
                ],
            },
        },
        "valor_total_pre_aprovado": 1400.00,
        "tarjeta_terminacion": "N/A",
        "tipo_tarjeta": "Portabilidade + Credito",
        "limite_credito": 1400.00,
        "limite_usado": 0.00,
        "tarjeta_status": "ativo",
        "ultima_interaccion": "2026-03-10",
        "margem_total": 1120.00,
        "margem_disponivel": 1400.00,
        "margem_cartao_disponivel": 0.00,
        "contratos_ativos": 0,
        "simulacao": {
            "margem_consignavel_35": 1120.00,
            "taxa_mensal": 1.80,
            "taxa_anual": 23.87,
            "cet_mensal": 1.95,
            "cet_anual": 26.08,
            "iof_percentual": 0.38,
            "iof_adicional_diario": 0.0082,
            "prazo_maximo_meses": 84,
            "sistema_amortizacao": "Tabela Price",
        },
    },

    # =========================================================================
    # CENARIO 3: Ana Beatriz - Refinanciamento (aliviar parcela)
    # =========================================================================
    "ana_beatriz_003": {
        "nome": "Ana Beatriz",
        "tempo_cliente": "5 anos e 1 mes",
        "dni": "345.678.901-22",
        "dni_ultimos_digitos": "1-22",
        "cpf": "345.678.901-22",
        "cpf_ultimos_digitos": "1-22",
        "email": "ana.b***@hotmail.com",
        "telefono": "+55 21 9**** 9012",
        "perfil": "pensionista_inss",
        "vinculo": "Pensionista INSS",
        "beneficio_inss": "****8845",
        "salario_bruto": 3800.00,
        "banco_atual": {
            "banco": "BRADESCO",
            "codigo_banco": "237",
            "agencia": "567",
            "conta": "****890-1",
        },
        "propostas_pre_aprovadas": {
            "refinanciamento": {
                "numero_proposta": "570013170",
                "tipo": "Refinanciamento",
                "valor_liberado": 5124.79,
                "parcelas": 84,
                "valor_parcela": 299.30,
                "status": "pre_aprovada",
                "ativa": True,
            },
        },
        "valor_total_pre_aprovado": 5124.79,
        "tarjeta_terminacion": "N/A",
        "tipo_tarjeta": "Refinanciamento",
        "limite_credito": 5124.79,
        "limite_usado": 0.00,
        "tarjeta_status": "ativo",
        "ultima_interaccion": "2026-03-10",
        "margem_total": 1330.00,
        "margem_disponivel": 5124.79,
        "margem_cartao_disponivel": 0.00,
        "contratos_ativos": 1,
        "simulacao": {
            "margem_consignavel_35": 1330.00,
            "taxa_mensal": 1.80,
            "taxa_anual": 23.87,
            "cet_mensal": 1.95,
            "cet_anual": 26.08,
            "iof_percentual": 0.38,
            "iof_adicional_diario": 0.0082,
            "prazo_maximo_meses": 84,
            "sistema_amortizacao": "Tabela Price",
        },
        "contrato_atual": {
            "numero": "CSG-2024-004567",
            "valor_emprestado": 18000.00,
            "parcela_mensal": 450.00,
            "parcelas_pagas": 12,
            "parcelas_totais": 60,
            "parcelas_restantes": 48,
            "saldo_devedor": 14500.00,
            "taxa_mensal": 2.10,
        },
    },

    # =========================================================================
    # CENARIO 4: Roberto Lima - Pacote Completo (4 propostas)
    # =========================================================================
    "roberto_lima_004": {
        "nome": "Roberto Lima",
        "tempo_cliente": "6 anos",
        "dni": "456.789.012-33",
        "dni_ultimos_digitos": "2-33",
        "cpf": "456.789.012-33",
        "cpf_ultimos_digitos": "2-33",
        "email": "roberto.l***@yahoo.com.br",
        "telefono": "+55 61 9**** 3456",
        "perfil": "aposentado_inss",
        "vinculo": "Aposentado INSS",
        "beneficio_inss": "****4512",
        "salario_bruto": 4500.00,
        "banco_atual": {
            "banco": "ITAU UNIBANCO",
            "codigo_banco": "341",
            "agencia": "8901",
            "conta": "****234-5",
        },
        "propostas_pre_aprovadas": {
            "emprestimo_consignado": {
                "numero_proposta": "570013180",
                "tipo": "Emprestimo Consignado INSS",
                "valor_liberado": 6456.29,
                "parcelas": 84,
                "valor_parcela": 150.55,
                "status": "pre_aprovada",
                "ativa": True,
            },
            "credito_pessoal": {
                "numero_proposta": "570013181",
                "tipo": "Credito Pessoal",
                "valor_liberado": 1400.00,
                "parcelas": 18,
                "valor_parcela": 299.31,
                "status": "pre_aprovada",
                "ativa": True,
                "requisitos": [
                    "Portabilidade do beneficio para a ConsigPro Financeira",
                    "Abertura de conta corrente na ConsigPro Financeira",
                    "Cadastro de transferencia automatica para receber valores no banco atual",
                ],
            },
            "portabilidade": {
                "numero_proposta": "570013182",
                "tipo": "Portabilidade",
                "valor_liberado": 0.00,
                "parcelas": 38,
                "valor_parcela": 299.30,
                "status": "pre_aprovada",
                "ativa": True,
            },
            "refinanciamento": {
                "numero_proposta": "570013183",
                "tipo": "Refinanciamento",
                "valor_liberado": 5124.79,
                "parcelas": 84,
                "valor_parcela": 299.30,
                "status": "pre_aprovada",
                "ativa": True,
            },
        },
        "valor_total_pre_aprovado": 12981.08,
        "tarjeta_terminacion": "N/A",
        "tipo_tarjeta": "Pacote Completo",
        "limite_credito": 12981.08,
        "limite_usado": 0.00,
        "tarjeta_status": "ativo",
        "ultima_interaccion": "2026-03-10",
        "margem_total": 1575.00,
        "margem_disponivel": 12981.08,
        "margem_cartao_disponivel": 0.00,
        "contratos_ativos": 0,
        "simulacao": {
            "margem_consignavel_35": 1575.00,
            "taxa_mensal": 1.80,
            "taxa_anual": 23.87,
            "cet_mensal": 1.95,
            "cet_anual": 26.08,
            "iof_percentual": 0.38,
            "iof_adicional_diario": 0.0082,
            "prazo_maximo_meses": 84,
            "sistema_amortizacao": "Tabela Price",
        },
    },

    # =========================================================================
    # CENARIO 5: Francisca Oliveira - Simulacao de Financiamento (sem proposta)
    # =========================================================================
    "francisca_oliveira_005": {
        "nome": "Francisca Oliveira",
        "tempo_cliente": "1 ano e 2 meses",
        "dni": "567.890.123-44",
        "dni_ultimos_digitos": "3-44",
        "cpf": "567.890.123-44",
        "cpf_ultimos_digitos": "3-44",
        "email": "francisca.o***@gmail.com",
        "telefono": "+55 85 9**** 7890",
        "perfil": "aposentada_inss",
        "vinculo": "Aposentada INSS",
        "beneficio_inss": "****9102",
        "salario_bruto": 3500.00,
        "banco_atual": {
            "banco": "BANCO DO NORDESTE",
            "codigo_banco": "4",
            "agencia": "456",
            "conta": "****678-9",
        },
        "propostas_pre_aprovadas": {},
        "valor_total_pre_aprovado": 0.00,
        "tarjeta_terminacion": "N/A",
        "tipo_tarjeta": "Simulacao",
        "limite_credito": 0.00,
        "limite_usado": 0.00,
        "tarjeta_status": "ativo",
        "ultima_interaccion": "2026-03-10",
        "margem_total": 1225.00,
        "margem_disponivel": 1225.00,
        "margem_cartao_disponivel": 0.00,
        "contratos_ativos": 0,
        "simulacao": {
            "margem_consignavel_35": 1225.00,
            "taxa_mensal": 1.80,
            "taxa_anual": 23.87,
            "cet_mensal": 1.95,
            "cet_anual": 26.08,
            "iof_percentual": 0.38,
            "iof_adicional_diario": 0.0082,
            "prazo_maximo_meses": 84,
            "sistema_amortizacao": "Tabela Price",
        },
    },
}

# =============================================================================
# TRANSACCIONES (proposals shown in right panel)
# =============================================================================

TRANSACCIONES = {
    # Maria Santos
    "prop_maria_001": {
        "cliente_id": "maria_santos_001",
        "valor": 8500.00,
        "nombre_comercio": "Proposta 570013160 - Emprestimo Consignado INSS",
        "categoria": "proposta_pre_aprovada",
        "fecha": "2026-03-10T00:00:00",
        "tipo": "emprestimo_consignado",
        "status": "pre_aprovada",
    },

    # Jose Carlos
    "prop_jose_001": {
        "cliente_id": "jose_carlos_002",
        "valor": 0.00,
        "nombre_comercio": "Proposta 570013155 - Portabilidade",
        "categoria": "proposta_pre_aprovada",
        "fecha": "2026-03-10T00:00:00",
        "tipo": "portabilidade",
        "status": "pre_aprovada",
    },
    "prop_jose_002": {
        "cliente_id": "jose_carlos_002",
        "valor": 1400.00,
        "nombre_comercio": "Proposta 570013153 - Credito Pessoal",
        "categoria": "proposta_pre_aprovada",
        "fecha": "2026-03-10T00:00:00",
        "tipo": "credito_pessoal",
        "status": "pre_aprovada",
    },

    # Ana Beatriz
    "prop_ana_001": {
        "cliente_id": "ana_beatriz_003",
        "valor": 5124.79,
        "nombre_comercio": "Proposta 570013170 - Refinanciamento",
        "categoria": "proposta_pre_aprovada",
        "fecha": "2026-03-10T00:00:00",
        "tipo": "refinanciamento",
        "status": "pre_aprovada",
    },

    # Roberto Lima
    "prop_roberto_001": {
        "cliente_id": "roberto_lima_004",
        "valor": 6456.29,
        "nombre_comercio": "Proposta 570013180 - Emprestimo Consignado INSS",
        "categoria": "proposta_pre_aprovada",
        "fecha": "2026-03-10T00:00:00",
        "tipo": "emprestimo_consignado",
        "status": "pre_aprovada",
    },
    "prop_roberto_002": {
        "cliente_id": "roberto_lima_004",
        "valor": 1400.00,
        "nombre_comercio": "Proposta 570013181 - Credito Pessoal",
        "categoria": "proposta_pre_aprovada",
        "fecha": "2026-03-10T00:00:00",
        "tipo": "credito_pessoal",
        "status": "pre_aprovada",
    },
    "prop_roberto_003": {
        "cliente_id": "roberto_lima_004",
        "valor": 0.00,
        "nombre_comercio": "Proposta 570013182 - Portabilidade",
        "categoria": "proposta_pre_aprovada",
        "fecha": "2026-03-10T00:00:00",
        "tipo": "portabilidade",
        "status": "pre_aprovada",
    },
    "prop_roberto_004": {
        "cliente_id": "roberto_lima_004",
        "valor": 5124.79,
        "nombre_comercio": "Proposta 570013183 - Refinanciamento",
        "categoria": "proposta_pre_aprovada",
        "fecha": "2026-03-10T00:00:00",
        "tipo": "refinanciamento",
        "status": "pre_aprovada",
    },
}

ESTADOS_CUENTA = {}
CLIENTES_CYMBALL = CLIENTES
