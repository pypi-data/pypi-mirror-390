# -*- coding: utf-8 -*-
"""
FASE 5: EVALUATION
Evaluación de modelos.
"""

import os
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.metrics import (
    f1_score, accuracy_score, classification_report,
    confusion_matrix, precision_recall_curve, roc_curve, auc
)

from ..utils import ensure_dirs, save_json, logger, DATA_PROCESSED_DIR


def evaluate_model(
    pipe,
    X_test: List[str],
    y_test: List[str]
) -> Dict:
    """Evalúa modelo y retorna métricas detalladas."""
    logger.info("[EVALUATION] Evaluando modelo...")
    
    y_pred = pipe.predict(X_test)
    
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1_macro": float(f1_score(y_test, y_pred, average="macro")),
        "f1_weighted": float(f1_score(y_test, y_pred, average="weighted")),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=sorted(set(y_test))).tolist(),
        "labels": sorted(set(y_test))
    }
    
    logger.info(f"[EVALUATION] Accuracy: {metrics['accuracy']:.4f}, "
               f"F1-Macro: {metrics['f1_macro']:.4f}")
    
    return metrics


def measure_latency(
    pipe,
    sample_texts: List[str],
    n_repeats: int = 100
) -> Dict:
    """Mide latencia de predicción."""
    logger.info(f"[EVALUATION] Midiendo latencia ({n_repeats} predicciones)...")
    
    # Warm-up
    _ = pipe.predict([sample_texts[0]])
    
    latencies = []
    for _ in range(n_repeats):
        text = np.random.choice(sample_texts)
        t0 = time.perf_counter()
        _ = pipe.predict([text])
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)  # ms
    
    result = {
        "n_predictions": n_repeats,
        "latency_p50_ms": float(np.percentile(latencies, 50)),
        "latency_p95_ms": float(np.percentile(latencies, 95)),
        "latency_p99_ms": float(np.percentile(latencies, 99)),
        "latency_mean_ms": float(np.mean(latencies)),
        "latency_std_ms": float(np.std(latencies))
    }
    
    logger.info(f"[EVALUATION] Latencia P95: {result['latency_p95_ms']:.3f}ms")
    return result


def check_fairness(
    y_test: List[str],
    y_pred: List[str],
    min_f1_per_class: float = 0.70
) -> Dict:
    """Verifica fairness: F1 similar entre clases."""
    logger.info("[EVALUATION] Verificando fairness...")
    
    report = classification_report(y_test, y_pred, output_dict=True)
    
    f1_per_class = {}
    min_f1 = 1.0
    for label in sorted(set(y_test)):
        f1 = report.get(str(label), {}).get("f1-score", 0.0)
        f1_per_class[label] = f1
        min_f1 = min(min_f1, f1)
    
    is_fair = min_f1 >= min_f1_per_class
    logger.info(f"[EVALUATION] Min F1 per class: {min_f1:.4f}, "
               f"Fair: {is_fair} (threshold: {min_f1_per_class})")
    
    return {
        "f1_per_class": f1_per_class,
        "min_f1": float(min_f1),
        "is_fair": is_fair,
        "threshold": min_f1_per_class
    }


def full_evaluation(
    pipe,
    X_test: List[str],
    y_test: List[str],
    min_f1_per_class: float = 0.70
) -> Dict:
    """Ejecuta evaluación completa."""
    logger.info("[EVALUATION] Iniciando evaluación completa...")
    
    eval_metrics = evaluate_model(pipe, X_test, y_test)
    latency_metrics = measure_latency(pipe, X_test, n_repeats=100)
    fairness_metrics = check_fairness(y_test, pipe.predict(X_test), min_f1_per_class)
    
    result = {
        "model_metrics": eval_metrics,
        "latency_metrics": latency_metrics,
        "fairness_metrics": fairness_metrics,
        "overall_status": "PASSED" if fairness_metrics["is_fair"] else "FAILED"
    }
    
    logger.info(f"[EVALUATION] Status: {result['overall_status']}")
    return result


def save_evaluation_report(
    evaluation: Dict,
    output_path: str = None
) -> str:
    """Guarda reporte de evaluación."""
    ensure_dirs(DATA_PROCESSED_DIR)
    
    if output_path is None:
        output_path = os.path.join(DATA_PROCESSED_DIR, "evaluation_report.json")
    
    save_json(evaluation, output_path)
    logger.info(f"[EVALUATION] Reporte guardado: {output_path}")
    return output_path
