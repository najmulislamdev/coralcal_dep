"""Consistency tests for the ``specs/`` documentation tree.

Each spec under ``specs/`` carries YAML frontmatter (``feature``, ``owns``,
``last_verified``) and ``specs/INDEX.md`` repeats that ownership in a table.
These tests keep the three sources -- frontmatter, index table, and the apps
that actually exist -- in agreement, so adding or renaming an app cannot
silently leave the specs stale.

Plain ``unittest.TestCase`` is used rather than ``django.test.TestCase``:
nothing here needs settings loaded or a database, so ``settings.py`` is read
statically with ``ast``. The frontmatter is hand-parsed because PyYAML is not
a dependency of this project.
"""

import ast
import re
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SPECS_DIR = BASE_DIR / "specs"
INDEX = SPECS_DIR / "INDEX.md"

# The Django project package: owned by core-platform.md but not an installed
# app, so it is exempt from the INSTALLED_APPS cross-checks.
PROJECT_PACKAGE = "coralcal_dep"

REQUIRED_FRONTMATTER_KEYS = {"feature", "owns", "last_verified"}
FIRST_HEADING = "## What it does"

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
OWNED_RE = re.compile(r"`([A-Za-z0-9_]+)/`")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def spec_paths():
    """Every spec file, excluding the index itself."""
    return sorted(p for p in SPECS_DIR.glob("*.md") if p.name != INDEX.name)


def parse_frontmatter(path):
    """Parse the leading ``---`` block of a spec.

    Returns ``(mapping, body)``. Only the two shapes the specs actually use are
    supported: ``key: value`` scalars and ``key:`` followed by ``  - item``
    list entries. Raises AssertionError if the block is missing or unclosed.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise AssertionError(f"{path.name} does not start with a '---' frontmatter block")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise AssertionError(f"{path.name} has an unclosed frontmatter block")

    data = {}
    current_list_key = None
    for line in lines[1:end]:
        if not line.strip():
            continue
        if line.startswith(("  - ", "- ")):
            if current_list_key is None:
                raise AssertionError(f"{path.name}: list item {line!r} has no parent key")
            data[current_list_key].append(line.split("-", 1)[1].strip())
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value:
            data[key] = value
            current_list_key = None
        else:
            data[key] = []
            current_list_key = key
    return data, "\n".join(lines[end + 1 :])


def index_rows():
    """Yield ``(spec_filename, owned_dirs)`` for each data row of the index table."""
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3:
            continue
        link = LINK_RE.search(cells[0])
        if link is None:  # header and |---|---|---| separator rows
            continue
        yield link.group(2), OWNED_RE.findall(cells[2])


def installed_local_apps():
    """Names of the project's own apps, read statically from settings.py."""
    source = (BASE_DIR / PROJECT_PACKAGE / "settings.py").read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "INSTALLED_APPS" for t in node.targets
        ):
            apps = ast.literal_eval(node.value)
            return {a for a in apps if not a.startswith("django.contrib")}
    raise AssertionError("INSTALLED_APPS not found in settings.py")


class SpecFrontmatterTests(unittest.TestCase):
    def test_specs_exist(self):
        self.assertTrue(spec_paths(), "no spec files found under specs/")

    def test_frontmatter_has_required_keys(self):
        for path in spec_paths():
            with self.subTest(spec=path.name):
                data, _ = parse_frontmatter(path)
                self.assertTrue(
                    REQUIRED_FRONTMATTER_KEYS <= set(data),
                    f"{path.name} frontmatter is missing "
                    f"{sorted(REQUIRED_FRONTMATTER_KEYS - set(data))}",
                )

    def test_feature_matches_filename(self):
        for path in spec_paths():
            with self.subTest(spec=path.name):
                data, _ = parse_frontmatter(path)
                self.assertEqual(
                    path.stem,
                    data["feature"],
                    f"{path.name}: 'feature' should match the filename stem",
                )

    def test_last_verified_is_a_full_sha(self):
        for path in spec_paths():
            with self.subTest(spec=path.name):
                data, _ = parse_frontmatter(path)
                self.assertRegex(
                    data["last_verified"],
                    SHA_RE,
                    f"{path.name}: 'last_verified' should be a 40-character commit sha",
                )

    def test_body_opens_with_what_it_does(self):
        for path in spec_paths():
            with self.subTest(spec=path.name):
                _, body = parse_frontmatter(path)
                body = body.strip()
                self.assertTrue(body, f"{path.name} has no content after its frontmatter")
                self.assertEqual(
                    FIRST_HEADING,
                    body.splitlines()[0].strip(),
                    f"{path.name} should open with '{FIRST_HEADING}'",
                )

    def test_owns_is_a_non_empty_list_of_directory_paths(self):
        for path in spec_paths():
            with self.subTest(spec=path.name):
                data, _ = parse_frontmatter(path)
                self.assertIsInstance(data["owns"], list)
                self.assertTrue(data["owns"], f"{path.name} owns nothing")
                for entry in data["owns"]:
                    self.assertTrue(
                        entry.endswith("/"),
                        f"{path.name}: owned path {entry!r} should end with '/'",
                    )


class SpecsIndexTests(unittest.TestCase):
    def test_index_covers_exactly_the_spec_files_on_disk(self):
        linked = [spec for spec, _ in index_rows()]
        self.assertEqual(
            len(linked), len(set(linked)), "a spec is listed more than once in specs/INDEX.md"
        )
        self.assertEqual(
            set(linked),
            {p.name for p in spec_paths()},
            "specs/INDEX.md and the specs/ directory disagree about which specs exist",
        )

    def test_index_ownership_matches_frontmatter(self):
        for spec, owned in index_rows():
            with self.subTest(spec=spec):
                data, _ = parse_frontmatter(SPECS_DIR / spec)
                self.assertEqual(
                    [entry.rstrip("/") for entry in data["owns"]],
                    owned,
                    f"the 'Owns' column for {spec} in INDEX.md disagrees with its frontmatter",
                )


class SpecsOwnershipTests(unittest.TestCase):
    """Ownership recorded in the specs must line up with the apps that exist."""

    def setUp(self):
        self.owned = {
            entry.rstrip("/")
            for path in spec_paths()
            for entry in parse_frontmatter(path)[0]["owns"]
        }
        self.assertTrue(self.owned, "no owned directories parsed out of the specs")

    def test_each_directory_is_owned_by_exactly_one_spec(self):
        seen = []
        for path in spec_paths():
            seen.extend(entry.rstrip("/") for entry in parse_frontmatter(path)[0]["owns"])
        duplicates = sorted({d for d in seen if seen.count(d) > 1})
        self.assertEqual([], duplicates, f"directories claimed by multiple specs: {duplicates}")

    def test_owned_directories_exist(self):
        for directory in sorted(self.owned):
            with self.subTest(directory=directory):
                self.assertTrue(
                    (BASE_DIR / directory).is_dir(),
                    f"the specs claim ownership of {directory}/ which does not exist",
                )

    def test_every_owned_app_is_installed(self):
        installed = installed_local_apps()
        for app in sorted(self.owned - {PROJECT_PACKAGE}):
            with self.subTest(app=app):
                self.assertIn(
                    app, installed, f"{app}/ is owned by a spec but is not in INSTALLED_APPS"
                )

    def test_every_installed_app_is_owned_by_a_spec(self):
        undocumented = installed_local_apps() - self.owned
        self.assertEqual(
            set(),
            undocumented,
            f"apps in INSTALLED_APPS with no spec covering them: {sorted(undocumented)}. "
            "Document them and add them to specs/INDEX.md.",
        )


if __name__ == "__main__":
    unittest.main()
