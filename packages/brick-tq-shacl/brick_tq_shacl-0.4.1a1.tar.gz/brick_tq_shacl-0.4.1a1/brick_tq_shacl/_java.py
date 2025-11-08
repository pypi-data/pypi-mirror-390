"""Utilities for ensuring a Java runtime is available.

This module optionally downloads a local JRE using the install-jdk package when
the package is installed with the ``withjre`` extra. Consumers that already
provide Java on PATH will incur no additional overhead.
"""
from __future__ import annotations

import os
import shutil
import threading
from pathlib import Path
from typing import Optional

_BOOTSTRAP_LOCK = threading.Lock()
_BOOTSTRAPPED = False


def _java_on_path() -> bool:
    """Return True if ``java`` is already discoverable."""
    return shutil.which("java") is not None


def _prepend_path(path: Path) -> None:
    """Prepend the provided path to PATH if not present."""
    current = os.environ.get("PATH", "")
    paths = current.split(os.pathsep) if current else []
    str_path = str(path)
    if str_path in paths:
        return
    os.environ["PATH"] = os.pathsep.join([str_path] + paths if paths else [str_path])


def ensure_java_runtime(version: Optional[str] = None) -> None:
    """Ensure that a Java runtime is available for pytqshacl.

    Parameters
    ----------
    version:
        Optional Java version string to install (defaults to the value of the
        BRICK_TQ_SHACL_JRE_VERSION environment variable, or ``"17"``).

    Raises
    ------
    RuntimeError
        If Java cannot be located and the local installation step fails or the
        install-jdk dependency is missing.
    """
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return

    with _BOOTSTRAP_LOCK:
        if _BOOTSTRAPPED:
            return
        if _java_on_path():
            _BOOTSTRAPPED = True
            return

        try:
            import jdk  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Java runtime not found. Install Java manually or reinstall "
                "brick-tq-shacl with the 'withjre' extra (for example, "
                "`uv sync --extra withjre`) to auto-provision a JRE."
            ) from exc

        requested_version = (
            version
            or os.environ.get("BRICK_TQ_SHACL_JRE_VERSION")
            or "17"
        )
        install_root = Path(
            os.environ.get(
                "BRICK_TQ_SHACL_JRE_HOME",
                Path.home() / ".brick_tq_shacl" / "jre",
            )
        )
        install_root.mkdir(parents=True, exist_ok=True)

        vendor = os.environ.get("BRICK_TQ_SHACL_JRE_VENDOR")

        try:
            install_kwargs = {
                "jre": True,
                "path": str(install_root),
            }
            if vendor:
                install_kwargs["vendor"] = vendor  # type: ignore[arg-type]
            install_path_str = jdk.install(requested_version, **install_kwargs)
        except Exception as exc:  # pragma: no cover - defensive fallback
            raise RuntimeError(
                f"Failed to install Java runtime version {requested_version!r}: {exc}"
            ) from exc

        install_path = Path(install_path_str).expanduser()
        bin_path = install_path / "bin"
        os.environ.setdefault("JAVA_HOME", str(install_path))
        if bin_path.is_dir():
            _prepend_path(bin_path)

        if not _java_on_path():
            raise RuntimeError(
                "Java runtime installation completed but `java` is still not on PATH. "
                f"Checked path: {install_path}"
            )

        _BOOTSTRAPPED = True
