"""
ARIA Custom Test Reporter
Provides color-coded, phase-grouped output for mission verification.

Writes all output to stderr so check-work.sh can discard pytest's
default stdout while preserving our formatted display.
"""
import os
import pytest
import sys

# -- Phase and test name mappings -------------------------------------------

PHASES = {
    "TestPlaybookStructure":  ("1", "OPORD Structure"),
    "TestVariablesAndTemplates": ("2", "Variables & Templates"),
    "TestMultiOSCompliance":  ("3", "Multi-OS Compliance"),
    "TestFirewall":           ("4", "Firewall"),
    "TestIdempotency":        ("5", "Idempotency"),
}

FRIENDLY = {
    "test_playbook_exists":             "Playbook file exists",
    "test_playbook_is_valid_yaml":      "Playbook is valid YAML",
    "test_playbook_has_tasks":          "Playbook contains sufficient tasks",
    "test_playbook_uses_variables":     "Playbook uses variables (not hardcoded)",
    "test_group_vars_defined":          "group_vars files contain variables",
    "test_sshd_template_exists":        "sshd_config.j2 template exists",
    "test_motd_template_exists":        "motd.j2 template exists",
    "test_ssh_hardened_ubuntu":         "SSH hardened on Ubuntu nodes",
    "test_ssh_hardened_rocky":          "SSH hardened on Rocky Linux node",
    "test_motd_deployed":               "Login banner deployed on all nodes",
    "test_firewall_ubuntu":             "Firewall active on Ubuntu nodes",
    "test_firewall_rocky":              "Firewall active on Rocky Linux node",
    "test_playbook_is_idempotent":      "Playbook is idempotent (changed=0)",
}

# -- Reporter ---------------------------------------------------------------

# The phase-oriented summary is rendered by the shared `aria-reporter`
# pytest plugin (installed via requirements.txt); this file only declares
# the mission's phases + friendly objective names.
from aria_reporter import configure  # noqa: E402

configure(phases=PHASES, friendly=FRIENDLY, mission_id="1-4")
