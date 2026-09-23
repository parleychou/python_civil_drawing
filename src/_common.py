"""Shared utility for resolving chapter script directories."""

from pathlib import Path


def find_chapter_scripts(prefix: str) -> Path:
    """Walk up from this file's location to find a chapter directory.

    Used by scripts that need to import from other chapters (e.g. the
    RenderEngine in chapter 04, or GeometryData in chapter 05).
    """
    current = Path(__file__).resolve()
    for parent in current.parents:
        try:
            for child in parent.iterdir():
                if child.is_dir() and child.name.startswith(prefix):
                    for sub_name in ("src", "scripts"):
                        sub = child / sub_name
                        if sub.exists():
                            return sub
                    return child
        except OSError:
            continue
    return Path()
