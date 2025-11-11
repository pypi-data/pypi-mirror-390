# -*- coding: utf-8 -*-
"""
FASE 1: BUSINESS UNDERSTANDING
Comprensión del negocio y definición de objetivos.
"""

import os
from typing import Dict
from ..utils import save_json, load_json, logger, DOCS_DIR, get_timestamp


def define_business_objectives() -> Dict:
    """
    Define los objetivos de negocio y técnicos del proyecto.
    """
    objectives = {
        "timestamp": get_timestamp(),
        "business_objective": {
            "titulo": "Sistema de Clasificación de Documentos en Español",
            "descripcion": "Desarrollar un modelo de ML que clasifique automáticamente documentos de texto en español en categorías predefinidas, mejorando la eficiencia operativa y reduciendo errores manuales.",
            "beneficios": [
                "Automatización de clasificación manual",
                "Reducción de tiempo de procesamiento (20-30%)",
                "Mejora de consistencia en categorización",
                "Escalabilidad a volúmenes más grandes"
            ],
            "stakeholders": [
                "Equipo de operaciones",
                "Equipo técnico",
                "Dirección ejecutiva"
            ]
        },
        "ml_objective": {
            "tipo": "Clasificación multiclase supervisada",
            "target_variable": "label (categoría del documento)",
            "features": "Texto en español (variable length)",
            "métricas_éxito": {
                "f1_macro_min": 0.75,
                "f1_por_clase_min": 0.70,
                "accuracy_min": 0.80
            }
        },
        "constraints": {
            "latencia_max_ms": 200,
            "throughput_minimo": "100 docs/segundo",
            "disponibilidad": "99.5%",
            "privacidad": "GDPR compliant"
        },
        "timeline": {
            "inicio": get_timestamp(),
            "fases_semanas": {
                "data_understanding": 1,
                "data_preparation": 1,
                "modeling": 2,
                "evaluation": 1,
                "deployment": 1
            }
        }
    }
    
    logger.info("[BUSINESS_UNDERSTANDING] Objetivos de negocio definidos")
    return objectives


def save_business_document():
    """Guarda documento de comprensión del negocio."""
    obj = define_business_objectives()
    path = os.path.join(DOCS_DIR, "business_understanding.json")
    save_json(obj, path)
    logger.info(f"Documento guardado: {path}")
    return obj


def load_business_document(path: str = None) -> Dict:
    """Carga documento de comprensión del negocio."""
    if path is None:
        path = os.path.join(DOCS_DIR, "business_understanding.json")
    return load_json(path)
