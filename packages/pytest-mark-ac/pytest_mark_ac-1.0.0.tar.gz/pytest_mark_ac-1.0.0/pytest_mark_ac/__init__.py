"""
Plugin callbacks to register and handle the markers.
"""

from collections.abc import Sequence

import pytest

_MARK = "ac"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        f"{_MARK}(story_id: int, criteria_ids: Sequence[int], "
        'ref_prefix: str = "ac", ref_suffix: str = ""): '
        "appends suffixes in the form __<ref_prefix><story>_<criterion><ref_suffix> "
        "to the test nodeid",
    )


def _validate_and_expand(mark: pytest.Mark) -> list[str]:
    if len(mark.args) != 2:
        raise pytest.UsageError(
            f"@pytest.mark.{_MARK} requires 2 positional arguments: "
            "(story_id:int, criteria_ids:Sequence[int])"
        )
    story_id, criteria_ids = mark.args
    if not isinstance(story_id, int):
        raise pytest.UsageError(f"{_MARK}: story_id must be int, got {type(story_id).__name__}")
    if isinstance(criteria_ids, (str, bytes)) or not isinstance(criteria_ids, Sequence):
        raise pytest.UsageError(f"{_MARK}: criteria_ids must be an int sequence")
    ref_prefix: str = str(mark.kwargs.get("ref_prefix", "ac"))
    ref_suffix: str = str(mark.kwargs.get("ref_suffix", ""))
    out = []
    for idx, cid in enumerate(criteria_ids):
        if not isinstance(cid, int):
            raise pytest.UsageError(
                f"{_MARK}: each criterion must be int, got {type(cid).__name__} at position {idx}"
            )
        out.append(f"__{ref_prefix}{story_id}_{cid}{ref_suffix}")
    return out


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
) -> None:
    for item in items:
        marks = list(item.iter_markers(_MARK))
        if not marks:
            continue
        suffixes: list[str] = []
        for m in marks:
            suffixes.extend(_validate_and_expand(m))

        seen = set()
        suffixes = [s for s in suffixes if not (s in seen or seen.add(s))]
        suffixes = [s for s in suffixes if s not in item.nodeid]
        if suffixes:
            item._nodeid = item.nodeid + "".join(suffixes)
