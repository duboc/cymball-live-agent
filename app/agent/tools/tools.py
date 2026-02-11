"""
Banking Agent Tools
===================

This file defines all the tools (functions) available to the agent.
Tools access mock data from mock_data.py and config from config.py.
"""

import logging
from typing import Dict, Any, List, Optional
from google.adk.tools import FunctionTool as Tool

# Support both relative imports (when run as module) and absolute imports (when run directly)
try:
    from ..data.mock_data import CLIENTES, TRANSACCIONES, ESTADOS_CUENTA, BENEFICIOS_TARJETAS
    from ...config import BANK_CURRENCY_SYMBOL, TIMEFRAMES
except ImportError:
    from agent.data.mock_data import CLIENTES, TRANSACCIONES, ESTADOS_CUENTA, BENEFICIOS_TARJETAS
    from config import BANK_CURRENCY_SYMBOL, TIMEFRAMES

logger = logging.getLogger(__name__)

#
# Helper Functions
#
def _get_cliente_by_dni_or_name(termino: str) -> Optional[str]:
    """Finds client ID by partial name or DNI digits."""
    termino = termino.lower().strip()
    for cid, data in CLIENTES.items():
        if termino in data["nombre"].lower() or termino in data["dni_ultimos_digitos"].lower():
            return cid
    return None

#
# Herramientas Generales
#

def identificar_cliente(termino_busca: str):
    """
    Busca un cliente por nombre o últimos dígitos del DNI para iniciar la atención.
    Retorna el perfil completo del cliente incluyendo el cliente_id para uso en otras herramientas.

    Args:
        termino_busca: Nombre parcial (ej: "Roberto", "Javier") o últimos dígitos del DNI (ej: "78A").

    Returns:
        Perfil del cliente con cliente_id. IMPORTANTE: Usa el cliente_id retornado
        para llamar las otras herramientas (consultar_mora, buscar_transacciones_recientes, etc).
    """
    cid = _get_cliente_by_dni_or_name(termino_busca)
    if cid:
        logger.info(f"Cliente identificado: {cid}")
        cliente_data = CLIENTES[cid].copy()
        cliente_data["cliente_id"] = cid
        return cliente_data
    return {"error": "Cliente no encontrado."}

identificar_cliente_tool = Tool(identificar_cliente)


def consultar_historial_cliente(cliente_id: str):
    """
    Retorna el historial y perfil del cliente (tiempo como cliente, productos, etc).

    Args:
        cliente_id: ID único del cliente (ej: "roberto_garcia_001").
    """
    if cliente_id in CLIENTES:
        return CLIENTES[cliente_id]
    return {"error": "Cliente no encontrado."}

consultar_historial_cliente_tool = Tool(consultar_historial_cliente)


#
# Escenario 1: Gestión de Cobros (Mora Temprana)
#

def consultar_mora(cliente_id: str):
    """
    Consulta el estado de mora del cliente: días de retraso, pago mínimo pendiente,
    recargos por mora y fecha límite de pago.

    Args:
        cliente_id: ID del cliente (ej: "roberto_garcia_001").
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente no encontrado."}

    # Buscar estado de cuenta
    for eid, estado in ESTADOS_CUENTA.items():
        if estado["cliente_id"] == cliente_id:
            return {
                "cliente": cliente["nombre"],
                "tarjeta_terminacion": cliente["tarjeta_terminacion"],
                "pago_minimo": estado["pago_minimo"],
                "fecha_limite_pago": estado["fecha_limite_pago"],
                "dias_mora": estado["dias_mora"],
                "recargo_mora": estado["recargo_mora"],
                "interes_mora_diario": estado["interes_mora_diario"],
                "status": estado["status"],
                "saldo_total": estado["pago_contado"]
            }

    # Si no hay estado de cuenta en mora
    if cliente.get("dias_mora", 0) > 0:
        return {
            "cliente": cliente["nombre"],
            "tarjeta_terminacion": cliente["tarjeta_terminacion"],
            "pago_minimo": cliente.get("pago_minimo", 0),
            "fecha_limite_pago": cliente.get("fecha_limite_pago", "N/A"),
            "dias_mora": cliente.get("dias_mora", 0),
            "status": "en_mora"
        }

    return {"status": "al_dia", "mensaje": "El cliente no tiene pagos en mora."}

consultar_mora_tool = Tool(consultar_mora)


def registrar_pago_prometido(cliente_id: str, monto: float, fecha_pago: str, canal_pago: str):
    """
    Registra en el sistema el compromiso de pago del cliente.

    Args:
        cliente_id: ID del cliente.
        monto: Importe que el cliente se compromete a pagar (ej: 150.00).
        fecha_pago: Fecha en que realizará el pago (ej: "2026-01-30" o "hoy").
        canal_pago: Canal por el que pagará (ej: "App", "Banca online", "Sucursal").
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente no encontrado."}

    return {
        "exito": True,
        "mensaje": f"Pago prometido registrado: {monto:.2f}{BANK_CURRENCY_SYMBOL} para {fecha_pago} vía {canal_pago}.",
        "nota_sistema": f"Se dejó nota en el sistema de que el pago del cliente {cliente['nombre']} quedará aplicado en la fecha indicada.",
        "numero_gestion": "COB-2026-4410"
    }

registrar_pago_prometido_tool = Tool(registrar_pago_prometido)


#
# Escenario 2: Consulta de Beneficios (Puntos y Pago Aplazado)
#

def consultar_beneficios_tarjeta(cliente_id: str):
    """
    Consulta los beneficios disponibles para la tarjeta del cliente:
    Pago Aplazado (comercios y plazos), puntos, seguros, etc.

    Args:
        cliente_id: ID del cliente.
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente no encontrado."}

    tipo_tarjeta = cliente.get("tipo_tarjeta", "").lower().replace(" ", "_")
    beneficios = BENEFICIOS_TARJETAS.get(tipo_tarjeta)

    if beneficios:
        resultado = beneficios.copy()
        resultado["tarjeta_cliente"] = cliente["tipo_tarjeta"]
        resultado["tarjeta_terminacion"] = cliente["tarjeta_terminacion"]
        if cliente.get("promociones_activas"):
            resultado["promociones_activas"] = cliente["promociones_activas"]
        return resultado

    return {
        "tarjeta_cliente": cliente.get("tipo_tarjeta", "N/A"),
        "mensaje": "Beneficios estándar disponibles.",
        "pago_aplazado": True,
        "comercios_pago_aplazado": ["El Corte Inglés", "MediaMarkt"],
        "plazos_pago_aplazado": [3, 6, 12]
    }

consultar_beneficios_tarjeta_tool = Tool(consultar_beneficios_tarjeta)


def consultar_puntos(cliente_id: str):
    """
    Consulta el balance de puntos del programa de fidelidad del cliente.

    Args:
        cliente_id: ID del cliente.
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente no encontrado."}

    puntos = cliente.get("puntos_programa", 0)
    if puntos > 0:
        return {
            "puntos_disponibles": puntos,
            "puntos_por_caducar": cliente.get("puntos_por_caducar", 0),
            "fecha_caducidad": cliente.get("fecha_caducidad_puntos", "N/A"),
            "tarjeta": cliente["tipo_tarjeta"]
        }

    return {
        "puntos_disponibles": 0,
        "mensaje": "Esta tarjeta no participa en el programa de puntos o no tiene puntos acumulados.",
        "tarjeta": cliente.get("tipo_tarjeta", "N/A")
    }

consultar_puntos_tool = Tool(consultar_puntos)


def consultar_disponible(cliente_id: str):
    """
    Consulta el límite de crédito disponible actual del cliente.

    Args:
        cliente_id: ID del cliente.
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente no encontrado."}

    limite = cliente.get("limite_credito", 0)
    usado = cliente.get("limite_usado", 0)
    disponible = limite - usado

    return {
        "limite_total": limite,
        "limite_usado": usado,
        "disponible": disponible,
        "tarjeta": cliente["tipo_tarjeta"],
        "tarjeta_terminacion": cliente["tarjeta_terminacion"]
    }

consultar_disponible_tool = Tool(consultar_disponible)


#
# Escenario 3: Seguridad / Desbloqueo por Viaje
#

def validar_identidad(cliente_id: str, metodo: str = "dni"):
    """
    Valida la identidad del cliente para operaciones de seguridad.

    Args:
        cliente_id: ID del cliente.
        metodo: Método de validación: 'dni', 'pasaporte', o 'preguntas_seguridad'.
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente no encontrado."}

    return {
        "exito": True,
        "metodo": metodo,
        "mensaje": f"Identidad del cliente {cliente['nombre']} validada correctamente.",
        "cliente_verificado": True
    }

validar_identidad_tool = Tool(validar_identidad)


def autorizar_transaccion(cliente_id: str, transaccion_id: str):
    """
    Autoriza una transacción específica que fue rechazada por el sistema de seguridad.

    Args:
        cliente_id: ID del cliente.
        transaccion_id: ID de la transacción rechazada.
    """
    txn = TRANSACCIONES.get(transaccion_id)
    if not txn:
        return {"error": "Transacción no encontrada."}

    return {
        "exito": True,
        "mensaje": f"Transacción en '{txn['nombre_comercio']}' por {txn['valor']:.2f}{BANK_CURRENCY_SYMBOL} autorizada exitosamente.",
        "nota": "El cliente puede intentar pasar la tarjeta nuevamente en 2 minutos."
    }

autorizar_transaccion_tool = Tool(autorizar_transaccion)


def registrar_aviso_viaje(cliente_id: str, pais_destino: str, fecha_regreso: str, incluir_debito: bool = False):
    """
    Registra un aviso de viaje para habilitar el uso de la tarjeta en el extranjero.

    Args:
        cliente_id: ID del cliente.
        pais_destino: País donde se encuentra o viajará (ej: "Portugal").
        fecha_regreso: Fecha de regreso (ej: "2026-02-05").
        incluir_debito: Si también se habilita la tarjeta de débito para uso internacional.
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente no encontrado."}

    resultado = {
        "exito": True,
        "mensaje": f"Tarjeta de crédito terminada en {cliente['tarjeta_terminacion']} habilitada para uso en {pais_destino} hasta {fecha_regreso}.",
        "tarjeta_credito": f"****{cliente['tarjeta_terminacion']} - Habilitada en {pais_destino}"
    }

    if incluir_debito and cliente.get("tarjeta_debito_terminacion"):
        resultado["tarjeta_debito"] = f"****{cliente['tarjeta_debito_terminacion']} - Habilitada en {pais_destino}"
        resultado["mensaje"] += f" Tarjeta de débito terminada en {cliente['tarjeta_debito_terminacion']} también habilitada."

    return resultado

registrar_aviso_viaje_tool = Tool(registrar_aviso_viaje)


#
# Escenario 4: Reclamación (Cargo no reconocido)
#

def buscar_transacciones_recientes(cliente_id: str):
    """
    Lista las transacciones recientes de un cliente.

    Args:
        cliente_id: ID del cliente.
    """
    resultado = []
    for tid, data in TRANSACCIONES.items():
        if data["cliente_id"] == cliente_id:
            txn_with_id = data.copy()
            txn_with_id["id"] = tid
            resultado.append(txn_with_id)
    return resultado

buscar_transacciones_recientes_tool = Tool(buscar_transacciones_recientes)


def bloquear_tarjeta(cliente_id: str, motivo: str):
    """
    Realiza el bloqueo preventivo de la tarjeta del cliente para evitar más cargos fraudulentos.

    Args:
        cliente_id: ID del cliente.
        motivo: Motivo del bloqueo (ej: "Cargo no reconocido", "Fraude", "Pérdida").
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente no encontrado."}

    return {
        "exito": True,
        "mensaje": f"Tarjeta terminada en {cliente['tarjeta_terminacion']} bloqueada preventivamente.",
        "motivo_registrado": motivo,
        "status_tarjeta": "BLOQUEADA",
        "nota": "No se realizarán más cargos a esta tarjeta hasta que se emita la reposición."
    }

bloquear_tarjeta_tool = Tool(bloquear_tarjeta)


def registrar_reclamacion(cliente_id: str, transaccion_id: str, descripcion: str):
    """
    Registra una reclamación formal por cargo no reconocido o fraude.
    Genera un número de caso para seguimiento.

    Args:
        cliente_id: ID del cliente.
        transaccion_id: ID de la transacción reclamada.
        descripcion: Descripción de la reclamación del cliente.
    """
    txn = TRANSACCIONES.get(transaccion_id)
    cliente = CLIENTES.get(cliente_id)

    if not txn:
        return {"error": "Transacción no encontrada."}
    if not cliente:
        return {"error": "Cliente no encontrado."}

    return {
        "exito": True,
        "numero_caso": "8892",
        "numero_gestion": "REC-2026-8892",
        "tipo_reclamacion": "cargo_no_reconocido",
        "importe_reclamado": txn["valor"],
        "comercio": txn["nombre_comercio"],
        "status": "EN_INVESTIGACION",
        "mensaje": f"Reclamación registrada exitosamente. Caso #{8892}.",
        "nota_cliente": f"El importe de {txn['valor']:.2f}{BANK_CURRENCY_SYMBOL} queda en disputa y no se le exigirá el pago de estos {txn['valor']:.2f}{BANK_CURRENCY_SYMBOL} hasta que se resuelva el caso.",
        "plazo_resolucion": "30 a 45 días hábiles"
    }

registrar_reclamacion_tool = Tool(registrar_reclamacion)


def solicitar_reposicion(cliente_id: str, destino_entrega: str):
    """
    Solicita la reposición (nueva tarjeta) después de un bloqueo.

    Args:
        cliente_id: ID del cliente.
        destino_entrega: Donde entregar la nueva tarjeta: "domicilio", "oficina" o nombre de sucursal.
    """
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        return {"error": "Cliente no encontrado."}

    return {
        "exito": True,
        "plazo": "3 a 5 días hábiles",
        "destino_entrega": destino_entrega,
        "tipo_tarjeta": cliente.get("tipo_tarjeta", "N/A"),
        "mensaje": f"Se generó la reposición de su tarjeta {cliente.get('tipo_tarjeta', '')}. Llegará a {destino_entrega} en 3 a 5 días hábiles."
    }

solicitar_reposicion_tool = Tool(solicitar_reposicion)


def consultar_transaccion(transaccion_id: str):
    """
    Busca los detalles de una transacción específica por su ID.

    Args:
        transaccion_id: ID de la transacción (ej: "txn_javier_001").
    """
    if transaccion_id in TRANSACCIONES:
        return TRANSACCIONES[transaccion_id]
    return {"error": "Transacción no encontrada."}

consultar_transaccion_tool = Tool(consultar_transaccion)
