"""
Mock Data for Testing
=====================

This file contains sample customer and transaction data for testing the agent.
Modify this data to match your bank's test scenarios.

Note: BENEFICIOS_TARJETAS is imported from config.py (as CARD_TYPES).
"""

# Support both relative imports (when run as module) and absolute imports (when run directly)
try:
    from ...config import CARD_TYPES
except ImportError:
    from config import CARD_TYPES

# Alias for backward compatibility
BENEFICIOS_TARJETAS = CARD_TYPES

# =============================================================================
# CUSTOMERS (CLIENTES)
# =============================================================================

CLIENTES = {
    "roberto_garcia_001": {
        "nombre": "Roberto García",
        "tiempo_cliente": "3 años y 5 meses",
        "dni": "12345678A",
        "dni_ultimos_digitos": "78A",
        "email": "roberto.g***@gmail.com",
        "telefono": "+34 6** *** 890",
        "perfil": "buen_pagador",
        "tarjeta_terminacion": "4501",
        "tipo_tarjeta": "Visa Clásica",
        "limite_credito": 3000.00,
        "limite_usado": 1200.00,
        "saldo_pendiente": 150.00,
        "pago_minimo": 150.00,
        "fecha_limite_pago": "2026-01-25",
        "dias_mora": 5,
        "tarjeta_status": "activa",
        "cuenta_ahorro": "ES91 2100 1234 5678 9012 3456",
        "saldo_cuenta_ahorro": 850.00,
        "ultima_interaccion": "2026-01-20"
    },
    "carolina_martinez_002": {
        "nombre": "Carolina Martínez",
        "tiempo_cliente": "1 año y 2 meses",
        "dni": "23456789B",
        "dni_ultimos_digitos": "89B",
        "email": "carolina.m***@hotmail.com",
        "telefono": "+34 6** *** 654",
        "perfil": "cliente_nuevo",
        "tarjeta_terminacion": "8823",
        "tipo_tarjeta": "Visa Premium",
        "limite_credito": 5000.00,
        "limite_usado": 800.00,
        "saldo_pendiente": 0.00,
        "pago_minimo": 0.00,
        "fecha_limite_pago": "2026-02-10",
        "dias_mora": 0,
        "tarjeta_status": "activa",
        "puntos_programa": 2350,
        "puntos_por_caducar": 500,
        "fecha_caducidad_puntos": "2026-06-30",
        "ultima_interaccion": "2026-01-28",
        "promociones_activas": ["Pago Aplazado El Corte Inglés", "Pago Aplazado MediaMarkt", "Pago Aplazado Fnac"]
    },
    "javier_fernandez_003": {
        "nombre": "Javier Fernández",
        "tiempo_cliente": "5 años",
        "dni": "34567890C",
        "dni_ultimos_digitos": "90C",
        "pasaporte": "AAA123456",
        "email": "javier.f***@gmail.com",
        "telefono": "+34 6** *** 123",
        "perfil": "cliente_premium",
        "tarjeta_terminacion": "7710",
        "tipo_tarjeta": "Visa Platinum",
        "tarjeta_debito_terminacion": "3344",
        "limite_credito": 8000.00,
        "limite_usado": 2500.00,
        "saldo_pendiente": 0.00,
        "pago_minimo": 0.00,
        "tarjeta_status": "bloqueada_viaje",
        "pais_actual": "Portugal",
        "aviso_viaje": False,
        "fecha_regreso": None,
        "ultima_interaccion": "2026-01-30"
    },
    "maria_elena_lopez_004": {
        "nombre": "María Elena López",
        "tiempo_cliente": "2 años y 8 meses",
        "dni": "45678901D",
        "dni_ultimos_digitos": "01D",
        "email": "maria.e***@yahoo.es",
        "telefono": "+34 6** *** 456",
        "perfil": "buen_pagador",
        "tarjeta_terminacion": "5590",
        "tipo_tarjeta": "Mastercard Oro",
        "limite_credito": 4000.00,
        "limite_usado": 1500.00,
        "saldo_pendiente": 0.00,
        "pago_minimo": 0.00,
        "tarjeta_status": "activa",
        "suscripcion_netflix": 15.00,
        "ultima_interaccion": "2026-01-29"
    }
}

TRANSACCIONES = {
    # === ROBERTO GARCÍA - Cobros / Mora Temprana ===
    "txn_roberto_001": {
        "cliente_id": "roberto_garcia_001",
        "valor": 85.00,
        "nombre_comercio": "Mercadona",
        "categoria": "supermercado",
        "fecha": "2026-01-18T16:30:00",
        "tipo": "presencial",
        "status": "aprobada"
    },
    "txn_roberto_002": {
        "cliente_id": "roberto_garcia_001",
        "valor": 32.50,
        "nombre_comercio": "Farmacia Ortega",
        "categoria": "farmacia",
        "fecha": "2026-01-15T10:15:00",
        "tipo": "presencial",
        "status": "aprobada"
    },
    "txn_roberto_003": {
        "cliente_id": "roberto_garcia_001",
        "valor": 45.00,
        "nombre_comercio": "Repsol Gasolinera",
        "categoria": "combustible",
        "fecha": "2026-01-12T08:00:00",
        "tipo": "presencial",
        "status": "aprobada"
    },
    "txn_roberto_004": {
        "cliente_id": "roberto_garcia_001",
        "valor": 120.00,
        "nombre_comercio": "El Corte Inglés",
        "categoria": "tienda",
        "fecha": "2026-01-10T14:20:00",
        "tipo": "presencial",
        "status": "aprobada"
    },
    "txn_roberto_005": {
        "cliente_id": "roberto_garcia_001",
        "valor": 15.00,
        "nombre_comercio": "Netflix",
        "categoria": "streaming",
        "fecha": "2026-01-08T00:00:00",
        "tipo": "online",
        "status": "aprobada"
    },

    # === CAROLINA MARTÍNEZ - Beneficios / Puntos / Pago Aplazado ===
    "txn_carolina_001": {
        "cliente_id": "carolina_martinez_002",
        "valor": 125.00,
        "nombre_comercio": "El Corte Inglés",
        "categoria": "tienda",
        "fecha": "2026-01-25T11:00:00",
        "tipo": "presencial",
        "status": "aprobada",
        "puntos_generados": 125
    },
    "txn_carolina_002": {
        "cliente_id": "carolina_martinez_002",
        "valor": 45.00,
        "nombre_comercio": "Restaurante La Barraca",
        "categoria": "restaurante",
        "fecha": "2026-01-22T13:30:00",
        "tipo": "presencial",
        "status": "aprobada",
        "puntos_generados": 45
    },
    "txn_carolina_003": {
        "cliente_id": "carolina_martinez_002",
        "valor": 200.00,
        "nombre_comercio": "MediaMarkt",
        "categoria": "electrodomesticos",
        "fecha": "2026-01-18T15:45:00",
        "tipo": "presencial",
        "status": "aprobada",
        "pago_aplazado": True,
        "cuotas": 6,
        "puntos_generados": 0
    },
    "txn_carolina_004": {
        "cliente_id": "carolina_martinez_002",
        "valor": 65.00,
        "nombre_comercio": "Fnac",
        "categoria": "oficina",
        "fecha": "2026-01-14T10:00:00",
        "tipo": "presencial",
        "status": "aprobada",
        "puntos_generados": 65
    },
    "txn_carolina_005": {
        "cliente_id": "carolina_martinez_002",
        "valor": 12.99,
        "nombre_comercio": "Spotify",
        "categoria": "streaming",
        "fecha": "2026-01-10T00:00:00",
        "tipo": "online",
        "status": "aprobada",
        "puntos_generados": 12
    },

    # === JAVIER FERNÁNDEZ - Seguridad / Viaje ===
    "txn_javier_001": {
        "cliente_id": "javier_fernandez_003",
        "valor": 400.00,
        "nombre_comercio": "Hotel Pestana Lisboa",
        "categoria": "hotel",
        "fecha": "2026-01-30T14:00:00",
        "tipo": "presencial",
        "pais": "Portugal",
        "ciudad": "Lisboa",
        "status": "rechazada",
        "motivo_rechazo": "sin_aviso_viaje",
        "destaque": True
    },
    "txn_javier_002": {
        "cliente_id": "javier_fernandez_003",
        "valor": 85.00,
        "nombre_comercio": "TAP Air Portugal",
        "categoria": "aerolínea",
        "fecha": "2026-01-28T09:00:00",
        "tipo": "online",
        "status": "aprobada"
    },
    "txn_javier_003": {
        "cliente_id": "javier_fernandez_003",
        "valor": 250.00,
        "nombre_comercio": "El Corte Inglés",
        "categoria": "tienda",
        "fecha": "2026-01-20T16:00:00",
        "tipo": "presencial",
        "pais": "España",
        "status": "aprobada"
    },
    "txn_javier_004": {
        "cliente_id": "javier_fernandez_003",
        "valor": 120.00,
        "nombre_comercio": "Carrefour",
        "categoria": "supermercado",
        "fecha": "2026-01-15T17:30:00",
        "tipo": "presencial",
        "pais": "España",
        "status": "aprobada"
    },
    "txn_javier_005": {
        "cliente_id": "javier_fernandez_003",
        "valor": 55.00,
        "nombre_comercio": "Restaurante Casa Lucio",
        "categoria": "restaurante",
        "fecha": "2026-01-12T12:30:00",
        "tipo": "presencial",
        "pais": "España",
        "status": "aprobada"
    },

    # === MARÍA ELENA LÓPEZ - Reclamación / Cargo no reconocido ===
    "txn_maria_elena_001": {
        "cliente_id": "maria_elena_lopez_004",
        "valor": 85.00,
        "nombre_comercio": "Netflix",
        "categoria": "streaming",
        "fecha": "2026-01-29T03:15:00",
        "tipo": "online",
        "status": "aprobada",
        "cargo_no_reconocido": True,
        "destaque": True
    },
    "txn_maria_elena_002": {
        "cliente_id": "maria_elena_lopez_004",
        "valor": 15.00,
        "nombre_comercio": "Netflix",
        "categoria": "streaming",
        "fecha": "2026-01-05T00:00:00",
        "tipo": "online",
        "status": "aprobada",
        "cargo_regular": True
    },
    "txn_maria_elena_003": {
        "cliente_id": "maria_elena_lopez_004",
        "valor": 95.00,
        "nombre_comercio": "Mercadona",
        "categoria": "supermercado",
        "fecha": "2026-01-26T16:45:00",
        "tipo": "presencial",
        "status": "aprobada"
    },
    "txn_maria_elena_004": {
        "cliente_id": "maria_elena_lopez_004",
        "valor": 42.00,
        "nombre_comercio": "Farmacia Ortega",
        "categoria": "farmacia",
        "fecha": "2026-01-22T09:30:00",
        "tipo": "presencial",
        "status": "aprobada"
    },
    "txn_maria_elena_005": {
        "cliente_id": "maria_elena_lopez_004",
        "valor": 28.50,
        "nombre_comercio": "Telepizza",
        "categoria": "restaurante",
        "fecha": "2026-01-19T12:15:00",
        "tipo": "presencial",
        "status": "aprobada"
    }
}

ESTADOS_CUENTA = {
    "estado_roberto_001": {
        "cliente_id": "roberto_garcia_001",
        "periodo": "Enero 2026",
        "fecha_corte": "2026-01-20",
        "fecha_limite_pago": "2026-01-25",
        "saldo_anterior": 300.00,
        "pagos_realizados": 300.00,
        "compras_periodo": 297.50,
        "pago_minimo": 150.00,
        "pago_contado": 297.50,
        "dias_mora": 5,
        "recargo_mora": 7.50,
        "interes_mora_diario": 1.50,
        "status": "en_mora"
    }
}

# =============================================================================
# BACKWARD COMPATIBILITY ALIASES
# =============================================================================

# For backward compatibility with code that uses the old name
CLIENTES_CYMBALL = CLIENTES
