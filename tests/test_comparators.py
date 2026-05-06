from data_reconciliation_agent.comparators import compare_values


def test_string_exact_match() -> None:
    assert compare_values("abc", "abc", "string").matched


def test_string_trim_match() -> None:
    assert compare_values(" abc ", "abc", "string", normalize={"trim": True}).matched


def test_string_case_insensitive_match() -> None:
    assert compare_values("ABC", "abc", "string", normalize={"case_sensitive": False}).matched


def test_string_mismatch() -> None:
    assert not compare_values("abc", "xyz", "string").matched


def test_null_vs_null_matches() -> None:
    out = compare_values(" ", None, "string")
    assert out.matched and out.reason == "both_null"


def test_null_vs_value_mismatch() -> None:
    out = compare_values(None, "x", "string")
    assert not out.matched and out.reason == "one_null"


def test_number_exact_match() -> None:
    assert compare_values("10", 10, "number").matched


def test_number_tolerance_match() -> None:
    assert compare_values(10.0, 10.009, "number", tolerance=0.01).matched


def test_number_outside_tolerance_mismatch() -> None:
    assert not compare_values(10.0, 10.02, "number", tolerance=0.01).matched


def test_number_parse_error() -> None:
    assert compare_values("ten", 10, "number").reason == "number_parse_error"


def test_date_formats_match() -> None:
    assert compare_values("2024/04/05", "2024-04-05", "date").matched


def test_date_mismatch() -> None:
    assert not compare_values("2024-04-05", "2024-04-06", "date").matched


def test_date_parse_error() -> None:
    assert compare_values("bad", "2024-04-06", "date").reason == "date_parse_error"


def test_datetime_exact_iso_match() -> None:
    assert compare_values("2024-04-01T10:15:00Z", "2024-04-01T10:15:00+00:00", "datetime").matched


def test_datetime_parse_error() -> None:
    assert compare_values("bad", "2024-04-01T10:15:00Z", "datetime").reason == "datetime_parse_error"
