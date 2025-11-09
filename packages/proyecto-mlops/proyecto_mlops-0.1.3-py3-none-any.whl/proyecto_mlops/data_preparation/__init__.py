# -*- coding: utf-8 -*-
"""
FASE 3: DATA PREPARATION
Preprocesamiento y transformación de datos.
"""

import os
import re
import unicodedata
import pandas as pd
from typing import List
from nltk.corpus import stopwords
from nltk.stem.snowball import SpanishStemmer

from ..utils import (
    ensure_dirs, save_json, logger,
    DATA_RAW_CSV, PROCESSED_PARQUET, DATA_PROCESSED_DIR
)


# Inicializar recursos
SPANISH_SW = set(stopwords.words("spanish"))
STEMMER = SpanishStemmer()


def normalize_text(text: str) -> str:
    """Normaliza texto: lowercase, remove accents, whitespace."""
    text = str(text).lower()
    # Remove accents
    text = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    # Normalize whitespace
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_simple(text: str) -> List[str]:
    """Tokenización simple (palabras)."""
    return re.findall(r"\b\w+\b", text, flags=re.UNICODE)


def clean_tokens(
    tokens: List[str],
    remove_digits: bool = True,
    remove_stopwords: bool = True
) -> List[str]:
    """Limpia tokens: elimina dígitos y stopwords."""
    cleaned = []
    for token in tokens:
        if remove_digits and token.isdigit():
            continue
        if remove_stopwords and token in SPANISH_SW:
            continue
        cleaned.append(token)
    return cleaned


def stem_tokens(tokens: List[str]) -> List[str]:
    """Aplica stemming a los tokens."""
    return [STEMMER.stem(t) for t in tokens]


def preprocess_dataframe(
    df: pd.DataFrame,
    use_lemmatization: bool = False
) -> pd.DataFrame:
    """
    Preprocesa un DataFrame completo.
    Añade columnas: text_norm, tokens, stems, [lemmas]
    """
    ensure_dirs(DATA_PROCESSED_DIR)
    
    d = df.copy()
    d["text_norm"] = d["text"].astype(str).apply(normalize_text)
    d["tokens"] = d["text_norm"].apply(tokenize_simple)
    d["tokens"] = d["tokens"].apply(clean_tokens)
    d["stems"] = d["tokens"].apply(stem_tokens)
    
    if use_lemmatization:
        try:
            import spacy
            nlp = spacy.load("es_core_news_sm")
            d["lemmas"] = d["tokens"].apply(
                lambda tokens: [
                    token.lemma_ if token.lemma_ else token.text
                    for token in nlp(" ".join(tokens))
                ]
            )
            logger.info("[DATA_PREPARATION] Lematización completada")
        except Exception as e:
            logger.warning(f"[DATA_PREPARATION] Lematización no disponible: {e}")
            d["lemmas"] = d["stems"]
    
    logger.info(f"[DATA_PREPARATION] Datos preprocesados: {d.shape}")
    return d


def save_preprocessed_data(
    df: pd.DataFrame,
    output_path: str = PROCESSED_PARQUET
) -> str:
    """Guarda datos preprocesados en CSV (fallback desde parquet)."""
    ensure_dirs(os.path.dirname(output_path))
    # Cambiar extensión a CSV si es parquet
    if output_path.endswith('.parquet'):
        output_path = output_path.replace('.parquet', '.csv')
    # Guardar como CSV
    df.to_csv(output_path, index=False)
    logger.info(f"[DATA_PREPARATION] Datos guardados: {output_path}")
    return output_path


def load_preprocessed_data(input_path: str = PROCESSED_PARQUET) -> pd.DataFrame:
    """Carga datos preprocesados (CSV o parquet)."""
    if not os.path.exists(input_path):
        # Intentar con CSV si parquet no existe
        csv_path = input_path.replace('.parquet', '.csv')
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path)
        raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
    # Intentar parquet primero
    try:
        return pd.read_parquet(input_path)
    except Exception:
        # Fallback a CSV
        csv_path = input_path.replace('.parquet', '.csv')
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path)
        raise


def prepare_data_pipeline(
    csv_path: str = DATA_RAW_CSV,
    output_path: str = PROCESSED_PARQUET,
    use_lemmatization: bool = False
) -> pd.DataFrame:
    """Pipeline completo: load -> preprocess -> save."""
    logger.info("[DATA_PREPARATION] Iniciando pipeline...")
    
    # Cargar
    df = pd.read_csv(csv_path)
    logger.info(f"[DATA_PREPARATION] Datos cargados: {csv_path}")
    
    # Preprocesar
    df_prep = preprocess_dataframe(df, use_lemmatization=use_lemmatization)
    
    # Guardar
    save_preprocessed_data(df_prep, output_path)
    
    logger.info("[DATA_PREPARATION] Pipeline completado")
    return df_prep


def get_preprocessing_config() -> dict:
    """Retorna configuración de preprocesamiento."""
    return {
        "normalize": True,
        "lowercase": True,
        "remove_accents": True,
        "tokenization": "simple_regex",
        "remove_digits": True,
        "remove_stopwords": True,
        "stemming": "Snowball(Spanish)",
        "language": "es"
    }
