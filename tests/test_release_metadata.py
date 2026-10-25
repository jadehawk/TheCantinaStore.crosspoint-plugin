import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_release_metadata import validate


class ReleaseMetadataTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {"name": "pluginhub", "title": "Plugin Hub", "version": "0.1.8"}
        self.device = {"title": "Plugin Hub", "version": "0.1.8"}

    def test_correct_title_and_version(self):
        validate(self.manifest, self.device, "v0.1.8")

    def test_bad_titles_rejected_on_new_releases(self):
        for metadata in (self.manifest, self.device):
            metadata["title"] = "Plugin Hub v0.1.8"
            with self.assertRaisesRegex(ValueError, "no version suffix"):
                validate(self.manifest, self.device, "v0.1.8")
            metadata["title"] = "Plugin Hub"

    def test_mismatched_versions_rejected(self):
        self.device["version"] = "0.1.7"
        with self.assertRaisesRegex(ValueError, "match release tag"):
            validate(self.manifest, self.device, "v0.1.8")

    def test_bad_id_or_tag_rejected(self):
        self.manifest["name"] = "wrong"
        with self.assertRaisesRegex(ValueError, "plugin ID"):
            validate(self.manifest, self.device, "v0.1.8")
        self.manifest["name"] = "pluginhub"
        with self.assertRaisesRegex(ValueError, "invalid release tag"):
            validate(self.manifest, self.device, "0.1.8")

    def test_cantina_store_release_title(self):
        self.manifest.update(title="The Cantina Store", version="0.1.12")
        self.device.update(title="The Cantina Store", version="0.1.12")
        validate(self.manifest, self.device, "v0.1.12")
        self.device["title"] = "Plugin Hub"
        with self.assertRaisesRegex(ValueError, "The Cantina Store"):
            validate(self.manifest, self.device, "v0.1.12")

    def test_side_by_side_identity_required_from_0_1_13(self):
        self.manifest.update(name="thecantinastore", title="The Cantina Store", version="0.1.13")
        self.device.update(title="The Cantina Store", version="0.1.13")
        validate(self.manifest, self.device, "v0.1.13")
        self.manifest["name"] = "pluginhub"
        with self.assertRaisesRegex(ValueError, "thecantinastore"):
            validate(self.manifest, self.device, "v0.1.13")

    def test_distinct_install_package_layout(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/package-release.yml").read_text(encoding="utf-8")
        self.assertIn('asset="thecantinastore-${version}.zip"', workflow)
        self.assertIn('--prefix=".crosspoint/plugins/thecantinastore/"', workflow)
        self.assertNotIn('--prefix=".crosspoint/plugins/pluginhub/"', workflow)

    def test_legacy_tag_remains_repackageable(self):
        self.manifest.update(title="Plugin Hub v0.1.7", version="0.1.7")
        self.device.update(title="Plugin Hub v0.1.7")
        self.device.pop("version", None)
        validate(self.manifest, self.device, "v0.1.7")
