"""Deterministic key inference helpers for bounded agent mode."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class KeyCandidate:
    source_key: str
    target_key: str
    confidence: str
    score: float
    reasons: list[str]
    warnings: list[str]


def _norm(series: pd.Series) -> pd.Series:
    normalized = series.astype("string").str.strip().str.lower()
    return normalized.where(normalized.notna() & (normalized != ""))


def _id_like(column: str) -> bool:
    name = column.lower()
    return name == "id" or name.endswith("_id") or name.endswith("_key") or name in {
        "customer_id",
        "order_id",
        "contact_id",
    }


def infer_key_candidates(source_df: pd.DataFrame, target_df: pd.DataFrame) -> list[KeyCandidate]:
    candidates: list[KeyCandidate] = []
    for column in sorted(set(source_df.columns) & set(target_df.columns)):
        source_values = _norm(source_df[column])
        target_values = _norm(target_df[column])
        source_non_null = source_values.dropna()
        target_non_null = target_values.dropna()
        if len(source_df) == 0 or len(target_df) == 0:
            continue

        source_non_null_ratio = len(source_non_null) / len(source_df)
        target_non_null_ratio = len(target_non_null) / len(target_df)
        source_unique_ratio = source_non_null.nunique() / max(1, len(source_non_null))
        target_unique_ratio = target_non_null.nunique() / max(1, len(target_non_null))
        overlap = 0.0
        if len(source_non_null) and len(target_non_null):
            source_set = set(source_non_null)
            target_set = set(target_non_null)
            overlap = len(source_set & target_set) / max(1, min(len(source_set), len(target_set)))

        score = 0.0
        reasons: list[str] = []
        warnings: list[str] = []

        if _id_like(column):
            score += 0.35
            reasons.append("column name is identifier-like")
        else:
            score -= 0.20
            warnings.append("column name is not identifier-like")
        if source_non_null_ratio > 0.95 and target_non_null_ratio > 0.95:
            score += 0.20
            reasons.append("high non-null ratio in source and target")
        else:
            score -= 0.15
            warnings.append("null-heavy column")
        if source_unique_ratio > 0.95 and target_unique_ratio > 0.95:
            score += 0.25
            reasons.append("high uniqueness ratio in source and target")
        else:
            score -= 0.25
            warnings.append("duplicate-heavy column")
        if overlap > 0.80:
            score += 0.25
            reasons.append("high normalized key overlap between source and target")
        elif overlap < 0.20:
            score -= 0.25
            warnings.append("very low overlap between source and target")

        lower_name = column.lower()
        if any(term in lower_name for term in ["name", "status", "date", "email", "city", "state"]):
            score -= 0.20
            warnings.append("column looks descriptive, not identifier-like")

        if score >= 0.75:
            confidence = "high"
        elif score >= 0.45:
            confidence = "medium"
        else:
            confidence = "low"
        candidates.append(KeyCandidate(column, column, confidence, round(score, 3), reasons, warnings))
    return sorted(candidates, key=lambda c: c.score, reverse=True)
