"""Unit tests for the pure helpers in validate_marketplace.py."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import validate_marketplace as vm  # noqa: E402


def two_plugin_data() -> dict:
    """beta owns whoami + recommend-study-filters; stable owns whoami."""
    return {
        "metadata": {"version": "0.5.0"},
        "plugins": [
            {
                "name": "prolific-beta-skills",
                "version": "0.5.0",
                "skills": ["./skills/whoami", "./skills/recommend-study-filters"],
            },
            {
                "name": "prolific-stable-skills",
                "version": "0.2.0",
                "skills": ["./skills/whoami"],
            },
        ],
    }


# Versions at the previous release tag.
PREV = {"prolific-beta-skills": "0.4.0", "prolific-stable-skills": "0.2.0"}


class TestSkillFolderName(unittest.TestCase):
    def test_strips_prefix_and_trailing_slash(self):
        self.assertEqual(vm.skill_folder_name("./skills/whoami"), "whoami")
        self.assertEqual(vm.skill_folder_name("skills/whoami/"), "whoami")


class TestPluginSkillFolders(unittest.TestCase):
    def test_collects_owned_folders(self):
        plugin = two_plugin_data()["plugins"][0]
        self.assertEqual(
            vm.plugin_skill_folders(plugin),
            {"whoami", "recommend-study-filters"},
        )


class TestParseSemver(unittest.TestCase):
    def test_orders_by_numeric_core(self):
        self.assertGreater(vm.parse_semver("0.5.0"), vm.parse_semver("0.4.0"))
        self.assertGreater(vm.parse_semver("0.2.1"), vm.parse_semver("0.2.0"))
        self.assertEqual(vm.parse_semver("0.5.0"), vm.parse_semver("0.5.0"))

    def test_unparsable_is_lowest(self):
        self.assertEqual(vm.parse_semver("nope"), (-1, -1, -1))


class TestPluginBumpErrors(unittest.TestCase):
    def test_changed_plugin_strictly_increased_is_ok(self):
        # beta owns recommend-study-filters (changed), 0.4.0 -> 0.5.0
        errs = vm.plugin_bump_errors(
            two_plugin_data(), PREV, {"recommend-study-filters"}
        )
        self.assertEqual(errs, [])

    def test_unchanged_plugin_kept_is_ok(self):
        # only a beta-only skill changed; stable stays at 0.2.0 -> no error
        errs = vm.plugin_bump_errors(
            two_plugin_data(), PREV, {"recommend-study-filters"}
        )
        self.assertEqual(errs, [])

    def test_changed_plugin_not_bumped_is_an_error(self):
        # whoami changed -> stable owns it but stayed at 0.2.0 == prev
        errs = vm.plugin_bump_errors(two_plugin_data(), PREV, {"whoami"})
        self.assertEqual(len(errs), 1)
        self.assertIn("prolific-stable-skills", errs[0])

    def test_unchanged_plugin_bumped_is_an_error(self):
        data = two_plugin_data()
        data["plugins"][1]["version"] = "0.3.0"  # stable moved without changes
        errs = vm.plugin_bump_errors(data, PREV, {"recommend-study-filters"})
        self.assertEqual(len(errs), 1)
        self.assertIn("prolific-stable-skills", errs[0])

    def test_new_plugin_without_previous_is_skipped(self):
        data = two_plugin_data()
        errs = vm.plugin_bump_errors(
            data, {"prolific-beta-skills": "0.4.0"}, {"whoami"}
        )
        self.assertEqual(errs, [])


class TestStrictErrors(unittest.TestCase):
    def test_clean_release_has_no_errors(self):
        errs = vm.strict_errors(
            two_plugin_data(),
            changelog_version="0.5.0",
            prev_versions=PREV,
            changed_folders={"recommend-study-filters"},
            tag_already_exists=False,
        )
        self.assertEqual(errs, [])

    def test_metadata_mismatch_reported(self):
        errs = vm.strict_errors(
            two_plugin_data(), "0.6.0", PREV, {"recommend-study-filters"}, False
        )
        self.assertTrue(any("metadata.version" in e for e in errs))

    def test_existing_tag_reported(self):
        errs = vm.strict_errors(
            two_plugin_data(), "0.5.0", PREV, set(), tag_already_exists=True
        )
        self.assertTrue(any("already exists" in e for e in errs))


class TestSharedMappingForBump(unittest.TestCase):
    """Locks the contract bump_release.py reuses for plugin↔skill mapping."""

    def test_only_owning_plugins_match_changed_folder(self):
        plugins = two_plugin_data()["plugins"]
        owning = [
            p["name"]
            for p in plugins
            if vm.plugin_skill_folders(p) & {"recommend-study-filters"}
        ]
        self.assertEqual(owning, ["prolific-beta-skills"])


if __name__ == "__main__":
    unittest.main()
