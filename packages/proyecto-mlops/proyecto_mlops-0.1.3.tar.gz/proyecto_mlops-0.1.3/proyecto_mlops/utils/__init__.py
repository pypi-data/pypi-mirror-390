# -*- coding: utf-8 -*-
"""
Utilidades compartidas para todas las fases del pipeline CRISP-DM.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Rutas por defecto
DATA_RAW_DIR = "data/raw"
DATA_PROCESSED_DIR = "data/processed"
MODELS_DIR = "models"
FIGURES_DIR = "figures"
DOCS_DIR = "docs"
REGISTRY_DATA_DIR = "data/registry"

# Constantes
DATA_RAW_CSV = os.path.join(DATA_RAW_DIR, "dataset.csv")
PROCESSED_PARQUET = os.path.join(DATA_PROCESSED_DIR, "preprocesado.parquet")
MODEL_REGISTRY = os.path.join(MODELS_DIR, "registry.json")
EXP_LOG = os.path.join(DATA_PROCESSED_DIR, "exp_log.jsonl")


def ensure_dirs(*dirs):
    """Crea directorios si no existen."""
    for d in dirs:
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
            logger.info(f"Directorio creado: {d}")


def save_json(obj: Any, path: str, **kwargs):
    """Guarda un objeto JSON."""
    ensure_dirs(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, **kwargs)
    logger.info(f"JSON guardado: {path}")


def load_json(path: str) -> Dict:
    """Carga un objeto JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def log_phase(phase_name: str, message: str):
    """Log estructurado para cada fase."""
    logger.info(f"[{phase_name.upper()}] {message}")


def get_timestamp() -> str:
    """Retorna timestamp en formato ISO."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
