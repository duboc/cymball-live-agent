"""
ConsigPro Agent Tools - Propostas Pre-Aprovadas
=================================================

Tools for presenting, explaining, and managing pre-approved proposals.
"""

import logging
from typing import Optional
from google.adk.tools import FunctionTool as Tool

# Support both relative imports (when run as module) and absolute imports (when run directly)
try:
    from ..data.mock_data import CLIENTES, TRANSACCIONES, ESTADOS_CUENTA, BENEFICIOS_TARJETAS
    from ...config import BANK_CURRENCY_SYMBOL, TIMEFRAMES, BANK_NAME
except ImportError:
    from agent.data.mock_data import CLIENTES, TRANSACCIONES, ESTADOS_CUENTA, BENEFICIOS_TARJETAS
    from config import BANK_CURRENCY_SYMBOL, TIMEFRAMES, BANK_NAME

logger = logging.getLogger(__name__)

#
# Helper Functions
#
def _get_cliente_by_dni_or_name(termino: str) -> Optional[str]:
    """Finds client ID by partial name or CPF digits."""
    termino = termino.lower().strip()
    for cid, data in CLIENTES.items():
        if data is None:
            continue
        if termino in data["nome"].lower() or termino in data["dni_ultimos_digitos"].lower():
            return cid
    return None


def _get_propostas_ativas(cliente_id: str) -> dict:
    """Returns only active proposals for a client."""
    # Always resolve to the base client
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {}
    propostas = cliente.get("propostas_pre_aprovadas", {})
    return {k: v for k, v in propostas.items() if v.get("ativa", True)}


def _calcular_valor_total(propostas_ativas: dict) -> float:
    """Calculates total available value from active proposals."""
    return sum(p.get("valor_liberado", 0) for p in propostas_ativas.values())


#
# Tool 1: Identificar Cliente
#

def identificar_cliente(termino_busca: str):
    """
    Busca um cliente por nome ou ultimos digitos do CPF para iniciar o atendimento.
    Retorna o perfil do cliente incluindo o cliente_id e o resumo das propostas pre-aprovadas.

    Args:
        termino_busca: Nome parcial (ex: "Jose", "Carlos") ou ultimos digitos do CPF (ex: "0-11").

    Returns:
        Perfil do cliente com cliente_id e resumo de propostas.
        IMPORTANTE: Use o cliente_id retornado para chamar as outras ferramentas.
    """
    cid = _get_cliente_by_dni_or_name(termino_busca)
    if cid:
        logger.info(f"Cliente identificado: {cid}")
        cliente_data = CLIENTES[cid].copy()
        cliente_data["cliente_id"] = cid

        # Adicionar resumo das propostas
        propostas_ativas = _get_propostas_ativas(cid)
        valor_total = _calcular_valor_total(propostas_ativas)
        cliente_data["resumo_propostas"] = {
            "quantidade_propostas": len(propostas_ativas),
            "valor_total_disponivel": round(valor_total, 2),
            "propostas": list(propostas_ativas.keys()),
        }
        return cliente_data
    return {"error": "Cliente nao encontrado."}

identificar_cliente_tool = Tool(identificar_cliente)


#
# Tool 2: Listar Propostas Pre-Aprovadas
#

def listar_propostas(cliente_id: str):
    """
    Lista todas as propostas pre-aprovadas ativas do cliente com valores,
    parcelas e numeros de proposta. Mostra tambem o valor total disponivel.

    Args:
        cliente_id: ID do cliente (ex: "jose_carlos_001").
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente nao encontrado."}

    propostas_ativas = _get_propostas_ativas(cliente_id)
    valor_total = _calcular_valor_total(propostas_ativas)

    lista = []
    for key, prop in propostas_ativas.items():
        item = {
            "id": key,
            "numero_proposta": prop["numero_proposta"],
            "tipo": prop["tipo"],
            "valor_liberado": prop["valor_liberado"],
            "parcelas": prop["parcelas"],
            "valor_parcela": prop["valor_parcela"],
        }
        if "requisitos" in prop:
            item["requisitos"] = prop["requisitos"]
        lista.append(item)

    return {
        "cliente": cliente["nome"],
        "propostas": lista,
        "quantidade": len(lista),
        "valor_total_disponivel": round(valor_total, 2),
        "nota": "Todas as propostas podem ser contratadas ao mesmo tempo.",
    }

listar_propostas_tool = Tool(listar_propostas)


#
# Tool 3: Detalhar Proposta Especifica
#

def detalhar_proposta(cliente_id: str, tipo_proposta: str):
    """
    Mostra detalhes completos de uma proposta pre-aprovada especifica,
    incluindo requisitos e condicoes.

    Args:
        cliente_id: ID do cliente.
        tipo_proposta: Tipo da proposta: "emprestimo_consignado", "credito_pessoal",
                       "portabilidade" ou "refinanciamento".
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente nao encontrado."}

    propostas = cliente.get("propostas_pre_aprovadas", {})
    proposta = propostas.get(tipo_proposta)

    if not proposta:
        return {"error": f"Proposta '{tipo_proposta}' nao encontrada."}

    if not proposta.get("ativa", True):
        return {"error": "Esta proposta foi removida pelo cliente."}

    resultado = {
        "numero_proposta": proposta["numero_proposta"],
        "tipo": proposta["tipo"],
        "valor_liberado": proposta["valor_liberado"],
        "parcelas": proposta["parcelas"],
        "valor_parcela": proposta["valor_parcela"],
        "status": proposta["status"],
    }

    # Adicionar detalhes especificos por tipo
    if tipo_proposta == "portabilidade":
        resultado["explicacao"] = (
            "A Portabilidade nao libera valor adicional, mas transfere seu contrato "
            "de outro banco para a ConsigPro Financeira com condicoes melhores. "
            "Isso pode aliviar seu orcamento mensal com parcelas menores."
        )
    elif tipo_proposta == "refinanciamento":
        resultado["explicacao"] = (
            f"O Refinanciamento libera R${proposta['valor_liberado']:.2f} na sua conta, "
            f"com parcelas de R${proposta['valor_parcela']:.2f} por {proposta['parcelas']} meses. "
            "E a renegociacao do seu contrato existente com liberacao de valor extra."
        )
    elif tipo_proposta == "emprestimo_consignado":
        resultado["explicacao"] = (
            f"O Emprestimo Consignado INSS libera R${proposta['valor_liberado']:.2f} na sua conta, "
            f"com parcelas de R${proposta['valor_parcela']:.2f} descontadas diretamente do beneficio INSS "
            f"por {proposta['parcelas']} meses."
        )
    elif tipo_proposta == "credito_pessoal":
        resultado["explicacao"] = (
            f"O Credito Pessoal libera R${proposta['valor_liberado']:.2f} na sua conta, "
            f"com parcelas de R${proposta['valor_parcela']:.2f} por {proposta['parcelas']} meses."
        )
        if "requisitos" in proposta:
            resultado["requisitos"] = proposta["requisitos"]
            resultado["info_conta_atual"] = {
                "banco": cliente.get("banco_atual", {}).get("banco", "N/A"),
                "agencia": cliente.get("banco_atual", {}).get("agencia", "N/A"),
                "conta": cliente.get("banco_atual", {}).get("conta", "N/A"),
                "beneficio": cliente.get("beneficio_inss", "N/A"),
            }
            resultado["nota_requisitos"] = (
                "Para contratar o Credito Pessoal, e necessario fazer a Portabilidade "
                "do beneficio para a ConsigPro Financeira e abrir conta corrente com "
                "cadastro de transferencia automatica para continuar recebendo no banco atual."
            )

    return resultado

detalhar_proposta_tool = Tool(detalhar_proposta)


#
# Tool 4: Remover Proposta
#

def remover_proposta(cliente_id: str, tipo_proposta: str):
    """
    Remove uma proposta pre-aprovada da lista do cliente.
    O valor total disponivel sera recalculado sem esta proposta.

    Args:
        cliente_id: ID do cliente.
        tipo_proposta: Tipo da proposta a remover: "emprestimo_consignado",
                       "credito_pessoal", "portabilidade" ou "refinanciamento".
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente nao encontrado."}

    propostas = cliente.get("propostas_pre_aprovadas", {})
    proposta = propostas.get(tipo_proposta)

    if not proposta:
        return {"error": f"Proposta '{tipo_proposta}' nao encontrada."}

    if not proposta.get("ativa", True):
        return {"error": "Esta proposta ja foi removida."}

    # Marcar como inativa
    proposta["ativa"] = False
    proposta["status"] = "removida_pelo_cliente"

    # Recalcular valor total
    propostas_ativas = _get_propostas_ativas(cliente_id)
    novo_total = _calcular_valor_total(propostas_ativas)

    return {
        "sucesso": True,
        "proposta_removida": proposta["tipo"],
        "numero_proposta": proposta["numero_proposta"],
        "valor_removido": proposta["valor_liberado"],
        "propostas_restantes": len(propostas_ativas),
        "novo_valor_total": round(novo_total, 2),
        "mensagem": (
            f"Proposta de {proposta['tipo']} (n. {proposta['numero_proposta']}) removida. "
            f"Valor total disponivel agora: R${novo_total:.2f}."
        ),
    }

remover_proposta_tool = Tool(remover_proposta)


#
# Tool 5: Contratar Propostas
#

def contratar_propostas(cliente_id: str, propostas_selecionadas: list):
    """
    Contrata uma ou mais propostas pre-aprovadas. Pode contratar todas de uma vez
    ou apenas as selecionadas pelo cliente.

    Args:
        cliente_id: ID do cliente.
        propostas_selecionadas: Lista com os tipos de proposta a contratar.
            Ex: ["emprestimo_consignado", "refinanciamento"]
            Opcoes: "emprestimo_consignado", "credito_pessoal", "portabilidade", "refinanciamento"
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente nao encontrado."}

    propostas = cliente.get("propostas_pre_aprovadas", {})
    contratadas = []
    erros = []
    valor_total_contratado = 0

    for tipo in propostas_selecionadas:
        prop = propostas.get(tipo)
        if not prop:
            erros.append(f"Proposta '{tipo}' nao encontrada.")
            continue
        if not prop.get("ativa", True):
            erros.append(f"Proposta '{tipo}' foi removida e nao pode ser contratada.")
            continue

        # Verificar requisitos do credito pessoal
        if tipo == "credito_pessoal" and "portabilidade" not in propostas_selecionadas:
            port_prop = propostas.get("portabilidade", {})
            if port_prop.get("status") != "contratada":
                erros.append(
                    "Credito Pessoal requer a Portabilidade do beneficio. "
                    "Inclua 'portabilidade' na lista ou contrate-a primeiro."
                )
                continue

        contratadas.append({
            "tipo": prop["tipo"],
            "numero_proposta": prop["numero_proposta"],
            "valor_liberado": prop["valor_liberado"],
            "parcelas": prop["parcelas"],
            "valor_parcela": prop["valor_parcela"],
        })
        prop["status"] = "contratada"
        valor_total_contratado += prop["valor_liberado"]

    if not contratadas and erros:
        return {"sucesso": False, "erros": erros}

    resultado = {
        "sucesso": True,
        "contratadas": contratadas,
        "quantidade_contratada": len(contratadas),
        "valor_total_liberado": round(valor_total_contratado, 2),
        "prazo_liberacao": TIMEFRAMES["proposta_aprovacao"],
    }

    if erros:
        resultado["avisos"] = erros

    resultado["mensagem"] = (
        f"Parabens! {len(contratadas)} proposta(s) contratada(s) com sucesso! "
        f"Valor total a ser liberado: R${valor_total_contratado:.2f}. "
        f"Prazo para liberacao: {TIMEFRAMES['proposta_aprovacao']}."
    )

    return resultado

contratar_propostas_tool = Tool(contratar_propostas)


#
# Tool 6: Consultar Valor Total Disponivel
#

def consultar_valor_total(cliente_id: str):
    """
    Consulta o valor total disponivel considerando apenas as propostas ativas (nao removidas).
    Mostra resumo de cada proposta e o total.

    Args:
        cliente_id: ID do cliente.
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente nao encontrado."}

    propostas_ativas = _get_propostas_ativas(cliente_id)
    valor_total = _calcular_valor_total(propostas_ativas)

    resumo = []
    for key, prop in propostas_ativas.items():
        resumo.append({
            "tipo": prop["tipo"],
            "valor_liberado": prop["valor_liberado"],
            "parcelas": f"{prop['parcelas']}x R${prop['valor_parcela']:.2f}",
        })

    return {
        "cliente": cliente["nome"],
        "propostas_ativas": resumo,
        "quantidade": len(propostas_ativas),
        "valor_total_disponivel": round(valor_total, 2),
    }

consultar_valor_total_tool = Tool(consultar_valor_total)


#
# Tool 7: Consultar Historial (backward compat)
#

def consultar_historial_cliente(cliente_id: str):
    """
    Retorna o historico e perfil do cliente (tempo como cliente, vinculo, banco atual, etc).

    Args:
        cliente_id: ID unico do cliente (ex: "jose_carlos_001").
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente nao encontrado."}
    return cliente

consultar_historial_cliente_tool = Tool(consultar_historial_cliente)


#
# Tools Auxiliares (backward compat)
#

def buscar_transacciones_recientes(cliente_id: str):
    """
    Lista as propostas e movimentacoes recentes de um cliente.

    Args:
        cliente_id: ID do cliente.
    """
    # Resolve to base client ID for transactions
    base_id = "jose_carlos_001" if "jose_carlos" in cliente_id else cliente_id
    resultado = []
    for tid, data in TRANSACCIONES.items():
        if data["cliente_id"] == base_id:
            txn_with_id = data.copy()
            txn_with_id["id"] = tid
            resultado.append(txn_with_id)
    return resultado

buscar_transacciones_recientes_tool = Tool(buscar_transacciones_recientes)


def simular_emprestimo(cliente_id: str, valor_desejado: float, prazo_meses: int):
    """
    Simula um novo emprestimo consignado para o cliente, calculando parcela mensal,
    taxa mensal, taxa anual, CET, IOF e valor total pago usando a Tabela Price.
    Verifica se a parcela cabe na margem consignavel do cliente.

    Args:
        cliente_id: ID do cliente.
        valor_desejado: Valor do emprestimo desejado em reais (ex: 10000.00).
        prazo_meses: Prazo em meses (ex: 48, 60, 72, 84). Maximo 84 meses.
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente nao encontrado."}

    sim = cliente.get("simulacao")
    if not sim:
        return {"error": "Cliente nao possui parametros de simulacao configurados."}

    if prazo_meses < 6 or prazo_meses > sim["prazo_maximo_meses"]:
        return {"error": f"Prazo deve ser entre 6 e {sim['prazo_maximo_meses']} meses."}

    if valor_desejado <= 0:
        return {"error": "Valor do emprestimo deve ser positivo."}

    taxa_mensal = sim["taxa_mensal"] / 100
    cet_mensal = sim["cet_mensal"] / 100

    # Tabela Price: PMT = PV * [i * (1+i)^n] / [(1+i)^n - 1]
    fator = (1 + taxa_mensal) ** prazo_meses
    parcela_mensal = valor_desejado * (taxa_mensal * fator) / (fator - 1)
    valor_total_pago = parcela_mensal * prazo_meses
    juros_totais = valor_total_pago - valor_desejado

    # CET calculation (parcela com CET)
    fator_cet = (1 + cet_mensal) ** prazo_meses
    parcela_cet = valor_desejado * (cet_mensal * fator_cet) / (fator_cet - 1)
    valor_total_cet = parcela_cet * prazo_meses

    # IOF estimado
    iof_base = valor_desejado * (sim["iof_percentual"] / 100)
    iof_adicional = valor_desejado * (sim["iof_adicional_diario"] / 100) * min(prazo_meses * 30, 365)
    iof_total = iof_base + iof_adicional

    margem = sim["margem_consignavel_35"]
    cabe_na_margem = parcela_mensal <= margem

    resultado = {
        "cliente": cliente["nome"],
        "valor_emprestimo": round(valor_desejado, 2),
        "prazo_meses": prazo_meses,
        "sistema_amortizacao": sim["sistema_amortizacao"],
        "taxa_mensal": f"{sim['taxa_mensal']}% a.m.",
        "taxa_anual": f"{sim['taxa_anual']}% a.a.",
        "parcela_mensal": round(parcela_mensal, 2),
        "valor_total_pago": round(valor_total_pago, 2),
        "juros_totais": round(juros_totais, 2),
        "cet_mensal": f"{sim['cet_mensal']}% a.m.",
        "cet_anual": f"{sim['cet_anual']}% a.a.",
        "parcela_com_cet": round(parcela_cet, 2),
        "valor_total_com_cet": round(valor_total_cet, 2),
        "iof_estimado": round(iof_total, 2),
        "margem_consignavel": round(margem, 2),
        "parcela_cabe_na_margem": cabe_na_margem,
    }

    if cabe_na_margem:
        resultado["margem_restante"] = round(margem - parcela_mensal, 2)
        resultado["mensagem"] = (
            f"Simulacao aprovada! A parcela de R${parcela_mensal:.2f} cabe na sua margem "
            f"consignavel de R${margem:.2f}. Sobram R${margem - parcela_mensal:.2f} de margem."
        )
    else:
        # Calcular valor maximo que cabe na margem
        fator_max = (1 + taxa_mensal) ** prazo_meses
        valor_maximo = margem * (fator_max - 1) / (taxa_mensal * fator_max)
        resultado["valor_maximo_na_margem"] = round(valor_maximo, 2)
        resultado["mensagem"] = (
            f"A parcela de R${parcela_mensal:.2f} ultrapassa sua margem consignavel "
            f"de R${margem:.2f}. O valor maximo para {prazo_meses} meses seria "
            f"R${valor_maximo:.2f}."
        )

    return resultado

simular_emprestimo_tool = Tool(simular_emprestimo)


def consultar_transaccion(transaccion_id: str):
    """
    Busca os detalhes de uma movimentacao especifica por seu ID.

    Args:
        transaccion_id: ID da movimentacao (ex: "prop_emp_001").
    """
    if transaccion_id in TRANSACCIONES:
        return TRANSACCIONES[transaccion_id]
    return {"error": "Movimentacao nao encontrada."}

consultar_transaccion_tool = Tool(consultar_transaccion)
