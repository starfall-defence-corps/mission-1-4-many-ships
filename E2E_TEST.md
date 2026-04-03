# Mission 1.4: One Playbook, Many Ships — E2E Manual Test Script

**Purpose**: Verify the entire student workflow works end-to-end on mixed-OS fleet.
**Time**: ~20 minutes (Rocky Linux image build adds time on first run).
**Prerequisites**: Docker running, ports 2221-2223 free.

---

## 1. Setup

```bash
cd ~/projects/starfall-defence-corps/mission-1-4-many-ships
make destroy 2>/dev/null; true
make setup
```

**Expected**: All 3 nodes ONLINE. Rocky Linux build may take 1-2 min on first run.

```bash
cd workspace
ansible all -m ping
```

**Expected**: All 3 nodes return `SUCCESS`.

---

## 2. Verify Starting State

```bash
# Check OS families
ansible all -m setup -a "filter=ansible_os_family"
```

**Expected**:
- sdc-web: `Debian`
- sdc-db: `RedHat`
- sdc-comms: `Debian`

```bash
# SSH is misconfigured on all nodes
ansible all -m shell -a "grep PermitRootLogin /etc/ssh/sshd_config | head -1"
```

**Expected**: `PermitRootLogin yes` on all nodes.

```bash
# No MOTD yet
ansible all -m shell -a "cat /etc/motd 2>/dev/null || echo EMPTY"
```

**Expected**: Empty or default content on all nodes.

---

## 3. Run ARIA Before Solution

```bash
cd ..
make test
cd workspace
```

**Expected**: Phase 1 partially passes. Later phases show deficiencies.

---

## 4. Apply Solution — group_vars

```bash
cat > inventory/group_vars/all.yml << 'EOF'
---
ssh_permit_root_login: "no"
ssh_password_authentication: "no"
ssh_login_grace_time: 30
ssh_max_auth_tries: 3
banner_message: "STARFALL DEFENCE CORPS — AUTHORISED PERSONNEL ONLY"
EOF

cat > inventory/group_vars/debian.yml << 'EOF'
---
ssh_service_name: ssh
firewall_pkg: ufw
firewall_service: ufw
EOF

cat > inventory/group_vars/redhat.yml << 'EOF'
---
ssh_service_name: sshd
firewall_pkg: firewalld
firewall_service: firewalld
EOF
```

---

## 5. Apply Solution — Playbook

```bash
cat > playbook.yml << 'PLAYBOOK'
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
PLAYBOOK
```

---

## 6. Syntax Check

```bash
ansible-playbook playbook.yml --syntax-check
```

**Expected**: No errors.

---

## 7. Dry Run

```bash
ansible-playbook playbook.yml --check --diff
```

**Expected**: Shows predicted changes on all nodes. `when` conditionals cause skips on non-matching OS. Return code 0.

---

## 8. Execute Playbook (First Run)

```bash
ansible-playbook playbook.yml
```

**Expected**:
- SSH template deployed on all 3 nodes (`changed`)
- MOTD deployed on all 3 nodes (`changed`)
- `apt` tasks run on sdc-web/sdc-comms, skipped on sdc-db
- `dnf` tasks run on sdc-db, skipped on sdc-web/sdc-comms
- ufw tasks run on Debian nodes, firewalld on RedHat
- Handler restarts SSH on all nodes

---

## 9. Verify Changes — Ubuntu Nodes

```bash
# SSH hardened
ansible debian -m shell -a "grep PermitRootLogin /etc/ssh/sshd_config"
```
**Expected**: `PermitRootLogin no`

```bash
# MOTD deployed with Ubuntu info
ansible debian -m shell -a "cat /etc/motd"
```
**Expected**: Contains `STARFALL DEFENCE CORPS`, `Ubuntu`, and each node's hostname.

```bash
# ufw active
ansible debian -m shell -a "ufw status | head -1"
```
**Expected**: `Status: active`

---

## 10. Verify Changes — Rocky Linux Node

```bash
# SSH hardened
ansible redhat -m shell -a "grep PermitRootLogin /etc/ssh/sshd_config"
```
**Expected**: `PermitRootLogin no`

```bash
# MOTD deployed with Rocky info
ansible redhat -m shell -a "cat /etc/motd"
```
**Expected**: Contains `STARFALL DEFENCE CORPS`, `Rocky`, and `sdc-db`.

```bash
# firewalld active
ansible redhat -m shell -a "systemctl is-active firewalld"
```
**Expected**: `active`

```bash
# SSH allowed in firewalld
ansible redhat -m shell -a "firewall-cmd --list-services"
```
**Expected**: Contains `ssh`.

---

## 11. Idempotency Check

```bash
ansible-playbook playbook.yml
```

**Expected**: `changed=0` on ALL hosts. No handler fires.

---

## 12. Full ARIA Verification

```bash
cd ..
make test
```

**Expected**: All 5 phases pass. "Mission 1.4 status: COMPLETE".

---

## 13. Edge Case Tests

### 13a. Missing group_vars (hardcoded values)

```bash
cd workspace
mv inventory/group_vars/debian.yml /tmp/debian.yml.bak
mv inventory/group_vars/redhat.yml /tmp/redhat.yml.bak
ansible-playbook playbook.yml --check 2>&1 | tail -10
```

**Expected**: Failure — undefined variables (`ssh_service_name`, `firewall_pkg`).

```bash
mv /tmp/debian.yml.bak inventory/group_vars/debian.yml
mv /tmp/redhat.yml.bak inventory/group_vars/redhat.yml
```

### 13b. Hardcoded playbook (no variables) — ARIA detection

```bash
cat > /tmp/hardcoded.yml << 'EOF'
---
- name: Hardcoded
  hosts: all
  become: true
  tasks:
    - name: Task 1
      ansible.builtin.shell: echo "no variables here"
    - name: Task 2
      ansible.builtin.shell: echo "still no variables"
    - name: Task 3
      ansible.builtin.shell: echo "Corporal Copy-Paste approves"
    - name: Task 4
      ansible.builtin.shell: echo "one more"
    - name: Task 5
      ansible.builtin.shell: echo "five tasks no vars"
EOF
cp /tmp/hardcoded.yml playbook.yml
cd ..
make test 2>&1 | grep -E "(variables|hardcod|✗)"
```

**Expected**: Phase 1 fails with message about no variables/conditionals detected.

### 13c. Wrong service name in handler

```bash
cd workspace
# Restore proper playbook first
cat > playbook.yml << 'PLAYBOOK'
---
- name: Test wrong handler
  hosts: all
  become: true
  tasks:
    - name: Gather facts
      ansible.builtin.setup:
    - name: Deploy SSH config
      ansible.builtin.template:
        src: templates/sshd_config.j2
        dest: /etc/ssh/sshd_config
        owner: root
        group: root
        mode: '0644'
      notify: Restart SSH
    - name: Deploy MOTD
      ansible.builtin.template:
        src: templates/motd.j2
        dest: /etc/motd
    - name: Placeholder 1
      ansible.builtin.debug:
        msg: "placeholder"
    - name: Placeholder 2
      ansible.builtin.debug:
        msg: "placeholder"
  handlers:
    - name: Restart SSH
      ansible.builtin.service:
        name: ssh
        state: restarted
PLAYBOOK
```

```bash
cd ..
make reset
cd workspace
ansible-playbook playbook.yml 2>&1 | tail -15
```

**Expected**: Works on Ubuntu nodes but FAILS on Rocky (service `ssh` doesn't exist — it's `sshd`). This proves the variable-based handler matters.

### 13d. Restore and verify recovery

```bash
cd ..
make reset
cd workspace
```

Restore the full solution from step 5, then:

```bash
ansible-playbook playbook.yml
cd ..
make test
```

**Expected**: All phases pass.

---

## 14. Template Rendering Test

```bash
cd workspace
# Verify template uses variables, not static values
ansible all -m shell -a "grep LoginGraceTime /etc/ssh/sshd_config"
```

**Expected**: `LoginGraceTime 30` on all nodes (from group_vars/all.yml variable).

```bash
# Change variable and re-run to prove templates are dynamic
sed -i 's/ssh_login_grace_time: 30/ssh_login_grace_time: 15/' inventory/group_vars/all.yml
ansible-playbook playbook.yml
ansible all -m shell -a "grep LoginGraceTime /etc/ssh/sshd_config"
```

**Expected**: `LoginGraceTime 15` on all nodes. Proves the template renders from variables.

```bash
# Restore original value
sed -i 's/ssh_login_grace_time: 15/ssh_login_grace_time: 30/' inventory/group_vars/all.yml
ansible-playbook playbook.yml
```

---

## 15. Cleanup

```bash
cd ..
make destroy
```

---

## Test Summary

| # | Test | Expected |
|---|------|----------|
| 1 | Setup | 3 nodes online (mixed OS) |
| 2 | Starting state | Misconfigs, correct OS families |
| 3 | ARIA before | Deficiencies |
| 4-7 | Solution + checks | No errors |
| 8 | First run | Changes + correct skips |
| 9-10 | Verify Ubuntu + Rocky | Both OS hardened correctly |
| 11 | Second run | changed=0 |
| 12 | ARIA after | All phases pass |
| 13a | Missing group_vars | Undefined variable error |
| 13b | Hardcoded playbook | ARIA detects no variables |
| 13c | Wrong service name | Fails on Rocky (proves vars matter) |
| 13d | Recovery | Full pass after fix |
| 14 | Template rendering | Variable change reflected |
| 15 | Cleanup | Torn down |
