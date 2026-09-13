"""Maintainer-only checks; no Docker, network, host changes or runtime packaging.

These deliberately test the agreed draft contract, not the complete CA schema.
Run: python3 -m unittest discover -s tests -v
"""

from copy import deepcopy
from datetime import date
from pathlib import Path
import re
import shlex
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
IMAGE = "ghcr.io/0xshug0/audio.cpp:"
TAGS = ("full-cpu", "full-cuda12", "full-cuda13", "full-vulkan")
BACKENDS = {"full-cpu": "cpu", "full-cuda12": "cuda", "full-cuda13": "cuda",
            "full-vulkan": "vulkan"}
# Every variant runs as 99:100. NVIDIA needs the runtime; Vulkan needs the
# Unraid `video` group (GID 18 in Slackware), which owns /dev/dri by default.
EXTRA_PARAMS = {"full-cpu": "--user=99:100",
                "full-cuda12": "--user=99:100 --runtime=nvidia",
                "full-cuda13": "--user=99:100 --runtime=nvidia",
                "full-vulkan": "--user=99:100 --group-add=18"}
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
    nvidia = BACKENDS[tag] == "cuda"
    vulkan = BACKENDS[tag] == "vulkan"
    assert shlex.split(root.findtext("PostArgs", "")) == shlex.split(
        LAUNCH + BACKENDS[tag]
    ), "Unexpected application tuning or startup code"
    assert root.findtext("ExtraParams", "") == EXTRA_PARAMS[tag], (
        "Unexpected Docker runtime options")
    configs = root.findall("Config")
    keyed = {(field.get("Type"), field.get("Target")): field for field in configs}
    assert len(keyed) == len(configs), "Duplicate configuration target"
    expected = {("Port", "8080"), ("Path", "/app/models")}
    if nvidia:
        expected |= {
            ("Variable", "NVIDIA_VISIBLE_DEVICES"),
            ("Variable", "NVIDIA_DRIVER_CAPABILITIES"),
        }
    if vulkan:
        expected |= {("Device", "/dev/dri")}
    assert set(keyed) == expected, "Missing shared field or unsupported variable/mount"
    for field in configs:
        assert field.get("Required") == "true"
        assert field.get("Mask") == "false"
        assert field.get("Display") in ("always", "advanced")
        assert field.text == field.get("Default"), "Inconsistent initial defaults"
        assert field.get("Description"), "Missing setup guidance"
    port = keyed[("Port", "8080")]
    assert port.get("Mode") == "tcp" and port.text == "6969"
    models = keyed[("Path", "/app/models")]
    assert models.get("Mode") == "rw"
    assert models.text == "/mnt/user/appdata/audio-cpp/models"
    if nvidia:
        assert keyed[("Variable", "NVIDIA_VISIBLE_DEVICES")].text == "all"
        assert keyed[("Variable", "NVIDIA_DRIVER_CAPABILITIES")].text == "compute,utility"
    if vulkan:
        assert keyed[("Device", "/dev/dri")].text == "/dev/dri"
        assert "llvmpipe" in keyed[("Device", "/dev/dri")].get("Description")
        assert "NVIDIA" in root.findtext("Requires"), "Say the variant excludes NVIDIA"


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

    def test_every_resolved_variant_is_complete(self):
        resolved = list(variants(self.root))
        self.assertEqual([tag for tag, _ in resolved], list(TAGS))
        for tag, root in resolved:
            with self.subTest(variant=tag):
                validate_variant(tag, root)

    def test_host_port_default_and_container_port_are_distinct(self):
        for tag, root in variants(self.root):
            with self.subTest(variant=tag):
                port = root.find("Config[@Type='Port']")
                self.assertEqual(port.get("Default"), "6969")
                self.assertEqual(port.text, "6969")
                self.assertEqual(port.get("Target"), "8080")
                self.assertEqual(root.findtext("WebUI"), "http://[IP]:[PORT:8080]/")
                args = shlex.split(root.findtext("PostArgs"))
                self.assertEqual(args[args.index("--port") + 1], "8080")
        for name in ("README.md", "docs/CONFIGURATION.md"):
            self.assertIn("`6969`", (ROOT / name).read_text(), name)

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

    def test_deployment_icon_is_256_pixel_png(self):
        import struct
        import zlib
        data = (ROOT / "assets/icon.png").read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        offset = 8
        chunks = []
        while offset < len(data):
            size = struct.unpack(">I", data[offset:offset + 4])[0]
            kind = data[offset + 4:offset + 8]
            payload = data[offset + 8:offset + 8 + size]
            crc = struct.unpack(">I", data[offset + 8 + size:offset + 12 + size])[0]
            self.assertEqual(crc, zlib.crc32(kind + payload))
            self.assertIn(kind, (b"IHDR", b"bKGD", b"IDAT", b"IEND"))
            chunks.append(kind)
            if kind == b"IHDR":
                self.assertEqual(struct.unpack(">II", payload[:8]), (256, 256))
            offset += 12 + size
        self.assertEqual(offset, len(data))
        self.assertEqual(chunks[0], b"IHDR")
        self.assertIn(b"IDAT", chunks)
        self.assertEqual(chunks[-1], b"IEND")
        for tag, root in variants(self.root):
            with self.subTest(variant=tag):
                self.assertTrue(root.findtext("Icon").endswith("/assets/icon.png"))

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

    def test_changes_field_has_dated_markdown_entries(self):
        """CA shows this field as the app changelog; it is the only channel to
        installed users, because Docker Manager never refreshes templates."""
        changes = self.root.findtext("Changes", "")
        lines = [line.strip() for line in changes.strip().splitlines()]
        self.assertTrue(lines and lines[0].startswith("### "), "Start with a ### date heading")
        headings = [line[4:] for line in lines if line.startswith("### ")]
        for heading in headings:
            date.fromisoformat(heading)
        self.assertEqual(headings, sorted(headings, reverse=True), "Newest entry first")
        for line in lines:
            self.assertTrue(re.fullmatch(r"### \S+|- .+", line), f"Unexpected line: {line!r}")
        for tag, resolved in variants(self.root):
            with self.subTest(variant=tag):
                self.assertEqual(resolved.findtext("Changes"), changes)

    def test_documented_release_gate(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("lozenge0/audio-cpp-unraid", readme)
        self.assertIn("Beta integration", readme)
        self.assertIn("docs/RELEASE-REVIEW.md", readme)
        self.assertTrue((ROOT / "docs/VALIDATION.md").is_file())
        self.assertIn("MIT License", (ROOT / "LICENSE").read_text())

    def test_ai_category_and_beta_flag(self):
        for tag, resolved in variants(self.root):
            with self.subTest(variant=tag):
                self.assertEqual(resolved.findtext("Category").split(), ["AI", "Tools:"])
                self.assertEqual(resolved.findtext("Beta"), "true")

    def test_selected_publication_destinations(self):
        base = "https://github.com/lozenge0/audio-cpp-unraid"
        raw = "https://raw.githubusercontent.com/lozenge0/audio-cpp-unraid/main/"
        self.assertEqual(self.root.findtext("Support"), base + "/issues")
        self.assertEqual(self.root.findtext("TemplateURL"), raw + "templates/audio-cpp.xml")
        self.assertEqual(self.root.findtext("ReadMe"), raw + "README.md")
        self.assertEqual(self.root.findtext("Icon"), raw + "assets/icon.png")
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
                    rest = EXTRA_PARAMS[tag].replace("--user=99:100", "", 1)
                    bad.find("ExtraParams").text = (user + rest).strip()
                    with self.assertRaisesRegex(AssertionError, "runtime options"):
                        validate_variant(tag, bad)

    def test_vulkan_variant_has_no_nvidia_settings_and_cuda_has_no_device(self):
        for tag, root in variants(self.root):
            with self.subTest(variant=tag):
                if BACKENDS[tag] == "vulkan":
                    self.assertNotIn("nvidia", root.findtext("ExtraParams"))
                    self.assertNotIn("nvidia", root.findtext("PostArgs"))
                    targets = [field.get("Target") for field in root.findall("Config")]
                    self.assertFalse([t for t in targets if t.startswith("NVIDIA")])
                else:
                    self.assertIsNone(root.find("Config[@Type='Device']"))
                    self.assertNotIn("--group-add", root.findtext("ExtraParams"))

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
