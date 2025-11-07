# ruff: noqa: PYI021, D415

import builtins
import typing

def generate_call_graph(
    lib_paths: dict,
    function_filter: builtins.str | None = None,
    select_path: builtins.str | None = None,
) -> typing.Any:
    r"""Generate a call graph for Python libraries"""

def get_settings() -> dict[str, typing.Any]:
    r"""Get the merged settings from all sources"""
