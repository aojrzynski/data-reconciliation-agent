"""Mapping configuration loading and validation for deterministic reconciliation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

ALLOWED_COMPARATORS = {"string", "number", "date", "datetime"}


@dataclass(frozen=True)
class FieldMapping:
    source: str
    target: str
    comparator: str
    normalize: dict | None = None
    tolerance: float | None = None


@dataclass(frozen=True)
class MappingConfig:
    entity: str
    source_key: str
    target_key: str
    field_mappings: list[FieldMapping]


def load_mapping_config(path: str) -> MappingConfig:
    mapping_path = Path(path)
    if not mapping_path.exists():
        raise FileNotFoundError(f"Mapping file does not exist: {path}")

    try:
        raw = yaml.safe_load(mapping_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Could not parse mapping YAML: {path}. {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("Mapping YAML must parse to a dictionary/object.")

    required_top_level = ["entity", "source_key", "target_key", "field_mappings"]
    for field_name in required_top_level:
        if field_name not in raw:
            raise ValueError(f"Mapping config is missing required field: '{field_name}'.")

    field_mappings_raw = raw["field_mappings"]
    if not isinstance(field_mappings_raw, list):
        raise ValueError("Mapping config field 'field_mappings' must be a list.")

    field_mappings: list[FieldMapping] = []
    for index, field in enumerate(field_mappings_raw):
        if not isinstance(field, dict):
            raise ValueError(f"field_mappings[{index}] must be an object.")
        for required in ["source", "target", "comparator"]:
            if required not in field:
                raise ValueError(f"field_mappings[{index}] is missing required field '{required}'.")

        comparator = str(field["comparator"])
        if comparator not in ALLOWED_COMPARATORS:
            raise ValueError(
                f"field_mappings[{index}].comparator must be one of {sorted(ALLOWED_COMPARATORS)}; got '{comparator}'."
            )

        tolerance = field.get("tolerance")
        if tolerance is not None:
            try:
                tolerance = float(tolerance)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"field_mappings[{index}].tolerance must be numeric when provided.") from exc

        normalize = field.get("normalize")
        if normalize is not None and not isinstance(normalize, dict):
            raise ValueError(f"field_mappings[{index}].normalize must be an object when provided.")

        field_mappings.append(
            FieldMapping(
                source=str(field["source"]),
                target=str(field["target"]),
                comparator=comparator,
                normalize=normalize,
                tolerance=tolerance,
            )
        )

    return MappingConfig(
        entity=str(raw["entity"]),
        source_key=str(raw["source_key"]),
        target_key=str(raw["target_key"]),
        field_mappings=field_mappings,
    )


def validate_mapping_config(config: MappingConfig, source_columns: list[str], target_columns: list[str]) -> list[str]:
    errors: list[str] = []

    if config.source_key not in source_columns:
        errors.append(f"Mapping source_key '{config.source_key}' is not present in source columns.")
    if config.target_key not in target_columns:
        errors.append(f"Mapping target_key '{config.target_key}' is not present in target columns.")

    for index, field_mapping in enumerate(config.field_mappings):
        if field_mapping.source not in source_columns:
            errors.append(
                f"field_mappings[{index}].source '{field_mapping.source}' is not present in source columns."
            )
        if field_mapping.target not in target_columns:
            errors.append(
                f"field_mappings[{index}].target '{field_mapping.target}' is not present in target columns."
            )
        if field_mapping.comparator not in ALLOWED_COMPARATORS:
            errors.append(
                f"field_mappings[{index}].comparator '{field_mapping.comparator}' is not supported. "
                f"Allowed: {sorted(ALLOWED_COMPARATORS)}."
            )

    return errors


def mapping_config_to_trace_dict(config: MappingConfig) -> dict:
    comparators = sorted({field_mapping.comparator for field_mapping in config.field_mappings})
    return {
        "entity": config.entity,
        "source_key": config.source_key,
        "target_key": config.target_key,
        "mapped_field_count": len(config.field_mappings),
        "planned_comparators": comparators,
    }
