# -*- coding: utf-8 -*-
"""
Paquete principal de proyecto_mlops.
"""

__version__ = "0.1.3"
__author__ = "Angel Castellanos"

from .business_understanding import (
    define_business_objectives,
    save_business_document,
    load_business_document
)

from .data_understanding import (
    load_raw_dataset,
    explore_data,
    save_data_exploration,
    make_data_schema,
    save_data_schema,
    validate_schema
)

from .data_preparation import (
    normalize_text,
    tokenize_simple,
    clean_tokens,
    stem_tokens,
    preprocess_dataframe,
    save_preprocessed_data,
    load_preprocessed_data,
    prepare_data_pipeline,
    get_preprocessing_config
)

from .modeling import (
    make_classification_pipeline,
    train_model,
    cross_validate_model,
    save_model,
    load_model,
    log_experiment,
    hyperparameter_sweep
)

from .evaluation import (
    evaluate_model,
    measure_latency,
    check_fairness,
    full_evaluation,
    save_evaluation_report
)

from .deployment import (
    register_model_in_registry,
    promote_to_production,
    get_production_model,
    create_deployment_package,
    generate_deployment_guide,
    save_deployment_guide
)

__all__ = [
    # Business Understanding
    "define_business_objectives",
    "save_business_document",
    "load_business_document",
    # Data Understanding
    "load_raw_dataset",
    "explore_data",
    "save_data_exploration",
    "make_data_schema",
    "save_data_schema",
    "validate_schema",
    # Data Preparation
    "normalize_text",
    "tokenize_simple",
    "clean_tokens",
    "stem_tokens",
    "preprocess_dataframe",
    "save_preprocessed_data",
    "load_preprocessed_data",
    "prepare_data_pipeline",
    "get_preprocessing_config",
    # Modeling
    "make_classification_pipeline",
    "train_model",
    "cross_validate_model",
    "save_model",
    "load_model",
    "log_experiment",
    "hyperparameter_sweep",
    # Evaluation
    "evaluate_model",
    "measure_latency",
    "check_fairness",
    "full_evaluation",
    "save_evaluation_report",
    # Deployment
    "register_model_in_registry",
    "promote_to_production",
    "get_production_model",
    "create_deployment_package",
    "generate_deployment_guide",
    "save_deployment_guide",
]
