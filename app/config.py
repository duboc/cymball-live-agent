"""
Bank Agent Configuration
========================

This is the ONLY file you need to edit to customize this template for a new bank.
All bank-specific values are centralized here.

Instructions:
1. Copy this file or edit it directly
2. Change the values below to match your bank's requirements
3. Restart the application

For detailed documentation, see CUSTOMIZATION.md
"""

# =============================================================================
# BANK IDENTITY
# =============================================================================

BANK_NAME = "Cymball Bank"
BANK_COUNTRY = "España"
BANK_LANGUAGE = "es"  # es = Spanish, en = English, pt = Portuguese
BANK_CURRENCY = "EUR"
BANK_CURRENCY_SYMBOL = "€"

# Document types used for identification (localized)
BANK_ID_DOCUMENT = "DNI"  # DNI (Spain), CPF (Brazil), ID Card, Passport, etc.
BANK_ID_DOCUMENT_FULL = "Documento Nacional de Identidad"

# =============================================================================
# AGENT PERSONA
# =============================================================================

AGENT_NAME = "Laura"
AGENT_DESCRIPTION = f"Agente de Servicio al Cliente - {BANK_NAME}, {BANK_COUNTRY}"

# Voice configuration for Gemini Live
# Available voices: Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr
AGENT_VOICE = "Leda"  # Leda is good for Spanish

# =============================================================================
# BRAND COLORS
# =============================================================================

BRAND_COLORS = {
    "primary": "#0066CC",       # Main brand color
    "primary_dark": "#004C99",  # Darker shade
    "primary_light": "#3399FF", # Lighter shade
    "success": "#00A86B",       # Success/positive actions
    "warning": "#FFB800",       # Warnings
    "error": "#FF4444",         # Errors/negative actions
    "text": "#191919",          # Main text color
    "background": "#EFEFEF",    # Page background
    "card_background": "#FFFFFF", # Card/panel background
}

# =============================================================================
# CARD TYPES & BENEFITS
# =============================================================================

CARD_TYPES = {
    "visa_clasica": {
        "nombre": "Visa Clásica",
        "puntos_por_euro": 0,
        "pago_aplazado": True,
        "comercios_pago_aplazado": ["El Corte Inglés", "MediaMarkt", "Fnac", "Decathlon"],
        "plazos_pago_aplazado": [3, 6, 12],
        "seguro_viaje": False,
        "acceso_salas_vip": False
    },
    "visa_premium": {
        "nombre": "Visa Premium",
        "puntos_por_euro": 1,
        "pago_aplazado": True,
        "comercios_pago_aplazado": ["El Corte Inglés", "MediaMarkt", "Fnac", "Decathlon"],
        "plazos_pago_aplazado": [3, 6, 12],
        "pago_aplazado_genera_puntos": False,
        "compras_normales_generan_puntos": True,
        "seguro_viaje": True,
        "acceso_salas_vip": False,
        "nota": "Las compras con Pago Aplazado NO acumulan puntos. Solo compras de contado acumulan 1 punto por euro."
    },
    "visa_platinum": {
        "nombre": "Visa Platinum",
        "puntos_por_euro": 1.5,
        "pago_aplazado": True,
        "comercios_pago_aplazado": ["El Corte Inglés", "MediaMarkt", "Fnac", "Decathlon", "Leroy Merlin"],
        "plazos_pago_aplazado": [3, 6, 12, 18],
        "seguro_viaje": True,
        "acceso_salas_vip": True,
        "asistencia_internacional": True
    },
    "mastercard_oro": {
        "nombre": "Mastercard Oro",
        "puntos_por_euro": 0,
        "pago_aplazado": True,
        "comercios_pago_aplazado": ["El Corte Inglés", "MediaMarkt", "Fnac"],
        "plazos_pago_aplazado": [3, 6, 12],
        "seguro_viaje": True,
        "acceso_salas_vip": False
    }
}

# =============================================================================
# SCENARIOS (Customer Journeys)
# =============================================================================
# Define the test scenarios/journeys available in the UI

SCENARIOS = {
    "roberto_garcia_001": {
        "name": "Cobros (Mora Temprana)",
        "description": "Cliente con pago atrasado"
    },
    "carolina_martinez_002": {
        "name": "Beneficios (Puntos/Pago Aplazado)",
        "description": "Consulta sobre beneficios de tarjeta"
    },
    "javier_fernandez_003": {
        "name": "Seguridad (Viaje)",
        "description": "Tarjeta bloqueada en el extranjero"
    },
    "maria_elena_lopez_004": {
        "name": "Reclamación (Cargo no reconocido)",
        "description": "Disputa de cargo fraudulento"
    }
}

# =============================================================================
# UI TEXT (Localization)
# =============================================================================

UI_TEXT = {
    # Header
    "app_title": f"{BANK_NAME} - Servicio al Cliente IA",
    "context_header": "Contexto Cliente",
    "chat_status_connected": "Conectado",
    "chat_status_disconnected": "Desconectado",

    # Left panel
    "scenario_label": "Escenario de Prueba",
    "client_label": "Cliente",
    "available_limit_label": "Límite Disponible",
    "minimum_payment_label": "Pago Mínimo Pendiente",
    "customer_since_label": "Tiempo como Cliente",
    "card_status_label": "Estado Tarjeta",

    # Chat
    "typing_indicator": "El agente está escribiendo...",
    "input_placeholder": "Escriba su mensaje...",
    "send_button": "Enviar",
    "voice_button": "Voz",
    "stop_button": "Parar",
    "recording_indicator": "Grabando...",

    # Right panel
    "transactions_tab": "Transacciones",
    "logs_tab": "Logs",
    "loading_transactions": "Cargando transacciones...",
    "tool_logs_placeholder": "Las llamadas de herramientas aparecerán aquí...",

    # Help modal
    "help_title": "Cómo Probar los Escenarios",
    "help_step1": "Identificarse",
    "help_step2": "Describa el Problema",
    "help_step3": "Interactúe",
    "voice_tip": "Use el modo voz para una experiencia más realista.",
}

# =============================================================================
# OPERATIONAL SETTINGS
# =============================================================================

# Timeframes for operations (localized text)
TIMEFRAMES = {
    "card_replacement": "3 a 5 días hábiles",
    "claim_resolution": "30 a 45 días hábiles",
    "transaction_retry": "2 minutos",
}

# Payment channels available
PAYMENT_CHANNELS = ["App", "Banca online", "Sucursal"]

# Card delivery options
DELIVERY_OPTIONS = ["domicilio", "oficina", "sucursal"]
