"""
Root Agent Configuration
========================

This file creates the main agent using configuration from config.py.
"""

import logging
from google.adk.agents import Agent

# Support both relative imports (when run as module) and absolute imports (when run directly)
try:
    from ..config import BANK_NAME, AGENT_DESCRIPTION
    from .tools.prompts import top_level_prompt
    from .tools.tools import (
        identificar_cliente_tool,
        consultar_historial_cliente_tool,
        listar_propostas_tool,
        detalhar_proposta_tool,
        remover_proposta_tool,
        contratar_propostas_tool,
        consultar_valor_total_tool,
        buscar_transacciones_recientes_tool,
        consultar_transaccion_tool,
        simular_emprestimo_tool,
    )
except ImportError:
    from config import BANK_NAME, AGENT_DESCRIPTION
    from agent.tools.prompts import top_level_prompt
    from agent.tools.tools import (
        identificar_cliente_tool,
        consultar_historial_cliente_tool,
        listar_propostas_tool,
        detalhar_proposta_tool,
        remover_proposta_tool,
        contratar_propostas_tool,
        consultar_valor_total_tool,
        buscar_transacciones_recientes_tool,
        consultar_transaccion_tool,
        simular_emprestimo_tool,
    )

logger = logging.getLogger(__name__)

# Create agent name from bank name (remove spaces and special chars)
agent_name = BANK_NAME.replace(" ", "").replace("-", "")

root_agent = Agent(
    model="gemini-live-2.5-flash-native-audio",
    name=agent_name,
    description=AGENT_DESCRIPTION,
    instruction=top_level_prompt,
    tools=[
        identificar_cliente_tool,
        consultar_historial_cliente_tool,
        listar_propostas_tool,
        detalhar_proposta_tool,
        remover_proposta_tool,
        contratar_propostas_tool,
        consultar_valor_total_tool,
        buscar_transacciones_recientes_tool,
        consultar_transaccion_tool,
        simular_emprestimo_tool,
    ],
)

logger.info(f"Initialized {root_agent.name}")
