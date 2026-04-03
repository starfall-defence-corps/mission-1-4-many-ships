---
CLASSIFICATION: CADET EYES ONLY
MISSION: 1.4 — ONE PLAYBOOK, MANY SHIPS
THEATRE: Starfall Defence Corps Academy
AUTHORITY: SDC Cyber Command, 2187
---

# OPERATION ORDER — MISSION 1.4: ONE PLAYBOOK, MANY SHIPS

---

## 1. SITUATION

### 1a. Enemy Forces

Voidborn operative **CORPORAL COPY-PASTE** has infiltrated fleet maintenance. Modus operandi: duplication without understanding. The Corporal has written 47 separate playbooks — one for every node, one for every OS variant. When a security patch was needed fleet-wide, only 12 of the 47 were updated. The rest are still vulnerable. Copy-paste is not automation — it is the illusion of automation.

### 1b. Friendly Forces

The **Starfall Defence Corps (SDC)** fleet has been inventoried (1.1), SSH-hardened (1.2), and swept clean of unnecessary services (1.3). But the fleet now runs **mixed operating systems** — Ubuntu and Rocky Linux. Previous playbooks only worked on Ubuntu. A single-OS playbook applied to a mixed fleet will fail on every Red Hat family node.

### 1c. Attachments / Support

**ARIA** (Automated Review & Intelligence Analyst) verifies that your single playbook works on both OS families. She checks SSH hardening, template deployment, and firewall state on every node — Ubuntu and Rocky alike.

### 1d. Operational Tools

This mission introduces the tools that make one playbook serve many ships:

| Tool | Purpose |
|------|---------|
| **Variables** (`group_vars/`) | OS-specific values without hardcoding |
| **Jinja2 Templates** (`.j2`) | Dynamic configuration files |
| **Facts** (`ansible_os_family`) | Auto-detected host properties |
| **Conditionals** (`when:`) | Run tasks only on matching hosts |
| **`ansible.builtin.template`** | Deploy Jinja2 templates to hosts |

---

## 2. MISSION

Write a single Ansible playbook that hardens SSH, deploys a login banner, and configures the firewall on **both Ubuntu and Rocky Linux** nodes. Use variables, templates, and conditionals — not separate task blocks for each OS.

**End state**: One playbook. All ships. Both OS families hardened identically (via different OS-appropriate mechanisms). Corporal Copy-Paste's 47-playbook approach replaced with one.

---

## 3. EXECUTION

### 3a. Commander's Intent

Duplication is the Voidborn's fifth column. Every copied playbook is a playbook that drifts, that gets forgotten, that doesn't get patched. The fleet runs mixed operating systems and that will never change — there will always be Debian derivatives and Red Hat derivatives. The answer is not 47 playbooks. The answer is one playbook smart enough to adapt.

### 3b. Concept of Operations

Five sequential phases. Full procedural detail is in **EXERCISES.md**.

| Phase | Task | Objective |
|-------|------|-----------|
| 1 | Reconnaissance | Gather facts, identify OS families, understand differences |
| 2 | Variables & Templates | Define group_vars, create Jinja2 templates |
| 3 | Conditional Tasks | Write tasks that adapt to each OS family |
| 4 | Firewall (Both Families) | ufw for Ubuntu, firewalld for Rocky |
| 5 | Verify & Harden | Execute on all nodes, confirm idempotency |

### 3c. Fleet Assets

**MIXED-OS FLEET** — this is the critical change from previous missions.

| Designation | Role | OS | SSH Port |
|-------------|------|----|----------|
| `sdc-web` | Fleet Web Server | **Ubuntu 22.04** | 2221 |
| `sdc-db` | Fleet Database Server | **Rocky Linux 9** | 2222 |
| `sdc-comms` | Fleet Communications Relay | **Ubuntu 22.04** | 2223 |

**SSH User**: `cadet`
**Authentication**: SSH key located at `workspace/.ssh/cadet_key`

### 3d. Key OS Differences

| Aspect | Ubuntu (Debian) | Rocky (Red Hat) |
|--------|-----------------|-----------------|
| Package manager | `apt` | `dnf` |
| SSH service name | `ssh` | `sshd` |
| Firewall tool | `ufw` | `firewalld` |
| OS family fact | `Debian` | `RedHat` |

Your playbook must handle all of these differences using variables and conditionals.

### 3e. Rules of Engagement

- One playbook. No separate playbooks per OS.
- No hardcoded OS-specific values in tasks. Use variables from `group_vars/`.
- Templates must use Jinja2 syntax — no raw configuration files.
- `when` conditionals must use `ansible_os_family`, not hostname checks.

---

## 4. SUPPORT

| Resource | Function | Command |
|----------|----------|---------|
| **ARIA** | Verifies multi-OS compliance | `make test` |
| **HINTS.md** | Operational guidance | — |
| **Fleet Reset** | Rebuild all containers | `make reset` |
| **Module Docs** | Template module docs | `ansible-doc template` |
| **Facts** | Inspect host facts | `ansible sdc-db -m setup` |

---

## 5. COMMAND AND SIGNAL

**Commander's Final Order**: Corporal Copy-Paste's reign ends today. One playbook, all ships, both operating systems. Variables replace hardcoding. Templates replace static files. Conditionals replace duplication. Execute.

Proceed to **EXERCISES.md** for phase-by-phase operational instructions.

---

*SDC Cyber Command — 2187 — CADET EYES ONLY*
