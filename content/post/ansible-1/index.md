+++
title = "Using Ansible for Hardening Linux Servers"
description = "A Practical Guide to configure common hardening settings on Linux servers using Ansible"
date = "2021-02-07"
draft = false
toc = false
tags = ["ansible"]
categories = ["anslbie"]
image = "ansible.png"
author = "Fabio M. Lopes"
+++

Server security is paramount in today's interconnected world.  A single vulnerability can expose your entire infrastructure to malicious actors.  Manual hardening across multiple servers is time-consuming, error-prone, and inconsistent.  This is where Ansible shines.  Ansible's automation capabilities allow us to implement robust security measures efficiently and reliably, ensuring consistent security posture across our entire fleet.

This blog post demonstrates how to leverage Ansible to harden Linux servers, focusing on key security best practices.  We'll build upon a previous example, enhancing it with crucial security features.  The example includes hardening Apache web servers, but the principles apply broadly to other server types.

**The Ansible Playbook:**

This Ansible playbook will implement the following security measures:

* **Disable Password Authentication (SSH):**  Eliminates the risk of brute-force attacks targeting password-based SSH logins.
* **Create and Secure an Admin User:**  Establishes a dedicated administrative account with strong authentication using SSH keys.
* **Configure `sudo` Permissions:**  Grants the admin user appropriate sudo privileges.
* **Install and Configure Fail2ban:**  Implements a security tool to detect and ban malicious IP addresses attempting unauthorized logins.
* **Limit SSH Authentication Attempts:**  Reduces the window of opportunity for brute-force attacks by setting a maximum number of authentication retries.

Here's the Ansible playbook (`hardening.yml`):

```yaml
---
- hosts: webservers
  become: true
  tasks:
    # Security Hardening Section
    - name: Disable password authentication (SSH)
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PasswordAuthentication'
        line: 'PasswordAuthentication no'
        state: present

    - name: Add admin user
      user:
        name: adminuser
        createhome: yes
        shell: /bin/bash
        state: present

    - name: Add admin user to sudoers
      lineinfile:
        path: /etc/sudoers
        line: "adminuser ALL=(ALL:ALL) ALL"
        create: yes
        state: present
        mode: '0440'

    - name: Copy authorized_keys
      copy:
        src: authorized_keys
        dest: /home/adminuser/.ssh/authorized_keys
        owner: adminuser
        group: adminuser
        mode: '0600'
      notify: restart sshd

    - name: Ensure .ssh directory exists
      file:
        path: /home/adminuser/.ssh
        state: directory
        mode: '0700'
        owner: adminuser
        group: adminuser

    - name: Install fail2ban
      apt:
        name: fail2ban
        state: present
      when: ansible_distribution == 'Ubuntu'

    - name: Install fail2ban (CentOS/RHEL)
      yum:
        name: fail2ban
        state: present
      when: ansible_distribution == 'CentOS' or ansible_distribution == 'RedHat'

    - name: Enable fail2ban service
      service:
        name: fail2ban
        state: started
        enabled: yes

    # SSH Hardening Tasks
    - name: Set SSH Protocol to 2
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^Protocol'
        line: 'Protocol 2'
        state: present

    - name: Disable SSH Protocol 1
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^Protocol 1'
        line: 'Protocol 1'
        state: absent

    - name: Disable RSA Authentication
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^RSAAuthentication'
        line: 'RSAAuthentication no'
        state: present

    - name: Set SSH Port
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^Port\ '
        line: "Port {{ ssh_port | default(22) }}" #Default to port 22 if ssh_port variable not defined
        state: present

    - name: Disable Root Login
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PermitRootLogin\ '
        line: 'PermitRootLogin no'
        state: present

    - name: Disable Password Authentication
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PasswordAuthentication\ '
        line: 'PasswordAuthentication no'
        state: present

    - name: Disable Empty Passwords
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PermitEmptyPasswords\ '
        line: 'PermitEmptyPasswords no'
        state: present

    - name: Enable Strict Modes
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^StrictModes\ '
        line: 'StrictModes yes'
        state: present

    - name: Ignore Rhosts
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^IgnoreRhosts\ '
        line: 'IgnoreRhosts yes'
        state: present

    - name: Disable Rhosts Authentication
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^RhostsAuthentication\ '
        line: 'RhostsAuthentication no'
        state: present

    - name: Disable Rhosts RSA Authentication
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^RhostsRSAAuthentication\ '
        line: 'RhostsRSAAuthentication no'
        state: present

    - name: Set Client Alive Interval
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^ClientAliveInterval\ '
        line: 'ClientAliveInterval 300'
        state: present

    - name: Set Client Alive Count Max
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^ClientAliveCountMax\ '
        line: 'ClientAliveCountMax 0'
        state: present

    - name: Disable TCP Forwarding
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^AllowTcpForwarding\ '
        line: 'AllowTcpForwarding no'
        state: present

    - name: Disable X11 Forwarding
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^X11Forwarding\ '
        line: 'X11Forwarding no'
        state: present

    - name: Set KexAlgorithms
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^KexAlgorithms\ '
        line: "KexAlgorithms curve25519-sha256@libssh.org,ecdh-sha2-nistp521,ecdh-sha2-nistp384,ecdh-sha2-nistp256,diffie-hellman-group-exchange-sha256"
        state: present

    - name: Set Ciphers
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^Ciphers\ '
        line: "Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr"
        state: present

    - name: Set MACs
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^MACs\ '
        line: "MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512,hmac-sha2-256,umac-128@openssh.com"
        state: present

  handlers:
    - name: restart sshd
      service:
        name: sshd
        state: restarted
```

**Before Running:**

1. **Prepare `authorized_keys`:** Create a file named `authorized_keys` containing the public key for the `adminuser` account.
2. **Inventory File:**  Configure your Ansible inventory file to point to your target servers.
3. **Caution:**  The `sudoers` file is critical.  Errors can lock you out.  Review this section carefully.

**Running the Playbook:**

Execute the playbook using: `ansible-playbook hardening.yml`


**Beyond the Basics:**

This playbook provides a solid foundation. Further enhancements could include:

* **Regular Security Updates:** Integrate Ansible with your update management system.
* **Security Auditing:**  Implement regular security audits using Ansible to monitor system configurations.
* **Vulnerability Scanning:** Integrate Ansible with vulnerability scanning tools.
* **Intrusion Detection Systems (IDS):** Configure and manage IDS using Ansible.

While not necessarily considered as hardening settings, it is common and desirable to use Ansible to configure system updates, logrotate, log shipping, time synchronization and basic system tuning. The playbook below performs those tasks:

```yaml
---
- hosts: webservers
  become: true
  tasks:

    # 1. System Updates and Security Patches
    - name: Update apt cache (Ubuntu/Debian)
      apt:
        update_cache: yes
      when: ansible_distribution == 'Ubuntu' or ansible_distribution == 'Debian'

    - name: Update yum cache (CentOS/RHEL)
      yum:
        update_cache: yes
      when: ansible_distribution == 'CentOS' or ansible_distribution == 'RedHat'

    - name: Upgrade system packages (Ubuntu/Debian)
      apt:
        upgrade: dist
        state: present
      when: ansible_distribution == 'Ubuntu' or ansible_distribution == 'Debian'

    - name: Upgrade system packages (CentOS/RHEL)
      yum:
        update: minimal
        state: present
      when: ansible_distribution == 'CentOS' or ansible_distribution == 'RedHat'

    # 2. Time Synchronization
    - name: Install ntp
      apt:
        name: ntp
        state: present
      when: ansible_distribution == 'Ubuntu' or ansible_distribution == 'Debian'

    - name: Install ntp (CentOS/RHEL)
      yum:
        name: ntp
        state: present
      when: ansible_distribution == 'CentOS' or ansible_distribution == 'RedHat'

    - name: Start NTP service
      service:
        name: ntpd
        state: started
        enabled: yes

    # 3. Logging and Monitoring: Logrotate and Loki/Promtail

    - name: Install logrotate
      apt:
        name: logrotate
        state: present
      when: ansible_distribution == 'Ubuntu' or ansible_distribution == 'Debian'

    - name: Install logrotate (CentOS/RHEL)
      yum:
        name: logrotate
        state: present
      when: ansible_distribution == 'CentOS' or ansible_distribution == 'RedHat'


    - name: Configure logrotate for apache
      template:
        src: logrotate.conf.j2
        dest: /etc/logrotate.d/apache2
      when: ansible_distribution == 'Ubuntu' or ansible_distribution == 'Debian'

    - name: Configure logrotate for httpd
      template:
        src: logrotate.conf.j2
        dest: /etc/logrotate.d/httpd
      when: ansible_distribution == 'CentOS' or ansible_distribution == 'RedHat'

    - name: Install Promtail
      apt:
        name: promtail
        state: present
      when: ansible_distribution == 'Ubuntu' or ansible_distribution == 'Debian'

    - name: Install Promtail (CentOS/RHEL)
       yum: 
         name: promtail 
         state: present
       when: ansible_distribution == 'CentOS' or ansible_distribution == 'RedHat'


    - name: Configure Promtail
      template:
        src: promtail.yml.j2
        dest: /etc/promtail/config.yml

    - name: Start Promtail service
      service:
        name: promtail
        state: started
        enabled: yes


    # 7. Basic System Tuning
    - name: Increase net.core.so_max_conn
      sysctl:
        name: net.core.so_max_conn
        value: "65535"
        state: present
        sysctl_file: /etc/sysctl.conf
    - name: Increase net.ipv4.tcp_max_syn_backlog
      sysctl:
        name: net.ipv4.tcp_max_syn_backlog
        value: "8192"
        state: present
        sysctl_file: /etc/sysctl.conf
```

Template files:

`logrotate.conf.j2`:
```jinja2
/var/log/apache2/*log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

`promtail.yml.j2`:

```jinja2
scrape_configs:
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: system
          __path__: /var/log/apache2/*.log
  - job_name: custom_logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: custom_logs
          __path__: /path/to/your/custom/logs/*.log


client:
  url: http://loki:3100/loki/api/v1/push
```

By automating server hardening with Ansible, you gain significant advantages in efficiency, consistency, and overall security posture.  This approach allows you to manage security effectively, even across large server deployments. Remember to always test your playbooks thoroughly in a non-production environment before deploying them to production servers.