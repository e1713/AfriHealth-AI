from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class DashboardHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.nav_tab_ids = []
        self.section_ids = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if not element_id:
            return
        self.ids.append(element_id)
        if tag == "button" and element_id.startswith("tab-"):
            self.nav_tab_ids.append(element_id.removeprefix("tab-"))
        if tag == "section" and element_id.startswith("sec-"):
            self.section_ids.append(element_id.removeprefix("sec-"))


class DashboardContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (REPOSITORY_ROOT / "index.html").read_text(encoding="utf-8")
        cls.parser = DashboardHTMLParser()
        cls.parser.feed(cls.html)
        cls.alignment = (REPOSITORY_ROOT / "CHALLENGE_ALIGNMENT.md").read_text(encoding="utf-8")
        cls.readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")

    def test_primary_navigation_has_matching_dashboard_and_challenge_views(self):
        self.assertIn("impact", self.parser.nav_tab_ids)
        self.assertIn("challenge", self.parser.nav_tab_ids)
        self.assertIn("followup", self.parser.nav_tab_ids)
        self.assertIn("impact", self.parser.section_ids)
        self.assertIn("challenge", self.parser.section_ids)
        self.assertEqual(set(self.parser.nav_tab_ids), set(self.parser.section_ids))

    def test_html_ids_are_unique(self):
        duplicates = [
            element_id
            for element_id, count in Counter(self.parser.ids).items()
            if count > 1
        ]
        self.assertEqual(duplicates, [])

    def test_impact_values_are_labeled_as_unvalidated_pilot_projections(self):
        self.assertIn("Clinical Impact &amp; Efficiency Dashboard", self.html)
        self.assertIn(
            "Estimated Clinical Workflow Impact (Pilot Projections). "
            "Not validated clinical study findings.",
            self.html,
        )
        for value in ("~5 minutes", "~200 minutes", "~70%", "~15%"):
            with self.subTest(value=value):
                self.assertIn(value, self.html)
        self.assertIn("assumed 40 consultations per workday", self.html)

    def test_voicebot_simulation_has_four_states_and_clear_non_live_boundary(self):
        for state in (
            "Patient Discharged / Intake Completed",
            "Post-Treatment Reminder Scheduled",
            "VoiceBot Adherence Check Triggered (Simulation Workflow)",
            "Follow-Up Status &amp; Flagged Adverse Reactions Log",
        ):
            with self.subTest(state=state):
                self.assertIn(state, self.html)
        self.assertIn("does not schedule or place a real call", self.html)
        self.assertIn("Workflow Simulation — Example adverse-reaction flag", self.html)

    def test_challenge_alignment_and_readme_document_the_evidence_map(self):
        self.assertIn("Sahara CodeSwitch Africa Challenge Alignment", self.html)
        for requirement in (
            "Voice downstream clinical workflows",
            "Three-or-more speech model comparisons",
            "Healthcare category focus",
            "Responsible AI and human review",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, self.alignment)
        self.assertIn("CHALLENGE_ALIGNMENT.md", self.readme)
        self.assertIn("VoiceBot Follow-Up Workflow Demo", self.readme)


if __name__ == "__main__":
    unittest.main()
