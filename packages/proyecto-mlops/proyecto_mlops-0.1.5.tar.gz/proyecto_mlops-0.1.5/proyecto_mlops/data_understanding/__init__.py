# -*- coding: utf-8 -*-
"""
FASE 2: DATA UNDERSTANDING
Exploración y comprensión de los datos.
"""

import os
import hashlib
import pandas as pd
import numpy as np
from typing import Dict, List
from collections import Counter
from ..utils import (
    ensure_dirs, save_json, load_json, logger,
    DATA_RAW_CSV, DATA_PROCESSED_DIR, DOCS_DIR, get_timestamp, REGISTRY_DATA_DIR
)


def load_raw_dataset(csv_path: str = DATA_RAW_CSV) -> pd.DataFrame:
    """Carga dataset crudo con validaciones básicas."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset no encontrado: {csv_path}")
    
    df = pd.read_csv(csv_path)
    logger.info(f"Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
    
    # Validaciones mínimas
    assert {"text", "label"}.issubset(df.columns), "Columnas esperadas (text, label) no encontradas"
    
    return df


def explore_data(df: pd.DataFrame) -> Dict:
    """Explora dataset y retorna reporte de características."""
    ensure_dirs(DATA_PROCESSED_DIR)
    
    report = {
        "timestamp": get_timestamp(),
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {col: int(df[col].isna().sum()) for col in df.columns},
        "text_stats": {
            "min_length": int(df["text"].astype(str).str.len().min()),
            "max_length": int(df["text"].astype(str).str.len().max()),
            "mean_length": float(df["text"].astype(str).str.len().mean()),
            "median_length": float(df["text"].astype(str).str.len().median()),
        },
        "label_distribution": {
            label: int(count) 
            for label, count in df["label"].value_counts().items()
        },
        "label_proportions": {
            label: float(prop)
            for label, prop in df["label"].value_counts(normalize=True).items()
        }
    }
    
    logger.info(f"[DATA_UNDERSTANDING] Datos explorados: {report['shape']}")
    return report


def save_data_exploration():
    """Ejecuta exploración y guarda reporte."""
    ensure_dirs(DATA_PROCESSED_DIR)
    
    df = load_raw_dataset()
    report = explore_data(df)
    
    path = os.path.join(DATA_PROCESSED_DIR, "data_exploration_report.json")
    save_json(report, path)
    logger.info(f"Reporte de exploración guardado: {path}")
    
    return report


def make_data_schema(df: pd.DataFrame, version: str = "1.0") -> Dict:
    """Crea esquema de datos (contrato)."""
    schema = {
        "version": version,
        "dataset_name": "news_classification_es",
        "timestamp": get_timestamp(),
        "columns": {
            "text": {
                "dtype": "string",
                "required": True,
                "min_length": 10,
                "description": "Documento de texto en español"
            },
            "label": {
                "dtype": "string",
                "required": True,
                "allowed": sorted(df["label"].astype(str).unique().tolist()),
                "description": "Categoría del documento"
            }
        },
        "allow_extra_columns": False
    }
    
    return schema


def save_data_schema():
    """Guarda esquema de datos."""
    df = load_raw_dataset()
    schema = make_data_schema(df)
    
    path = os.path.join(DOCS_DIR, "data_schema.json")
    save_json(schema, path)
    logger.info(f"Esquema de datos guardado: {path}")
    
    return schema


def validate_schema(df: pd.DataFrame, schema: Dict) -> Dict:
    """Valida un DataFrame contra un esquema."""
    report = {
        "timestamp": get_timestamp(),
        "total_rows": int(len(df)),
        "valid": True,
        "errors": []
    }
    
    # Verificar columnas
    expected_cols = set(schema["columns"].keys())
    present_cols = set(df.columns)
    missing = expected_cols - present_cols
    extra = present_cols - expected_cols
    
    if missing:
        report["errors"].append({"type": "missing_columns", "cols": sorted(missing)})
        report["valid"] = False
    
    if extra and not schema.get("allow_extra_columns", False):
        report["errors"].append({"type": "extra_columns", "cols": sorted(extra)})
        report["valid"] = False
    
    # Validar columna text
    if "text" in df:
        col_schema = schema["columns"]["text"]
        nulls = int(df["text"].isna().sum())
        if nulls > 0:
            report["errors"].append({"type": "text_nulls", "count": nulls})
            report["valid"] = False
        
        min_len = col_schema.get("min_length", 0)
        too_short = int((df["text"].astype(str).str.len() < min_len).sum())
        if too_short > 0:
            report["errors"].append({"type": "text_too_short", "count": too_short})
            report["valid"] = False
    
    # Validar columna label
    if "label" in df:
        col_schema = schema["columns"]["label"]
        allowed = set(col_schema.get("allowed", []))
        invalid_labels = df[~df["label"].astype(str).isin(allowed)]
        if len(invalid_labels) > 0:
            report["errors"].append({
                "type": "invalid_labels",
                "count": len(invalid_labels),
                "invalid_values": list(invalid_labels["label"].unique())
            })
            report["valid"] = False
    
    logger.info(f"[DATA_UNDERSTANDING] Validación: {report['valid']}")
    return report
