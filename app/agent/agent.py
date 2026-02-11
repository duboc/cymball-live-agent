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
        consultar_mora_tool,
        registrar_pago_prometido_tool,
        consultar_beneficios_tarjeta_tool,
        consultar_puntos_tool,
        consultar_disponible_tool,
        validar_identidad_tool,
        autorizar_transaccion_tool,
        registrar_aviso_viaje_tool,
        buscar_transacciones_recientes_tool,
        bloquear_tarjeta_tool,
        registrar_reclamacion_tool,
        solicitar_reposicion_tool,
        consultar_transaccion_tool
    )
except ImportError:
    from config import BANK_NAME, AGENT_DESCRIPTION
    from agent.tools.prompts import top_level_prompt
    from agent.tools.tools import (
        identificar_cliente_tool,
        consultar_historial_cliente_tool,
        consultar_mora_tool,
        registrar_pago_prometido_tool,
        consultar_beneficios_tarjeta_tool,
        consultar_puntos_tool,
        consultar_disponible_tool,
        validar_identidad_tool,
        autorizar_transaccion_tool,
        registrar_aviso_viaje_tool,
        buscar_transacciones_recientes_tool,
        bloquear_tarjeta_tool,
        registrar_reclamacion_tool,
        solicitar_reposicion_tool,
        consultar_transaccion_tool
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
        consultar_mora_tool,
        registrar_pago_prometido_tool,
        consultar_beneficios_tarjeta_tool,
        consultar_puntos_tool,
        consultar_disponible_tool,
        validar_identidad_tool,
        autorizar_transaccion_tool,
        registrar_aviso_viaje_tool,
        buscar_transacciones_recientes_tool,
        bloquear_tarjeta_tool,
        registrar_reclamacion_tool,
        solicitar_reposicion_tool,
        consultar_transaccion_tool
    ],
)

logger.info(f"Initialized {root_agent.name}")
