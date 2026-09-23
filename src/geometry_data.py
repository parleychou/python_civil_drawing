"""Compatibility shim — re-exports everything from ``geometry_primitives``.

Prefer importing from ``geometry_primitives`` directly.  This module exists
so that scripts outside chapter 05 that still reference ``geometry_data``
continue to work without changes.
"""

from geometry_primitives import *  # noqa: F401, F403
