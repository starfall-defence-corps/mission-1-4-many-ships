# Mission 1.4: One Playbook, Many Ships — Hints & Troubleshooting Guide

**Rank**: Ensign Candidate (Reduced Scaffolding)

Fewer hints this time, Cadet. You've earned your way here.

---

## Variables & group_vars

**How group_vars work:**

Ansible automatically loads variable files from `group_vars/` based on group membership. If a host is in the `debian` group, it loads `group_vars/debian.yml`. If in `all`, it loads `group_vars/all.yml`.

Your inventory defines the groups:
```yaml
all:
  children:
    debian:       # ← loads group_vars/debian.yml
      children:
        web_servers:
          hosts:
            sdc-web: ...
    redhat:       # ← loads group_vars/redhat.yml
      children:
        db_servers:
          hosts:
            sdc-db: ...
```

**Variable precedence (what matters for this mission):**

1. `group_vars/all.yml` — lowest (applies to everyone)
2. `group_vars/<group>.yml` — overrides `all` for that group
3. `host_vars/<host>.yml` — overrides everything for that host

For this mission, shared values go in `all.yml` and OS-specific values go in `debian.yml` / `redhat.yml`.

---

## Templates

**Jinja2 basics:**

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{{ var }}` | Insert variable | `PermitRootLogin {{ ssh_permit_root_login }}` |
| `{{ ansible_hostname }}` | Insert fact | `Hostname: {{ ansible_hostname }}` |
| `{% if %}` | Conditional | `{% if ansible_os_family == "Debian" %}` |
| `{# comment #}` | Template comment | Not rendered in output |

**The `ansible_managed` variable:**

Including `{{ ansible_managed }}` at the top of templates adds a comment like:
```
# Ansible managed: sshd_config.j2 modified on 2187-01-15
```

This warns anyone manually editing the file that Ansible manages it.

**Template deployment:**

```yaml
    - name: Deploy config
      ansible.builtin.template:
        src: templates/my-template.j2
        dest: /etc/target/config.conf
        owner: root
        group: root
        mode: '0644'
```

The `src` path is relative to the playbook location.

---

## Conditionals

**`when` clause syntax:**

```yaml
    - name: Task for Debian only
      ansible.builtin.apt:
        name: some-package
        state: present
      when: ansible_os_family == "Debian"
```

The `when` clause uses Jinja2 expressions but **without** `{{ }}` braces. This is a common mistake:

```yaml
# WRONG:
when: "{{ ansible_os_family }}" == "Debian"

# CORRECT:
when: ansible_os_family == "Debian"
```

**Skipped tasks are normal:**

When a `when` condition is false, the task shows `skipping` in the output. This is correct — it means the conditional is working.

---

## Firewall Differences

**Ubuntu (ufw):**

```yaml
    - name: Allow SSH (Debian)
      community.general.ufw:
        rule: allow
        port: '22'
        proto: tcp
      when: ansible_os_family == "Debian"

    - name: Enable ufw (Debian)
      community.general.ufw:
        state: enabled
      when: ansible_os_family == "Debian"
```

**Rocky (firewalld):**

```yaml
    - name: Allow SSH (RedHat)
      ansible.posix.firewalld:
        service: ssh
        permanent: true
        immediate: true
        state: enabled
      when: ansible_os_family == "RedHat"

    - name: Enable firewalld (RedHat)
      ansible.builtin.service:
        name: firewalld
        state: started
        enabled: true
      when: ansible_os_family == "RedHat"
```

Note: `firewalld` uses **service names** (like `ssh`) rather than port numbers. The `permanent: true` makes the rule survive reboots. `immediate: true` applies it right now.

**"No module named ansible.posix" error:**

Install the collection:
```bash
ansible-galaxy collection install ansible.posix
```

---

## Connection Hints

**Rocky Linux node won't start:**

Rocky Linux 9 images are larger than Ubuntu. The first `make setup` may take longer. If the build fails, ensure you have enough disk space and try `make reset`.

**SSH works on Ubuntu but not Rocky:**

Check that SSH host keys were generated in the Rocky container. If not, the container may need a rebuild: `make reset`.

---

## CRITICAL SPOILER — Full Playbook Solution

> **STOP.** This is your last resort.

<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>

```yaml
---
- name: One Playbook, Many Ships — Multi-OS Fleet Hardening
  hosts: all
  become: true

  tasks:
    - name: Gather fleet intelligence
      ansible.builtin.setup:

    - name: Deploy SSH configuration
      ansible.builtin.template:
        src: templates/sshd_config.j2
        dest: /etc/ssh/sshd_config
        owner: root
        group: root
        mode: '0644'
        validate: 'sshd -t -f %s'
      notify: Restart SSH

    - name: Deploy login banner
      ansible.builtin.template:
        src: templates/motd.j2
        dest: /etc/motd
        owner: root
        group: root
        mode: '0644'

    - name: Install firewall (Debian)
      ansible.builtin.apt:
        name: "{{ firewall_pkg }}"
        state: present
      when: ansible_os_family == "Debian"

    - name: Install firewall (RedHat)
      ansible.builtin.dnf:
        name: "{{ firewall_pkg }}"
        state: present
      when: ansible_os_family == "RedHat"

    - name: Allow SSH through firewall (Debian)
      community.general.ufw:
        rule: allow
        port: '22'
        proto: tcp
      when: ansible_os_family == "Debian"

    - name: Allow SSH through firewall (RedHat)
      ansible.posix.firewalld:
        service: ssh
        permanent: true
        immediate: true
        state: enabled
      when: ansible_os_family == "RedHat"

    - name: Enable firewall (Debian)
      community.general.ufw:
        state: enabled
      when: ansible_os_family == "Debian"

    - name: Enable firewall (RedHat)
      ansible.builtin.service:
        name: firewalld
        state: started
        enabled: true
      when: ansible_os_family == "RedHat"

  handlers:
    - name: Restart SSH
      ansible.builtin.service:
        name: "{{ ssh_service_name }}"
        state: restarted
```

**group_vars/all.yml:**
```yaml
---
ssh_permit_root_login: "no"
ssh_password_authentication: "no"
ssh_login_grace_time: 30
ssh_max_auth_tries: 3
banner_message: "STARFALL DEFENCE CORPS — AUTHORISED PERSONNEL ONLY"
```

**group_vars/debian.yml:**
```yaml
---
ssh_service_name: ssh
firewall_pkg: ufw
firewall_service: ufw
```

**group_vars/redhat.yml:**
```yaml
---
ssh_service_name: sshd
firewall_pkg: firewalld
firewall_service: firewalld
```

---

*SDC Cyber Command — 2187 — CADET EYES ONLY*
