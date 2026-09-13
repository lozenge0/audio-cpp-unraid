"""Maintainer-only checks; no Docker, network, host changes or runtime packaging.

These deliberately test the agreed draft contract, not the complete CA schema.
Run: python3 -m unittest discover -s tests -v
"""

from copy import deepcopy
from pathlib import Path
import shlex
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
IMAGE = "ghcr.io/0xshug0/audio.cpp:"
TAGS = ("full-cpu", "full-cuda12", "full-cuda13")
LAUNCH = "server --ui --ui-management --host 0.0.0.0 --port 8080 --backend "


def variants(root):
    """Model the reviewed CA wholesale field override, not CA validation itself."""
    base = deepcopy(root)
    for branch in list(base.findall("Branch")):
        base.remove(branch)
    yield "full-cpu", base
    for branch in root.findall("Branch"):
        resolved = deepcopy(base)
        keys = {child.tag for child in branch} - {"Tag", "TagDescription"}
        for key in keys:
            for old in list(resolved.findall(key)):
                resolved.remove(old)
            for child in branch.findall(key):
                resolved.append(deepcopy(child))
        yield branch.findtext("Tag"), resolved


def validate_variant(tag, root):
    """Reject deviations from the intentionally minimal upstream-only draft."""
    assert tag in TAGS, "Unsupported image variant"
    assert root.findtext("Repository") == IMAGE + tag, "Not a moving upstream image"
    assert root.findtext("Network") == "bridge"
    assert root.findtext("Privileged") == "false"
    assert root.findtext("WebUI") == "http://[IP]:[PORT:8080]/"
    gpu = tag != "full-cpu"
    expected_backend = "cuda" if gpu else "cpu"
    assert shlex.split(root.findtext("PostArgs", "")) == shlex.split(
        LAUNCH + expected_backend
    ), "Unexpected application tuning or startup code"
    assert root.findtext("ExtraParams", "") == (
        "--user=99:100 --runtime=nvidia" if gpu else "--user=99:100"
    ), "Unexpected Docker runtime options"
    configs = root.findall("Config")
    keyed = {(field.get("Type"), field.get("Target")): field for field in configs}
    assert len(keyed) == len(configs), "Duplicate configuration target"
    expected = {("Port", "8080"), ("Path", "/app/models")}
    if gpu:
        expected |= {
            ("Variable", "NVIDIA_VISIBLE_DEVICES"),
            ("Variable", "NVIDIA_DRIVER_CAPABILITIES"),
        }
    assert set(keyed) == expected, "Missing shared field or unsupported variable/mount"
    for field in configs:
        assert field.get("Required") == "true"
        assert field.get("Mask") == "false"
        assert field.get("Display") in ("always", "advanced")
        assert field.text == field.get("Default"), "Inconsistent initial defaults"
        assert field.get("Description"), "Missing setup guidance"
    port = keyed[("Port", "8080")]
    assert port.get("Mode") == "tcp" and port.text == "8080"
    models = keyed[("Path", "/app/models")]
    assert models.get("Mode") == "rw"
    assert models.text == "/mnt/user/appdata/audio-cpp/models"
    if gpu:
        assert keyed[("Variable", "NVIDIA_VISIBLE_DEVICES")].text == "all"
        assert keyed[("Variable", "NVIDIA_DRIVER_CAPABILITIES")].text == "compute,utility"


class TemplateTests(unittest.TestCase):
    def setUp(self):
        self.root = ET.parse(ROOT / "templates/audio-cpp.xml").getroot()

    def test_v2_metadata(self):
        self.assertEqual(self.root.tag, "Container")
        self.assertEqual(self.root.get("version"), "2")
        self.assertEqual(self.root.findtext("Name"), "audio-cpp")
        for tag in ("Overview", "Requires", "Category", "Project", "Support",
                    "Icon", "TemplateURL", "ReadMe", "DefaultTagDescription"):
            self.assertTrue(self.root.findtext(tag), tag)
        self.assertEqual(self.root.findtext("Project"), "https://github.com/0xShug0/audio.cpp")

    def test_three_complete_resolved_variants(self):
        resolved = list(variants(self.root))
        self.assertEqual([tag for tag, _ in resolved], list(TAGS))
        for tag, root in resolved:
            with self.subTest(variant=tag):
                validate_variant(tag, root)

    def test_branch_labels_and_shared_fields(self):
        shared = [ET.tostring(field) for field in self.root.findall("Config")]
        for branch in self.root.findall("Branch"):
            self.assertTrue(branch.findtext("TagDescription"))
            fields = branch.findall("Config")
            self.assertEqual([ET.tostring(field).strip() for field in fields[:2]],
                             [value.strip() for value in shared])

    def test_no_personal_values_in_deployable_metadata(self):
        payload = (ROOT / "templates/audio-cpp.xml").read_text() + (
            ROOT / "ca_profile.xml").read_text()
        for token in ("192.168.", "GPU-", "/Users/", "speak.sh", "pocket-tts",
                      "alba", "/mnt/user/appdata/audio.cpp", "@sha256:", "PUID\""):
            self.assertNotIn(token, payload)

    def test_profile(self):
        profile = ET.parse(ROOT / "ca_profile.xml").getroot()
        self.assertEqual(profile.tag, "CommunityApplications")
        self.assertTrue(profile.findtext("Profile"))
        self.assertEqual(profile.findtext("Icon"), self.root.findtext("Icon"))

    def test_icon_is_self_contained_svg(self):
        icon = ET.parse(ROOT / "assets/icon.svg").getroot()
        self.assertEqual(icon.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertEqual(icon.get("viewBox"), "0 0 180 180")
        for element in icon.iter():
            local_tag = element.tag.split("}")[-1]
            self.assertNotIn(local_tag, ("script", "image", "text", "foreignObject"))
            for key, value in element.attrib.items():
                if key.split("}")[-1] == "href":
                    self.assertTrue(value.startswith("#"), "External asset reference")

    def test_only_repository_assets_not_runtime_payload(self):
        allowed = {".gitignore", ".github", "README.md", "LICENSE", "CHANGELOG.md",
                   "CONTRIBUTING.md", "SECURITY.md",
                   "ca_profile.xml", "assets", "templates", "docs", "tests", ".git"}
        self.assertTrue({item.name for item in ROOT.iterdir()} <= allowed)
        self.assertEqual([p.name for p in (ROOT / "templates").iterdir()], ["audio-cpp.xml"])

    def test_documented_release_gate(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("lozenge0/audio-cpp-unraid", readme)
        self.assertIn("beta integration", readme)
        self.assertIn("full deployment acceptance pending", readme)
        self.assertTrue((ROOT / "docs/PLAN.md").is_file())
        self.assertTrue((ROOT / "docs/VALIDATION.md").is_file())
        self.assertIn("MIT License", (ROOT / "LICENSE").read_text())

    def test_ai_category_and_honest_beta_status(self):
        for tag, resolved in variants(self.root):
            with self.subTest(variant=tag):
                self.assertEqual(resolved.findtext("Category").split(), ["AI", "Tools:"])
                self.assertEqual(resolved.findtext("Beta"), "true")
                self.assertIn("full deployment acceptance remain pending", resolved.findtext("Overview"))
                self.assertNotIn("Not ready for public submission", resolved.findtext("Overview"))
        self.assertNotIn("not yet submitted", (ROOT / "ca_profile.xml").read_text())

    def test_selected_publication_destinations(self):
        base = "https://github.com/lozenge0/audio-cpp-unraid"
        raw = "https://raw.githubusercontent.com/lozenge0/audio-cpp-unraid/main/"
        self.assertEqual(self.root.findtext("Support"), base + "/issues")
        self.assertEqual(self.root.findtext("TemplateURL"), raw + "templates/audio-cpp.xml")
        self.assertEqual(self.root.findtext("ReadMe"), raw + "README.md")
        self.assertEqual(self.root.findtext("Icon"), raw + "assets/icon.svg")
        profile = ET.parse(ROOT / "ca_profile.xml").getroot()
        self.assertEqual(profile.findtext("WebPage"), base)
        for path in (ROOT / "templates/audio-cpp.xml", ROOT / "ca_profile.xml"):
            self.assertNotIn("REPLACE_WITH", path.read_text())

    def test_rejects_tag_backend_mismatch(self):
        bad = deepcopy(self.root)
        bad.find("Repository").text = IMAGE + "full-cuda12"
        with self.assertRaises(AssertionError):
            validate_variant("full-cpu", bad)

    def test_rejects_partial_branch_config(self):
        bad = deepcopy(self.root)
        branch = bad.find("Branch")
        branch.remove(branch.find("Config"))
        tag, resolved = list(variants(bad))[1]
        with self.assertRaisesRegex(AssertionError, "Missing shared field"):
            validate_variant(tag, resolved)

    def test_rejects_custom_runtime_wrapper(self):
        bad = deepcopy(self.root)
        bad.find("ExtraParams").text = "--entrypoint=/bin/sh"
        with self.assertRaisesRegex(AssertionError, "runtime options"):
            validate_variant("full-cpu", bad)

    def test_rejects_missing_or_changed_user_for_every_variant(self):
        for tag, root in variants(self.root):
            for user in ("", "--user=0:0", "--user=1000:1000", "--user=99:99"):
                with self.subTest(variant=tag, user=user):
                    bad = deepcopy(root)
                    bad.find("ExtraParams").text = " ".join(filter(None, (
                        user, "--runtime=nvidia" if tag != "full-cpu" else ""
                    )))
                    with self.assertRaisesRegex(AssertionError, "runtime options"):
                        validate_variant(tag, bad)

    def test_rejects_unsupported_identity_environment_variables(self):
        for tag, root in variants(self.root):
            for variable in ("PUID", "PGID"):
                with self.subTest(variant=tag, variable=variable):
                    bad = deepcopy(root)
                    ET.SubElement(bad, "Config", Type="Variable", Target=variable)
                    with self.assertRaisesRegex(AssertionError, "unsupported variable"):
                        validate_variant(tag, bad)

    def test_identity_is_explained_in_every_variant(self):
        for tag, root in variants(self.root):
            with self.subTest(variant=tag):
                self.assertIn("UID 99/GID 100", root.findtext("Requires"))
                models = next(field for field in root.findall("Config")
                              if field.get("Target") == "/app/models")
                self.assertIn("UID 99/GID 100", models.get("Description"))
                self.assertIn("PUID/PGID are not supported", models.get("Description"))

    def test_rejects_personal_tuning(self):
        bad = deepcopy(self.root)
        bad.find("PostArgs").text += " --threads 4 --idle-unload-ms 300000"
        with self.assertRaisesRegex(AssertionError, "application tuning"):
            validate_variant("full-cpu", bad)


if __name__ == "__main__":
    unittest.main()
