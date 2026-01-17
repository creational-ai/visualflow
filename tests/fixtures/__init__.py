"""Test fixtures with realistic box content."""

from tests.fixtures.simple_chain import create_simple_chain
from tests.fixtures.diamond import create_diamond
from tests.fixtures.wide_fanout import create_wide_fanout
from tests.fixtures.merge_branch import create_merge_branch
from tests.fixtures.skip_level import create_skip_level
from tests.fixtures.standalone import create_standalone
from tests.fixtures.complex_graph import create_complex_graph

__all__ = [
    "create_simple_chain",
    "create_diamond",
    "create_wide_fanout",
    "create_merge_branch",
    "create_skip_level",
    "create_standalone",
    "create_complex_graph",
]
