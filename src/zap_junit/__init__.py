import json
import sys
from datetime import datetime
from typing import Any
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent

import click


__version__ = "0.1.1"


RISK_LEVELS = {
    "0": "informational",
    "1": "low",
    "2": "medium",
    "3": "high",
}


def parse_datetime(date_str: str) -> str:
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except (ValueError, AttributeError):
        return date_str


def create_junit_xml(zap_data: dict[str, Any]) -> Element:
    root = Element("testsuites")
    root.set("name", zap_data.get("@programName", "ZAP"))
    root.set("version", zap_data.get("@version", ""))
    root.set("generated", parse_datetime(zap_data.get("@generated", "")))

    tests = 0
    failures = 0
    errors = 0

    sites = zap_data.get("site", [])

    for site in sites:
        site_name = site.get("@name", "unknown")
        suite = SubElement(root, "testsuite")
        suite.set("name", site_name)
        suite.set("hostname", site.get("@host", ""))
        suite.set("port", site.get("@port", ""))

        alerts = site.get("alerts", [])

        for alert in alerts:
            test_case = SubElement(suite, "testcase")
            alert_ref = alert.get("alertRef", "")
            test_case.set("classname", alert_ref)
            test_case.set("name", alert.get("alert", "Unknown Alert"))

            risk_code = alert.get("riskcode", "0")
            risk_level = RISK_LEVELS.get(risk_code, "informational")

            if risk_level in ("medium", "high"):
                failure = SubElement(test_case, "failure")
                failure.set("type", risk_level)
                failure.set("message", alert.get("riskdesc", ""))

                desc_text = _strip_html(alert.get("desc", ""))
                failure.text = desc_text

                instances = alert.get("instances", [])
                if instances:
                    failure.text += "\n\nAffected URLs:"
                    for inst in instances:
                        uri = inst.get("uri", "")
                        method = inst.get("method", "GET")
                        failure.text += f"\n  - {method} {uri}"

                failures += 1
            elif risk_level == "low":
                error = SubElement(test_case, "error")
                error.set("type", risk_level)
                error.set("message", alert.get("riskdesc", ""))
                desc_text = _strip_html(alert.get("desc", ""))
                error.text = desc_text
                errors += 1

            tests += 1

        suite.set("tests", str(len(alerts)))
        suite.set("failures", str(failures))
        suite.set("errors", str(errors))

    root.set("tests", str(tests))
    root.set("failures", str(failures))
    root.set("errors", str(errors))

    return root


def _strip_html(text: str) -> str:
    import re
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&#xA;", "\n", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&quot;", '"', text)
    return text.strip()


def convert(input_path: str, output_path: str | None = None) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        zap_data = json.load(f)

    tree = create_junit_xml(zap_data)
    indent(tree, "  ")

    output = output_path or input_path.replace(".json", "-junit.xml")

    ElementTree(tree).write(output, encoding="unicode", xml_declaration=True)


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", "output_file", type=click.Path(), help="Output file path")
@click.version_option(version=__version__)
def main(input_file: str, output_file: str | None) -> None:
    """Convert ZAP JSON report to JUnit XML format."""
    convert(input_file, output_file)
    click.echo(f"Converted {input_file} to {output_file or input_file.replace('.json', '-junit.xml')}")


if __name__ == "__main__":
    main()
