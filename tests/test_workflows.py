"""The workflows pin action majors that run on Node 24, and Dependabot keeps them current.

The Node 20 majors (checkout@v4, upload-artifact@v4, download-artifact@v4 and their
kin) draw a deprecation warning on every run and stop working when the runners drop
Node 20. The floors below are the majors these workflows moved to; each one's
action.yml declares node24, and upload-artifact@v7 pairs with download-artifact@v8.
"""

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
NODE24_FLOOR = {
    "actions/checkout": 6,
    "actions/setup-python": 6,
    "actions/upload-artifact": 7,
    "actions/download-artifact": 8,
    "actions/upload-pages-artifact": 5,
    "actions/deploy-pages": 5,
}
PIN = re.compile(r"^(?P<action>[\w.-]+/[\w.-]+)@v(?P<major>\d+)")


def floored_pins():
    """Yield (workflow, action, major) for every step whose action has a floor."""
    for workflow in WORKFLOWS:
        for job in yaml.safe_load(workflow.read_text())["jobs"].values():
            for step in job.get("steps", []):
                match = PIN.match(step.get("uses", ""))
                if match and match["action"] in NODE24_FLOOR:
                    yield workflow.name, match["action"], int(match["major"])


def test_the_workflows_use_floored_actions():
    assert list(floored_pins())


@pytest.mark.parametrize("workflow, action, major", list(floored_pins()))
def test_action_majors_run_on_node24(workflow, action, major):
    assert major >= NODE24_FLOOR[action], f"{workflow}: {action}@v{major}"


def test_dependabot_updates_github_actions_weekly():
    config = yaml.safe_load((ROOT / ".github" / "dependabot.yml").read_text())
    assert config["version"] == 2
    actions = [u for u in config["updates"] if u["package-ecosystem"] == "github-actions"]
    assert len(actions) == 1
    assert actions[0]["directory"] == "/"
    assert actions[0]["schedule"]["interval"] == "weekly"
