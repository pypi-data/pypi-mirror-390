# -*- coding: utf-8 -*-
"""
FASE 6: DEPLOYMENT
Deployment y puesta en producción del modelo.
"""

import os
import json
from typing import Dict, Optional
from datetime import datetime

from ..utils import ensure_dirs, save_json, load_json, logger, MODELS_DIR, DATA_PROCESSED_DIR


MODEL_REGISTRY = os.path.join(MODELS_DIR, "registry.json")


def init_model_registry() -> Dict:
    """Inicializa registro de modelos."""
    return {
        "models": [],
        "current_production": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def register_model_in_registry(
    model_path: str,
    model_name: str,
    version: int,
    metrics: Dict,
    status: str = "candidate"
) -> Dict:
    """Registra modelo en el registro central."""
    ensure_dirs(MODELS_DIR)
    
    # Cargar registro existente
    if os.path.exists(MODEL_REGISTRY):
        registry = load_json(MODEL_REGISTRY)
        # Verificar si usa formato antiguo
        if "versions" in registry and "models" not in registry:
            # Migrar formato antiguo al nuevo
            old_versions = registry.get("versions", [])
            registry = {
                "models": [
                    {
                        "version": v["version"],
                        "name": model_name,
                        "path": v["path"],
                        "status": "archived",
                        "metrics": {},
                        "registered_at": v.get("created_at", "")
                    }
                    for v in old_versions
                ],
                "current_production": None,
                "created_at": registry.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            }
    else:
        registry = init_model_registry()
    
    entry = {
        "version": version,
        "name": model_name,
        "path": model_path,
        "status": status,  # "candidate" | "production" | "archived"
        "metrics": metrics,
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    registry["models"].append(entry)
    save_json(registry, MODEL_REGISTRY)
    
    logger.info(f"[DEPLOYMENT] Modelo registrado: {model_name} v{version}")
    return entry


def promote_to_production(
    version: int,
    registry_path: str = MODEL_REGISTRY
) -> Dict:
    """Promueve modelo a producción."""
    registry = load_json(registry_path)
    
    # Cambiar status previo a archived
    for model in registry["models"]:
        if model["status"] == "production":
            model["status"] = "archived"
            logger.info(f"[DEPLOYMENT] Modelo anterior archivado: v{model['version']}")
    
    # Promover a producción
    target = next((m for m in registry["models"] if m["version"] == version), None)
    if not target:
        raise ValueError(f"Modelo v{version} no encontrado")
    
    target["status"] = "production"
    target["promoted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registry["current_production"] = version
    
    save_json(registry, registry_path)
    logger.info(f"[DEPLOYMENT] Modelo promovido a producción: v{version}")
    
    return target


def get_production_model(registry_path: str = MODEL_REGISTRY) -> Optional[Dict]:
    """Retorna modelo en producción."""
    if not os.path.exists(registry_path):
        return None
    
    registry = load_json(registry_path)
    version = registry.get("current_production")
    
    if version is None:
        return None
    
    model = next((m for m in registry["models"] if m["version"] == version), None)
    return model


def create_deployment_package(
    model_path: str,
    output_dir: str = os.path.join(DATA_PROCESSED_DIR, "deployment_package")
) -> Dict:
    """Crea paquete de deployment con modelo y metadata."""
    ensure_dirs(output_dir)
    
    package = {
        "model_path": model_path,
        "package_created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": []
    }
    
    # Copiar modelo
    import shutil
    dst_model = os.path.join(output_dir, os.path.basename(model_path))
    shutil.copy2(model_path, dst_model)
    package["files"].append({
        "file": os.path.basename(model_path),
        "type": "model",
        "location": dst_model
    })
    
    # Guardar metadata
    metadata_path = os.path.join(output_dir, "metadata.json")
    save_json(package, metadata_path)
    package["files"].append({
        "file": "metadata.json",
        "type": "metadata",
        "location": metadata_path
    })
    
    logger.info(f"[DEPLOYMENT] Paquete de deployment creado: {output_dir}")
    return package


def generate_deployment_guide() -> Dict:
    """Genera guía de deployment."""
    guide = {
        "title": "Guía de Deployment - Clasificador de Documentos",
        "version": "1.0",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "steps": [
            {
                "numero": 1,
                "titulo": "Preparar entorno",
                "instrucciones": [
                    "Instalar Python 3.8+",
                    "Instalar dependencias: pip install -r requirements.txt",
                    "Configurar variables de entorno"
                ]
            },
            {
                "numero": 2,
                "titulo": "Cargar modelo",
                "instrucciones": [
                    "Descargar modelo de producción",
                    "Verificar integridad (checksum)",
                    "Cargar en memoria: joblib.load('modelo.joblib')"
                ]
            },
            {
                "numero": 3,
                "titulo": "Iniciar servicio",
                "instrucciones": [
                    "Ejecutar servidor (Flask/FastAPI)",
                    "Exponer endpoint /predict",
                    "Configurar healthcheck"
                ]
            },
            {
                "numero": 4,
                "titulo": "Monitoreo",
                "instrucciones": [
                    "Registrar predicciones (para drift detection)",
                    "Monitorear latencia",
                    "Monitorear tasa de errores"
                ]
            }
        ],
        "rollback_procedure": {
            "paso1": "Cambiar tráfico a versión anterior",
            "paso2": "Ejecutar smoke tests",
            "paso3": "Registrar incidente",
            "paso4": "Post-mortem"
        }
    }
    
    return guide


def save_deployment_guide() -> str:
    """Guarda guía de deployment."""
    ensure_dirs(DATA_PROCESSED_DIR)
    
    guide = generate_deployment_guide()
    path = os.path.join(DATA_PROCESSED_DIR, "deployment_guide.json")
    save_json(guide, path)
    
    logger.info(f"[DEPLOYMENT] Guía guardada: {path}")
    return path
