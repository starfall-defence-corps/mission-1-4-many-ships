"""
=== STARFALL DEFENCE CORPS ACADEMY ===
ARIA Automated Verification - Mission 1.4: One Playbook, Many Ships
====================================================================
"""
import os
import re
import subprocess
import yaml
import pytest


def _root_dir():
    """Return the mission root directory."""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(tests_dir, "..", "..", ".."))


def _workspace_dir():
    return os.path.join(_root_dir(), "workspace")


def _playbook_path():
    return os.path.join(_workspace_dir(), "playbook.yml")


def _load_playbook():
    path = _playbook_path()
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def _run_ansible(*args, **kwargs):
    """Run an ansible command from the workspace directory."""
    timeout = kwargs.pop("timeout", 90)
    result = subprocess.run(
        list(args),
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=_workspace_dir(),
    )
    return result


def _count_real_tasks(data):
    """Count non-empty tasks in the first play."""
    if not data or not isinstance(data, list) or len(data) == 0:
        return 0
    play = data[0]
    tasks = play.get("tasks") or []
    return len([t for t in tasks if t])


def _playbook_text():
    """Read the raw playbook text."""
    path = _playbook_path()
    if not os.path.isfile(path):
        return ""
    with open(path) as f:
        return f.read()


# -------------------------------------------------------------------
# Phase 1: Playbook structure
# -------------------------------------------------------------------

class TestPlaybookStructure:
    """ARIA verifies: Has the cadet written a valid OPORD?"""

    def test_playbook_exists(self):
        """Playbook file must exist at workspace/playbook.yml"""
        assert os.path.isfile(_playbook_path()), (
            "ARIA: No playbook detected at workspace/playbook.yml. "
            "Cadet, one playbook to rule them all. Create it."
        )

    def test_playbook_is_valid_yaml(self):
        """Playbook must be valid YAML"""
        path = _playbook_path()
        if not os.path.isfile(path):
            pytest.skip("Playbook does not exist yet")
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data is not None, (
            "ARIA: Playbook is empty. Corporal Copy-Paste had 47 "
            "playbooks. You need at least one."
        )

    def test_playbook_has_tasks(self):
        """Playbook must contain sufficient tasks"""
        data = _load_playbook()
        if data is None:
            pytest.skip("Playbook does not exist yet")
        count = _count_real_tasks(data)
        assert count >= 5, (
            f"ARIA: Insufficient tasks. Found {count} — expected at least 5 "
            f"(gather facts, deploy SSH config, deploy MOTD, install firewall, "
            f"configure firewall). Complete the TODO sections."
        )

    def test_playbook_uses_variables(self):
        """Playbook must use variables — no hardcoded OS-specific values"""
        text = _playbook_text()
        if not text or "TODO" in text:
            pytest.skip("Playbook not yet complete")
        # Check for variable usage patterns
        has_vars = (
            "{{" in text
            or "ansible_os_family" in text
        )
        assert has_vars, (
            "ARIA: No variables or conditionals detected in playbook. "
            "Corporal Copy-Paste would be proud — you're hardcoding. "
            "Use variables from group_vars and 'when' conditionals."
        )


# -------------------------------------------------------------------
# Phase 2: Variables & Templates
# -------------------------------------------------------------------

class TestVariablesAndTemplates:
    """ARIA verifies: Are variables and templates properly configured?"""

    def test_group_vars_defined(self):
        """group_vars must contain actual variable definitions"""
        gv_dir = os.path.join(_workspace_dir(), "inventory", "group_vars")
        all_yml = os.path.join(gv_dir, "all.yml")
        if not os.path.isfile(all_yml):
            pytest.skip("group_vars/all.yml does not exist")
        with open(all_yml) as f:
            data = yaml.safe_load(f)
        assert data is not None and isinstance(data, dict), (
            "ARIA: group_vars/all.yml contains no variable definitions. "
            "Define ssh_permit_root_login, ssh_password_authentication, "
            "ssh_login_grace_time, ssh_max_auth_tries, and banner_message."
        )
        required = ["ssh_permit_root_login", "ssh_password_authentication",
                     "ssh_login_grace_time", "banner_message"]
        missing = [k for k in required if k not in data]
        assert not missing, (
            f"ARIA: Missing variables in group_vars/all.yml: "
            f"{', '.join(missing)}. Define all required variables."
        )

    def test_sshd_template_exists(self):
        """sshd_config.j2 template must exist"""
        tpl = os.path.join(_workspace_dir(), "templates", "sshd_config.j2")
        assert os.path.isfile(tpl), (
            "ARIA: Template templates/sshd_config.j2 not found. "
            "This template generates the SSH configuration from variables."
        )

    def test_motd_template_exists(self):
        """motd.j2 template must exist"""
        tpl = os.path.join(_workspace_dir(), "templates", "motd.j2")
        assert os.path.isfile(tpl), (
            "ARIA: Template templates/motd.j2 not found. "
            "This template generates the login banner with host-specific facts."
        )


# -------------------------------------------------------------------
# Phase 3: Multi-OS compliance
# -------------------------------------------------------------------

class TestMultiOSCompliance:
    """ARIA verifies: Does the playbook work on both OS families?"""

    @pytest.fixture(autouse=True)
    def _require_playbook(self):
        data = _load_playbook()
        if data is None:
            pytest.skip("Playbook does not exist yet")
        if _count_real_tasks(data) < 5:
            pytest.skip("Playbook tasks not yet complete")

    def test_ssh_hardened_ubuntu(self):
        """SSH must be hardened on Ubuntu nodes"""
        result = _run_ansible(
            "ansible", "debian", "-m", "shell",
            "-a", "grep -E '^PermitRootLogin\\s+no' /etc/ssh/sshd_config",
        )
        assert result.returncode == 0, (
            "ARIA: SSH is not hardened on Ubuntu nodes. "
            "Deploy the sshd_config.j2 template with correct variables. "
            "Run your playbook, then verify with: "
            "ansible debian -m shell -a \"grep PermitRootLogin /etc/ssh/sshd_config\""
        )

    def test_ssh_hardened_rocky(self):
        """SSH must be hardened on Rocky Linux node"""
        result = _run_ansible(
            "ansible", "redhat", "-m", "shell",
            "-a", "grep -E '^PermitRootLogin\\s+no' /etc/ssh/sshd_config",
        )
        assert result.returncode == 0, (
            "ARIA: SSH is not hardened on the Rocky Linux node. "
            "Ensure your template deploys correctly on Red Hat family. "
            "Check that group_vars/redhat.yml defines ssh_service_name."
        )

    def test_motd_deployed(self):
        """Login banner must be deployed on all nodes"""
        result = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "cat /etc/motd",
        )
        assert result.returncode == 0 and "STARFALL" in result.stdout, (
            "ARIA: Login banner not deployed or missing expected content. "
            "Deploy templates/motd.j2 to /etc/motd on all nodes. "
            "Ensure banner_message is defined in group_vars/all.yml."
        )


# -------------------------------------------------------------------
# Phase 4: Firewall
# -------------------------------------------------------------------

class TestFirewall:
    """ARIA verifies: Are firewalls active on both OS families?"""

    @pytest.fixture(autouse=True)
    def _require_playbook(self):
        data = _load_playbook()
        if data is None:
            pytest.skip("Playbook does not exist yet")
        if _count_real_tasks(data) < 5:
            pytest.skip("Playbook tasks not yet complete")

    def test_firewall_ubuntu(self):
        """ufw must be active on Ubuntu nodes"""
        result = _run_ansible(
            "ansible", "debian", "-m", "shell",
            "-a", "ufw status | head -1",
        )
        assert result.returncode == 0 and "inactive" not in result.stdout.lower(), (
            "ARIA: Firewall (ufw) is not active on Ubuntu nodes. "
            "Use community.general.ufw with 'when: ansible_os_family == \"Debian\"'."
        )

    def test_firewall_rocky(self):
        """firewalld must be active on Rocky Linux node"""
        result = _run_ansible(
            "ansible", "redhat", "-m", "shell",
            "-a", "systemctl is-active firewalld",
        )
        assert result.returncode == 0 and "active" in result.stdout, (
            "ARIA: Firewall (firewalld) is not active on the Rocky Linux node. "
            "Use ansible.builtin.service with 'when: ansible_os_family == \"RedHat\"'."
        )


# -------------------------------------------------------------------
# Phase 5: Idempotency
# -------------------------------------------------------------------

class TestIdempotency:
    """ARIA verifies: Is the playbook idempotent?"""

    def test_playbook_is_idempotent(self):
        """Running the playbook must show changed=0"""
        data = _load_playbook()
        if data is None:
            pytest.skip("Playbook does not exist yet")
        if _count_real_tasks(data) < 5:
            pytest.skip("Playbook tasks not yet complete")

        # Check if SSH hardening has been applied
        check = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "grep -E '^PermitRootLogin\\s+no' /etc/ssh/sshd_config",
        )
        if check.returncode != 0:
            pytest.skip(
                "Fleet not yet hardened — run your playbook first"
            )

        result = _run_ansible(
            "ansible-playbook", "playbook.yml",
            timeout=120,
        )
        assert result.returncode == 0, (
            "ARIA: Playbook failed. "
            "Fix the errors reported by 'ansible-playbook playbook.yml'."
        )
        changed_match = re.findall(r"changed=(\d+)", result.stdout)
        total_changed = sum(int(c) for c in changed_match)
        assert total_changed == 0, (
            f"ARIA: Idempotency failure. Playbook changed "
            f"{total_changed} task(s). One playbook, zero surprises. "
            f"Common causes: shell/command tasks without changed_when, "
            f"or template differences between runs."
        )
