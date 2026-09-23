"""Compatibility shim — re-exports everything from ``brep_primitives``.

Prefer importing from ``brep_primitives`` directly.  This module exists
so that scripts inside and outside chapter 06 that still reference
``brep_mesh_rendering`` continue to work without changes.
"""

from brep_primitives import *  # noqa: F401, F403
