from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "check-image-tags.py"
SPEC = importlib.util.spec_from_file_location("check_image_tags", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CheckImageTagsTests(unittest.TestCase):
    @patch.object(MODULE, "_registry_token", return_value="token")
    @patch.object(
        MODULE,
        "_manifest_digest",
        side_effect=lambda repository, tag, token: {
            "1.2.3": "sha256:stable",
            "1.2.3-compatible": "sha256:compatible",
            "latest": "sha256:stable",
        }[tag],
    )
    def test_complete_tags_need_no_publish(self, _manifest, _token) -> None:
        result = MODULE.check("ghcr.io/example/image", "1.2.3")
        self.assertFalse(result["publish_needed"])
        self.assertEqual(result["missing"], [])

    @patch.object(MODULE, "_registry_token", return_value="token")
    @patch.object(
        MODULE,
        "_manifest_digest",
        side_effect=lambda repository, tag, token: {
            "1.2.3": "sha256:stable",
            "1.2.3-compatible": None,
            "latest": "sha256:old",
        }[tag],
    )
    def test_missing_or_stale_tags_need_publish(self, _manifest, _token) -> None:
        result = MODULE.check("ghcr.io/example/image", "1.2.3")
        self.assertTrue(result["publish_needed"])
        self.assertEqual(result["missing"], ["1.2.3-compatible", "latest (stale)"])


if __name__ == "__main__":
    unittest.main()
