#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PROYECTO-MLOPS: CLI Principal
Herramienta de línea de comandos para el pipeline MLOps completo
"""

from typing import Optional

import pandas as pd
import typer

# Import fases CRISP-DM
from proyecto_mlops.business_understanding import save_business_document
from proyecto_mlops.data_understanding import (
    load_raw_dataset,
    explore_data,
    save_data_schema,
)
from proyecto_mlops.data_preparation import prepare_data_pipeline
from proyecto_mlops.modeling import (
    train_model,
    cross_validate_model,
    save_model,
)
from proyecto_mlops.utils import (
    DATA_PROCESSED_DIR,
    DATA_RAW_CSV,
    MODELS_DIR,
    PROCESSED_PARQUET,
    load_json,
)
from proyecto_mlops.evaluation import (
    full_evaluation,
    save_evaluation_report
)
from proyecto_mlops.deployment import (
    register_model_in_registry,
    promote_to_production,
    save_deployment_guide,
    get_production_model
)

app = typer.Typer(
    name="proyecto-mlops",
    help="🚀 MLOps Pipeline para Clasificación de Documentos en Español",
    rich_markup_mode="rich"
)


@app.command()
def business():
    """[PHASE1] Business Understanding - Define objetivos de negocio"""
    typer.echo("[bold blue]INICIANDO BUSINESS UNDERSTANDING[/bold blue]")
    try:
        doc = save_business_document()
        typer.echo("[bold green][OK] Documento guardado[/bold green]")
        typer.echo(f"   [INFO] Objetivo: {doc['business_objective']['titulo']}")
        typer.echo(f"   [INFO] Target F1-Macro: {doc['ml_objective']['métricas_éxito']['f1_macro_min']}")
    except Exception as e:
        typer.echo(f"[bold red][ERROR] {e}[/bold red]", err=True)
        raise typer.Exit(1)


@app.command()
def understand():
    """[PHASE2] Data Understanding - Explora y valida datos"""
    typer.echo("[bold blue]INICIANDO DATA UNDERSTANDING[/bold blue]")
    try:
        # Load and explore
        df = load_raw_dataset()
        typer.echo(f"   [OK] Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
        
        # Explore
        exploration = explore_data(df)
        typer.echo(f"   [INFO] Etiquetas: {exploration.get('label_distribution', {})}")
        
        # Schema
        save_data_schema()
        typer.echo("[bold green][OK] Data Understanding completado[/bold green]")
    except Exception as e:
        typer.echo(f"[bold red][ERROR] {e}[/bold red]", err=True)
        raise typer.Exit(1)


@app.command()
def prepare():
    """[PHASE3] Data Preparation - Preprocesa textos"""
    typer.echo("[bold blue]INICIANDO DATA PREPARATION[/bold blue]")
    try:
        prepare_data_pipeline()
        typer.echo("[bold green][OK] Datos preparados guardados en data/processed/[/bold green]")
    except Exception as e:
        typer.echo(f"[bold red][ERROR] {e}[/bold red]", err=True)
        raise typer.Exit(1)


@app.command()
def train(
    do_cv: bool = typer.Option(True, help="Realizar validación cruzada"),
    do_sweep: bool = typer.Option(False, help="Realizar grid search")
):
    """[PHASE4] Modeling - Entrena modelos de clasificacion"""
    typer.echo("[bold blue]INICIANDO MODELING[/bold blue]")
    try:
        # Load prepared data
        import os
        
        # Try CSV first (no pyarrow needed)
        csv_path = os.path.join(os.path.dirname(PROCESSED_PARQUET), "preprocesado.csv")
        
        try:
            df_prep = pd.read_csv(csv_path)
            typer.echo("   [INFO] Datos cargados desde CSV procesado")
        except Exception:
            # Fallback a CSV crudo
            df_prep = pd.read_csv(DATA_RAW_CSV)
            typer.echo("   [INFO] Datos cargados desde CSV (sin procesamiento)")
        
        texts = df_prep['text' if 'text' in df_prep.columns else 'text_prep'].tolist()
        labels = df_prep['label'].tolist()
        typer.echo(f"   [OK] {len(texts)} muestras cargadas")
        
        # Train
        model, metrics = train_model(texts, labels)
        typer.echo(f"   [OK] Modelo entrenado - F1-Macro: {metrics['f1_macro']:.4f}")
        
        # CV
        if do_cv:
            typer.echo("   [INFO] Realizando validacion cruzada...")
            cv_metrics = cross_validate_model(texts, labels)
            # Manejo seguro de diferentes claves posibles
            f1_value = cv_metrics.get('mean_f1_macro') or cv_metrics.get('f1_macro') or cv_metrics.get('mean_f1') or 0.0
            if f1_value:
                typer.echo(f"   [OK] CV F1: {f1_value:.4f}")
            else:
                typer.echo("   [OK] Validacion cruzada completada")
        
        # Save
        save_model(model)
        typer.echo("[bold green][OK] Modelo guardado en models/[/bold green]")
    except Exception as e:
        typer.echo(f"[bold red][ERROR] {e}[/bold red]", err=True)
        raise typer.Exit(1)


@app.command()
def evaluate():
    """[PHASE5] Evaluation - Evalua desempeño del modelo"""
    typer.echo("[bold blue]INICIANDO EVALUATION[/bold blue]")
    try:
        # Cargar modelo y datos
        import os
        import joblib
        from sklearn.model_selection import train_test_split
        
        # Cargar datos
        csv_path = os.path.join(os.path.dirname(PROCESSED_PARQUET), "preprocesado.csv")
        try:
            df_prep = pd.read_csv(csv_path)
        except Exception:
            df_prep = pd.read_csv(DATA_RAW_CSV)
        
        texts = df_prep['text' if 'text' in df_prep.columns else 'text_prep'].tolist()
        labels = df_prep['label'].tolist()
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Cargar modelo
        model_files = [f for f in os.listdir(MODELS_DIR) if f.startswith('svm_tfidf_v') and f.endswith('.joblib')]
        if model_files:
            latest_model = sorted(model_files, key=lambda x: int(x.replace('svm_tfidf_v', '').replace('.joblib', '')))[-1]
            model_path = os.path.join(MODELS_DIR, latest_model)
            pipe = joblib.load(model_path)
            typer.echo(f"   [INFO] Modelo cargado: {latest_model}")
        else:
            typer.echo("   [WARN] No hay modelo entrenado")
            raise typer.Exit(1)
        
        # Evaluar
        status_report = full_evaluation(pipe, X_test, y_test)
        save_evaluation_report(status_report)
        typer.echo(f"   [OK] Status: {status_report.get('overall_status', 'UNKNOWN')}")
        typer.echo("[bold green][OK] Evaluacion completada[/bold green]")
    except Exception as e:
        typer.echo(f"[bold red][ERROR] {e}[/bold red]", err=True)
        raise typer.Exit(1)


@app.command()
def deploy(
    promote: bool = typer.Option(False, help="Promover a produccion"),
    version: Optional[int] = typer.Option(None, help="Version a promover")
):
    """[PHASE6] Deployment - Registra y despliega modelos"""
    typer.echo("[bold blue]INICIANDO DEPLOYMENT[/bold blue]")
    try:
        import os
        import joblib
        from datetime import datetime
        
        # Buscar modelo más reciente
        model_files = [f for f in os.listdir(MODELS_DIR) if f.startswith('svm_tfidf_v') and f.endswith('.joblib')]
        if not model_files:
            typer.echo("   [WARN] No hay modelo entrenado para desplegar")
            raise typer.Exit(1)
        
        latest_model = sorted(model_files, key=lambda x: int(x.replace('svm_tfidf_v', '').replace('.joblib', '')))[-1]
        model_path = os.path.join(MODELS_DIR, latest_model)
        
        # Extraer versión
        model_version = int(latest_model.replace('svm_tfidf_v', '').replace('.joblib', ''))
        
        # Cargar métricas de evaluación
        evaluation_report_path = os.path.join(DATA_PROCESSED_DIR, "evaluation_report.json")
        if os.path.exists(evaluation_report_path):
            eval_report = load_json(evaluation_report_path)
            metrics = eval_report.get("metrics", {})
        else:
            metrics = {"status": "not_evaluated"}
        
        # Registrar modelo
        register_model_in_registry(
            model_path=model_path,
            model_name="svm_tfidf",
            version=model_version,
            metrics=metrics,
            status="candidate"
        )
        typer.echo("   [OK] Modelo registrado")
        
        # Solo promover si se especifica explícitamente
        if promote is True and version is not None:
            promote_to_production(version)
            typer.echo(f"   [OK] Modelo v{version} promovido a produccion")
        
        save_deployment_guide()
        typer.echo("[bold green][OK] Deployment completado[/bold green]")
    except Exception as e:
        typer.echo(f"[bold red][ERROR] {e}[/bold red]", err=True)
        raise typer.Exit(1)


@app.command()
def all(
    cv: bool = typer.Option(True, help="Incluir validacion cruzada")
):
    """Pipeline Completo - Ejecuta todas las fases CRISP-DM"""
    typer.echo("[bold cyan]INICIANDO PIPELINE COMPLETO CRISP-DM[/bold cyan]\n")
    
    try:
        # Phase 1
        typer.echo("[bold]1 - Business Understanding[/bold]")
        business()
        typer.echo()
        
        # Phase 2
        typer.echo("[bold]2 - Data Understanding[/bold]")
        understand()
        typer.echo()
        
        # Phase 3
        typer.echo("[bold]3 - Data Preparation[/bold]")
        prepare()
        typer.echo()
        
        # Phase 4
        typer.echo("[bold]4 - Modeling[/bold]")
        train(do_cv=cv)
        typer.echo()
        
        # Phase 5
        typer.echo("[bold]5 - Evaluation[/bold]")
        evaluate()
        typer.echo()
        
        # Phase 6
        typer.echo("[bold]6 - Deployment[/bold]")
        deploy()
        typer.echo()
        
        typer.echo("[bold green]*** PIPELINE COMPLETO FINALIZADO EXITOSAMENTE ***[/bold green]")
        
    except Exception as e:
        typer.echo(f"\n[bold red][ERROR] PIPELINE FALLIDO: {e}[/bold red]", err=True)
        raise typer.Exit(1)


@app.command()
def status():
    """Estado del modelo actual en produccion"""
    typer.echo("[bold blue]Estado Actual[/bold blue]")
    try:
        prod_model = get_production_model()
        if prod_model:
            typer.echo(f"   [OK] Modelo en Produccion: v{prod_model['version']}")
            typer.echo(f"   [INFO] Fecha: {prod_model.get('created_at', 'N/A')}")
            typer.echo(f"   [INFO] F1-Macro: {prod_model.get('metrics', {}).get('f1_macro', 'N/A')}")
        else:
            typer.echo("   [WARN] No hay modelo en produccion")
    except Exception as e:
        typer.echo(f"[bold red][ERROR] {e}[/bold red]", err=True)


@app.command()
def version():
    """Version del paquete"""
    typer.echo("proyecto-mlops v0.1.0")
    typer.echo("MLOps Pipeline para Clasificacion de Documentos en Espanol")


def main():
    """Punto de entrada principal"""
    app()


if __name__ == "__main__":
    main()
