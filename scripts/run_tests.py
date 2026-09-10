#!/usr/bin/env python3
"""Test entry point for this project (invoked by ``npm test``).

CoralCal is a Django project, but its dependencies are not always installed --
a bare checkout has no ``venv`` and no ``django`` on the path. The specs
consistency suite in ``core/tests.py`` is deliberately written against the
standard library so it still runs in that situation.

This runner therefore collects every ``<app>/tests.py`` module and runs what it
can. A module that fails to import *only* because an optional third-party
dependency from ``requirements.txt`` is missing is reported as skipped rather
than failed; any other import error is a real problem and is re-raised. If
nothing at all could be collected the run fails, so an environment that quietly
skips the entire suite can never be mistaken for a passing one.

Install the full dependency set (``pip install -r requirements.txt``) to run the
Django-backed tests as well.
"""

import importlib
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Third-party packages that tests may import. They are declared in
# requirements.txt, so their absence means "environment not fully provisioned",
# not "the code is broken".
OPTIONAL_DEPENDENCIES = {
    "django",
    "openpyxl",
    "pandas",
    "numpy",
    "PIL",
    "requests",
    "MySQLdb",
    "dateutil",
}


def _missing_dependency(exc):
    """Return the top-level package name an ImportError is complaining about."""
    name = getattr(exc, "name", None)
    return name.split(".")[0] if name else ""


def collect():
    """Import every ``<app>/tests.py``; return ``(suite, skipped)``."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    skipped = []

    for path in sorted(BASE_DIR.glob("*/tests.py")):
        module_name = "{}.tests".format(path.parent.name)
        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            missing = _missing_dependency(exc)
            if missing in OPTIONAL_DEPENDENCIES:
                skipped.append((module_name, missing))
                continue
            raise
        suite.addTests(loader.loadTestsFromModule(module))

    return suite, skipped


def main():
    sys.path.insert(0, str(BASE_DIR))
    suite, skipped = collect()

    if skipped:
        print("Skipped (dependency not installed):", file=sys.stderr)
        for module_name, missing in skipped:
            print("  {} (needs {})".format(module_name, missing), file=sys.stderr)
        print(file=sys.stderr)

    if suite.countTestCases() == 0:
        print(
            "No tests could be collected -- refusing to report success.\n"
            "Install dependencies with: pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
