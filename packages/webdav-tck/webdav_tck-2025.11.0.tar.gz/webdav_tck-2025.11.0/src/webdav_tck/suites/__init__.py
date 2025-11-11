"""WebDAV test suites."""

from __future__ import annotations

from webdav_tck.suites.basic import create_basic_suite
from webdav_tck.suites.copymove import create_copymove_suite
from webdav_tck.suites.locks import create_locks_suite
from webdav_tck.suites.props import create_props_suite

__all__ = [
    "create_basic_suite",
    "create_copymove_suite",
    "create_locks_suite",
    "create_props_suite",
]
