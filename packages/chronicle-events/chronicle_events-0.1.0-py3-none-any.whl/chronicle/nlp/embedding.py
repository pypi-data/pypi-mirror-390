from __future__ import annotations
from typing import List
import numpy as np

_model = None
_vectorizer = None


def _ensure_sbert():
    global _model
    if _model is not None:
        return _model
    try:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    except Exception:
        _model = None
    return _model


def _ensure_tfidf(corpus: List[str]):
    global _vectorizer
    if _vectorizer is None:
        from sklearn.feature_extraction.text import TfidfVectorizer

        _vectorizer = TfidfVectorizer(max_features=4096, ngram_range=(1, 2))
        _vectorizer.fit(corpus)
    return _vectorizer


def encode(texts: List[str]) -> np.ndarray:
    m = _ensure_sbert()
    if m is not None:
        return np.asarray(m.encode(texts, normalize_embeddings=True))
    v = _ensure_tfidf(texts)
    X = v.transform(texts).toarray()
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return X / norms
