# Mission 1.4: One Playbook, Many Ships — Progress Tracker

**Rank**: Ensign Candidate
**Mission Progress**: 4 of 5 toward Ensign

---

## Phase 1: Reconnaissance

- [ ] Fleet nodes are online (`make setup` succeeded)
- [ ] Identified OS families: sdc-web (Debian), sdc-db (RedHat), sdc-comms (Debian)
- [ ] Explored facts: `ansible_distribution`, `ansible_hostname`
- [ ] Understand package manager differences (apt vs dnf)
- [ ] Understand service name differences (ssh vs sshd)

---

## Phase 2: Variables & Templates

- [ ] Defined shared variables in `group_vars/all.yml`
- [ ] Defined Debian-specific variables in `group_vars/debian.yml`
- [ ] Defined Red Hat-specific variables in `group_vars/redhat.yml`
- [ ] Reviewed `templates/sshd_config.j2` — understands `{{ }}` syntax
- [ ] Reviewed `templates/motd.j2` — understands fact-based templates

---

## Phase 3: Conditional Tasks

- [ ] Wrote Task 2: Deploy SSH config via `template` module
- [ ] Wrote Task 3: Deploy MOTD via `template` module
- [ ] Wrote Task 4: Install firewall (conditional `apt`/`dnf`)
- [ ] Wrote SSH restart handler using `{{ ssh_service_name }}`
- [ ] Playbook passes syntax check

---

## Phase 4: Firewall (Both Families)

- [ ] Wrote Task 5: Allow SSH (conditional `ufw`/`firewalld`)
- [ ] Wrote Task 6: Enable firewall (conditional)
- [ ] SSH allow rule comes before firewall enable (both OS families)

---

## Phase 5: Verify & Harden

- [ ] Dry run succeeded on all nodes (including Rocky)
- [ ] Playbook executed — `when` conditionals skipping correctly
- [ ] SSH hardened on Ubuntu nodes
- [ ] SSH hardened on Rocky Linux node
- [ ] MOTD deployed with host-specific content on all nodes
- [ ] ufw active on Ubuntu nodes
- [ ] firewalld active on Rocky Linux node
- [ ] Second run is idempotent — `changed=0` on all hosts
- [ ] `make test` — all ARIA checks pass

---

## Verification

- [ ] `make test` — all ARIA checks pass
