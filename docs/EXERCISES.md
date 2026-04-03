---
CLASSIFICATION: CADET EYES ONLY
MISSION: 1.4 — ONE PLAYBOOK, MANY SHIPS
DOCUMENT: EXERCISES — Phase-by-Phase Operational Instructions
---

# EXERCISES — MISSION 1.4: ONE PLAYBOOK, MANY SHIPS

Complete each phase in sequence. Run `make test` after each phase.

**Directory convention** (same as previous missions):
- Ansible commands: run from `workspace/`
- Make commands: run from the **project root**

---

## PHASE 0: Launch the Fleet

```bash
make setup
```

This builds both Ubuntu and Rocky Linux containers. Wait for all 3 nodes to report ONLINE.

**Note**: The Rocky Linux image is larger than Ubuntu and may take longer to build on first run.

---

## PHASE 1: Reconnaissance

> Before writing a multi-OS playbook, understand the differences. Gather facts from each node and observe what changes between OS families.

### Step 1.1 — Gather Facts from All Nodes

```bash
cd workspace
ansible all -m setup -a "filter=ansible_os_family"
```

You will see:
- `sdc-web`: `ansible_os_family: Debian`
- `sdc-db`: `ansible_os_family: RedHat`
- `sdc-comms`: `ansible_os_family: Debian`

This fact is how your playbook will distinguish between OS families.

### Step 1.2 — Explore More Facts

```bash
ansible all -m setup -a "filter=ansible_distribution*"
```

Note the differences: `Ubuntu` vs `Rocky`, version numbers, etc.

```bash
ansible all -m setup -a "filter=ansible_hostname"
```

Each node reports its own hostname. Templates can use this to generate host-specific configuration.

### Step 1.3 — Observe Package Manager Differences

```bash
# This works on Ubuntu nodes:
ansible debian -m shell -a "which apt"

# This works on Rocky:
ansible redhat -m shell -a "which dnf"
```

### Step 1.4 — Observe Service Name Differences

```bash
# Ubuntu uses 'ssh':
ansible debian -m shell -a "systemctl status ssh | head -3"

# Rocky uses 'sshd':
ansible redhat -m shell -a "systemctl status sshd | head -3"
```

### Step 1.5 — Run ARIA

```bash
cd ..
make test
cd workspace
```

---

## PHASE 2: Variables & Templates

> Define the variables that capture OS differences. Create Jinja2 templates that use those variables to generate correct configuration for any OS.

### Step 2.1 — Define Shared Variables

Edit `inventory/group_vars/all.yml`. Replace the TODO comments with actual variable definitions:

```yaml
---
ssh_permit_root_login: "no"
ssh_password_authentication: "no"
ssh_login_grace_time: 30
ssh_max_auth_tries: 3
banner_message: "STARFALL DEFENCE CORPS — AUTHORISED PERSONNEL ONLY"
```

These values apply to ALL nodes regardless of OS.

### Step 2.2 — Define Debian-Specific Variables

Edit `inventory/group_vars/debian.yml`:

```yaml
---
ssh_service_name: ssh
firewall_pkg: ufw
firewall_service: ufw
```

### Step 2.3 — Define Red Hat-Specific Variables

Edit `inventory/group_vars/redhat.yml`:

```yaml
---
ssh_service_name: sshd
firewall_pkg: firewalld
firewall_service: firewalld
```

### Step 2.4 — Examine the SSH Template

Open `templates/sshd_config.j2`. This template is provided — observe how it uses `{{ variable_name }}` syntax to insert values from your group_vars:

```jinja2
PermitRootLogin {{ ssh_permit_root_login }}
PasswordAuthentication {{ ssh_password_authentication }}
LoginGraceTime {{ ssh_login_grace_time }}
```

When Ansible deploys this template, it replaces each `{{ }}` with the actual variable value.

### Step 2.5 — Examine the MOTD Template

Open `templates/motd.j2`. This template uses **facts** — values Ansible gathers automatically:

```jinja2
Hostname : {{ ansible_hostname }}
OS       : {{ ansible_distribution }} {{ ansible_distribution_version }}
```

Each node gets a different banner because the facts differ per host.

### Step 2.6 — Run ARIA

```bash
cd ..
make test
cd workspace
```

---

## PHASE 3: Conditional Tasks

> Write the playbook tasks. Each task either works on all OS families (templates), or uses `when` to run only on the matching OS.

### Step 3.1 — Read the template Module Documentation

```bash
ansible-doc template
```

The `template` module works like `copy`, but processes Jinja2 syntax before deploying the file.

### Step 3.2 — Task 2: Deploy SSH Configuration

Find the Task 2 TODO in `playbook.yml`. Write a task that:

1. Uses `ansible.builtin.template`
2. Deploys `templates/sshd_config.j2` to `/etc/ssh/sshd_config`
3. Sets owner: `root`, group: `root`, mode: `'0644'`
4. Validates with `sshd -t -f %s`
5. Notifies `Restart SSH`

```yaml
    - name: Deploy SSH configuration
      ansible.builtin.template:
        src: templates/sshd_config.j2
        dest: /etc/ssh/sshd_config
        owner: root
        group: root
        mode: '0644'
        validate: 'sshd -t -f %s'
      notify: Restart SSH
```

This task works on BOTH OS families because the template uses variables, and the handler uses `{{ ssh_service_name }}`.

### Step 3.3 — Task 3: Deploy Login Banner

Write a task to deploy `templates/motd.j2` to `/etc/motd`:

```yaml
    - name: Deploy login banner
      ansible.builtin.template:
        src: templates/motd.j2
        dest: /etc/motd
        owner: root
        group: root
        mode: '0644'
```

No `when` needed — this works on all OS families.

### Step 3.4 — Task 4: Install Firewall (Conditional)

This is where `when` conditionals come in. You need TWO tasks — one for each package manager:

```yaml
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
```

On Ubuntu nodes, only the `apt` task runs. On Rocky, only the `dnf` task runs. The other is **skipped** (not failed).

### Step 3.5 — Write the Handler

Write the SSH restart handler using the `ssh_service_name` variable:

```yaml
  handlers:
    - name: Restart SSH
      ansible.builtin.service:
        name: "{{ ssh_service_name }}"
        state: restarted
```

On Ubuntu this restarts `ssh`. On Rocky this restarts `sshd`. Same handler, both OS families.

### Step 3.6 — Verify Syntax and Run ARIA

```bash
ansible-playbook playbook.yml --syntax-check
cd ..
make test
cd workspace
```

---

## PHASE 4: Firewall (Both Families)

> Configure the firewall on both OS families. Ubuntu uses ufw, Rocky uses firewalld.

### Step 4.1 — Task 5: Allow SSH Through Firewall

**Ubuntu:**

```yaml
    - name: Allow SSH through firewall (Debian)
      community.general.ufw:
        rule: allow
        port: '22'
        proto: tcp
      when: ansible_os_family == "Debian"
```

**Rocky:**

```yaml
    - name: Allow SSH through firewall (RedHat)
      ansible.posix.firewalld:
        service: ssh
        permanent: true
        immediate: true
        state: enabled
      when: ansible_os_family == "RedHat"
```

### Step 4.2 — Task 6: Enable Firewall

**Ubuntu:**

```yaml
    - name: Enable firewall (Debian)
      community.general.ufw:
        state: enabled
      when: ansible_os_family == "Debian"
```

**Rocky:**

```yaml
    - name: Enable firewall (RedHat)
      ansible.builtin.service:
        name: firewalld
        state: started
        enabled: true
      when: ansible_os_family == "RedHat"
```

### Step 4.3 — Verify and Run ARIA

```bash
ansible-playbook playbook.yml --syntax-check
cd ..
make test
cd workspace
```

---

## PHASE 5: Verify & Harden

### Step 5.1 — Dry Run

```bash
ansible-playbook playbook.yml --check --diff
```

### Step 5.2 — Execute

```bash
ansible-playbook playbook.yml
```

Watch the output. Notice how `when` conditionals cause tasks to be **skipped** on non-matching OS families — this is correct behaviour.

### Step 5.3 — Verify on Both OS Families

```bash
# SSH on Ubuntu:
ansible debian -m shell -a "grep PermitRootLogin /etc/ssh/sshd_config"

# SSH on Rocky:
ansible redhat -m shell -a "grep PermitRootLogin /etc/ssh/sshd_config"

# MOTD on all (note different hostnames and OS in output):
ansible all -m shell -a "cat /etc/motd"

# Firewall on Ubuntu:
ansible debian -m shell -a "ufw status | head -1"

# Firewall on Rocky:
ansible redhat -m shell -a "systemctl is-active firewalld"
```

### Step 5.4 — Idempotency

```bash
ansible-playbook playbook.yml
```

`changed=0` on all hosts.

### Step 5.5 — Final ARIA Verification

```bash
cd ..
make test
```

---

## MISSION COMPLETE — DEBRIEF CHECKLIST

- [ ] Identified OS families on each node using `ansible_os_family`
- [ ] Defined shared variables in `group_vars/all.yml`
- [ ] Defined OS-specific variables in `group_vars/debian.yml` and `group_vars/redhat.yml`
- [ ] Deployed SSH config via Jinja2 template — works on both OS families
- [ ] Deployed MOTD via template — shows host-specific facts
- [ ] Installed firewall via conditional `apt`/`dnf` tasks
- [ ] Configured firewall via conditional `ufw`/`firewalld` tasks
- [ ] Handler uses variable for service name — works on both OS families
- [ ] All changes verified on both Ubuntu and Rocky Linux
- [ ] `make test` — all ARIA checks pass

**What you learned in this mission:**

- [ ] Variables and `group_vars/` directory structure
- [ ] Jinja2 template syntax: `{{ variable_name }}`
- [ ] Ansible facts: `ansible_os_family`, `ansible_hostname`, `ansible_distribution`
- [ ] `when` conditionals for OS-specific tasks
- [ ] The `template` module for dynamic configuration
- [ ] Why one flexible playbook beats many static ones

---

*SDC Cyber Command — 2187 — CADET EYES ONLY*
