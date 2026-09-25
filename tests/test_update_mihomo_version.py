from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "update-mihomo-version.py"
SPEC = importlib.util.spec_from_file_location("update_mihomo_version", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class UpdateMihomoVersionTests(unittest.TestCase):
    def make_checkout(self, readme: str = "image 1.2.3\n") -> Path:
        root = Path(tempfile.mkdtemp())
        (root / ".github/workflows").mkdir(parents=True)
        (root / "scripts").mkdir()
        (root / ".github/workflows/docker-image.yml").write_text(
            'env:\n  DEFAULT_MIHOMO_VERSION: "1.2.3"\n',
            encoding="utf-8",
        )
        (root / "build.sh").write_text("MIHOMO_VERSION=1.2.3\n", encoding="utf-8")
        (root / "README.md").write_text(readme, encoding="utf-8")
        return root

    def test_reads_consistent_version(self) -> None:
        root = self.make_checkout()
        self.assertEqual(MODULE.read_current(root), "1.2.3")

    def test_updates_all_version_copies(self) -> None:
        root = self.make_checkout("image 1.2.3 and 1.2.3-compatible\n")
        self.assertTrue(MODULE.update(root, "1.2.4"))
        self.assertEqual(MODULE.read_current(root), "1.2.4")
        self.assertIn("1.2.4", (root / "build.sh").read_text(encoding="utf-8"))
        self.assertNotIn("1.2.3", (root / "README.md").read_text(encoding="utf-8"))

    def test_same_version_is_idempotent(self) -> None:
        root = self.make_checkout()
        self.assertFalse(MODULE.update(root, "1.2.3"))

    def test_rejects_downgrade(self) -> None:
        root = self.make_checkout()
        with self.assertRaises(ValueError):
            MODULE.update(root, "1.2.2")

    def test_rejects_drift(self) -> None:
        root = self.make_checkout("image 1.2.2\n")
        with self.assertRaises(ValueError):
            MODULE.read_current(root)


if __name__ == "__main__":
    unittest.main()
