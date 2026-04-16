import json
import os
import tempfile

from zap_junit import convert, create_junit_xml, _strip_html


SAMPLE_ZAP_DATA = {
    "@programName": "ZAP",
    "@version": "2.17.0",
    "@generated": "Wed, 15 Apr 2026 12:27:01",
    "site": [
        {
            "@name": "http://example.com",
            "@host": "example.com",
            "@port": "443",
            "@ssl": "true",
            "alerts": [
                {
                    "alertRef": "10038-1",
                    "alert": "Content Security Policy Header Not Set",
                    "name": "Content Security Policy Header Not Set",
                    "riskcode": "2",
                    "confidence": "3",
                    "riskdesc": "Medium (High)",
                    "desc": "<p>CSP is important.</p>",
                    "instances": [
                        {"uri": "https://example.com", "method": "GET"}
                    ],
                    "count": "1",
                    "solution": "Set CSP header."
                },
                {
                    "alertRef": "90004-1",
                    "alert": "Low Risk Alert",
                    "name": "Low Risk Alert",
                    "riskcode": "1",
                    "confidence": "2",
                    "riskdesc": "Low (Medium)",
                    "desc": "Low risk issue.",
                    "instances": [],
                    "count": "0"
                },
                {
                    "alertRef": "10049-1",
                    "alert": "Informational Alert",
                    "name": "Informational Alert",
                    "riskcode": "0",
                    "confidence": "2",
                    "riskdesc": "Informational (Medium)",
                    "desc": "Info only.",
                    "instances": [],
                    "count": "0"
                }
            ]
        }
    ]
}


class TestStripHtml:
    def test_strips_simple_tags(self):
        assert _strip_html("<p>Hello</p>") == "Hello"

    def test_strips_nested_tags(self):
        assert _strip_html("<p><strong>Bold</strong> text</p>") == "Bold text"

    def test_handles_empty_string(self):
        assert _strip_html("") == ""

    def test_handles_plain_text(self):
        assert _strip_html("Plain text without tags") == "Plain text without tags"

    def test_decodes_html_entities(self):
        assert _strip_html("&amp; &lt; &gt; &quot;") == '& < > "'


class TestCreateJunitXml:
    def test_creates_root_testsuites(self):
        root = create_junit_xml(SAMPLE_ZAP_DATA)
        assert root.tag == "testsuites"
        assert root.get("name") == "ZAP"
        assert root.get("version") == "2.17.0"

    def test_creates_testsuite_per_site(self):
        root = create_junit_xml(SAMPLE_ZAP_DATA)
        suites = root.findall("testsuite")
        assert len(suites) == 1
        assert suites[0].get("name") == "http://example.com"

    def test_medium_risk_becomes_failure(self):
        root = create_junit_xml(SAMPLE_ZAP_DATA)
        suite = root.find("testsuite")
        failures = suite.findall("testcase/failure")
        assert len(failures) == 1
        assert failures[0].get("type") == "medium"

    def test_low_risk_becomes_error(self):
        root = create_junit_xml(SAMPLE_ZAP_DATA)
        suite = root.find("testsuite")
        errors = suite.findall("testcase/error")
        assert len(errors) == 1
        assert errors[0].get("type") == "low"

    def test_informational_has_no_failure_or_error(self):
        root = create_junit_xml(SAMPLE_ZAP_DATA)
        suite = root.find("testsuite")
        testcases = suite.findall("testcase")
        informational = [tc for tc in testcases if tc.get("name") == "Informational Alert"][0]
        assert informational.find("failure") is None
        assert informational.find("error") is None

    def test_counts_are_correct(self):
        root = create_junit_xml(SAMPLE_ZAP_DATA)
        assert root.get("tests") == "3"
        assert root.get("failures") == "1"
        assert root.get("errors") == "1"

    def test_empty_sites(self):
        empty_data = {"@programName": "ZAP", "site": []}
        root = create_junit_xml(empty_data)
        assert root.get("tests") == "0"
        assert root.get("failures") == "0"
        assert root.get("errors") == "0"


class TestConvert:
    def test_writes_valid_xml_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(SAMPLE_ZAP_DATA, f)
            json_path = f.name

        xml_path = json_path.replace(".json", "-junit.xml")

        try:
            convert(json_path, xml_path)

            assert os.path.exists(xml_path)
            with open(xml_path) as f:
                content = f.read()
            assert '<?xml version' in content
            assert "<testsuites" in content
            assert "<testsuite" in content
        finally:
            os.unlink(json_path)
            if os.path.exists(xml_path):
                os.unlink(xml_path)

    def test_generates_default_output_path(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(SAMPLE_ZAP_DATA, f)
            json_path = f.name

        expected_xml_path = json_path.replace(".json", "-junit.xml")

        try:
            convert(json_path)
            assert os.path.exists(expected_xml_path)
        finally:
            os.unlink(json_path)
            if os.path.exists(expected_xml_path):
                os.unlink(expected_xml_path)
