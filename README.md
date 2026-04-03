# Starfall Defence Corps Academy

## Mission 1.4: One Playbook, Many Ships

> *"Fleet runs mixed OS — Ubuntu and Rocky. Corporal Copy-Paste has written 47 separate playbooks. No more. One playbook. All ships."*

You are a cadet at the Starfall Defence Corps Academy. The fleet now runs mixed operating systems — Ubuntu and Rocky Linux. Previous missions only targeted Ubuntu. Corporal Copy-Paste's answer was to duplicate everything. Your answer: one playbook that adapts to any OS using variables, Jinja2 templates, and conditionals.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (with Docker Compose v2)
- [GNU Make](https://www.gnu.org/software/make/)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/) (`ansible-core`)
- Python 3.10+ (for test environment)
  - On Debian/Ubuntu: `sudo apt install python3-venv`
- Git

> **Windows users**: This mission requires a Linux environment. Install [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) and run all commands from within your WSL terminal.

## Quick Start

```bash
# 1. Use this template on GitHub (green button, top right)
git clone https://github.com/YOUR-USERNAME/mission-1-4-many-ships.git
cd mission-1-4-many-ships

# 2. Start the fleet (builds Ubuntu + Rocky Linux containers)
make setup

# 3. Activate the virtual environment
source venv/bin/activate
```

4. **Read your orders**: [Mission Briefing](docs/BRIEFING.md)
5. **Complete the exercises**: [Exercises](docs/EXERCISES.md)
6. **Stuck?** [Hints & Troubleshooting](docs/HINTS.md)
7. **Track progress**: [Checklist](CHECKLIST.md)

## Lab Architecture

```
 Your Machine
+--------------------------------------------------+
|  workspace/                                      |
|    ansible.cfg                                   |
|    inventory/hosts.yml         (pre-configured)  |
|    inventory/group_vars/all.yml    (you define)  |
|    inventory/group_vars/debian.yml (you define)  |
|    inventory/group_vars/redhat.yml (you define)  |
|    templates/sshd_config.j2   (provided)         |
|    templates/motd.j2          (provided)         |
|    playbook.yml               (you complete)     |
|    .ssh/cadet_key             (auto-generated)   |
|                                                  |
|  Docker Network: 172.30.0.0/24                   |
|  +------------+ +-------------+ +------------+  |
|  | sdc-web    | | sdc-db      | | sdc-comms  |  |
|  | :2221      | | :2222       | | :2223      |  |
|  | Ubuntu22.04| | Rocky Lin 9 | | Ubuntu22.04|  |
|  | (Debian)   | | (RedHat)    | | (Debian)   |  |
|  +------------+ +-------------+ +------------+  |
+--------------------------------------------------+
```

## Available Commands

```
make help       Show available commands
make setup      Start the fleet (2 Ubuntu + 1 Rocky Linux)
make test       Ask ARIA to verify your work
make reset      Destroy and rebuild all fleet nodes
make destroy    Tear down everything (containers, keys, venv)
make ssh-web    SSH into sdc-web (Ubuntu)
make ssh-db     SSH into sdc-db (Rocky Linux)
make ssh-comms  SSH into sdc-comms (Ubuntu)
```

## Mission Files

| File | Purpose |
|------|---------|
| [BRIEFING.md](docs/BRIEFING.md) | Mission briefing — **read this first** |
| [EXERCISES.md](docs/EXERCISES.md) | Step-by-step exercises (5 phases) |
| [HINTS.md](docs/HINTS.md) | Troubleshooting and hints |
| [CHECKLIST.md](CHECKLIST.md) | Progress tracker |

## ARIA Review (Pull Request Workflow)

**Locally** — run `make test` for instant verification.

**On Pull Request** — push your work, open a PR, ARIA reviews automatically.

To enable PR reviews, add `ANTHROPIC_API_KEY` to your repo's Secrets (Settings > Secrets > Actions).

## Troubleshooting

**Rocky Linux container won't build**: The Rocky image is larger than Ubuntu. Ensure you have sufficient disk space and a stable internet connection.

**Locked out after enabling firewall**: Run `make reset`. Remember: allow SSH BEFORE enabling the firewall on both OS families.

**"No module named community.general"**: Run `ansible-galaxy collection install community.general`.

**"No module named ansible.posix"**: Run `ansible-galaxy collection install ansible.posix`.

**Need a clean slate**: Run `make reset` to destroy and rebuild everything.
