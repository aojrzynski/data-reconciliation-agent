"""Deterministic key-level reconciliation checks."""

from __future__ import annotations

import pandas as pd


def key_exists(dataframe: pd.DataFrame, key: str) -> bool:
    return key in dataframe.columns


def _normalize_key_series(dataframe: pd.DataFrame, key: str) -> pd.Series:
    return dataframe[key].astype("string").str.strip()


def null_keys(dataframe: pd.DataFrame, key: str) -> pd.DataFrame:
    key_series = _normalize_key_series(dataframe, key)
    null_mask = key_series.isna() | (key_series == "")
    return dataframe[null_mask].copy()


def duplicate_keys(dataframe: pd.DataFrame, key: str) -> pd.DataFrame:
    key_series = _normalize_key_series(dataframe, key)
    non_null_mask = ~(key_series.isna() | (key_series == ""))
    dup_mask = key_series[non_null_mask].duplicated(keep=False)
    full_mask = pd.Series(False, index=dataframe.index)
    full_mask.loc[dup_mask.index] = dup_mask
    return dataframe[full_mask].copy()


def missing_keys(source_df: pd.DataFrame, target_df: pd.DataFrame, source_key: str, target_key: str) -> pd.DataFrame:
    source_keys = _normalize_key_series(source_df, source_key)
    target_key_set = set(_normalize_key_series(target_df, target_key).dropna())
    target_key_set.discard("")
    missing_mask = source_keys.notna() & (source_keys != "") & ~source_keys.isin(target_key_set)
    return source_df[missing_mask].copy()


def unexpected_keys(source_df: pd.DataFrame, target_df: pd.DataFrame, source_key: str, target_key: str) -> pd.DataFrame:
    source_key_set = set(_normalize_key_series(source_df, source_key).dropna())
    source_key_set.discard("")
    target_keys = _normalize_key_series(target_df, target_key)
    unexpected_mask = target_keys.notna() & (target_keys != "") & ~target_keys.isin(source_key_set)
    return target_df[unexpected_mask].copy()
