+++
title = "Intro to Ansible"
description = "A comprehensive introduction to Ansible, a powerful automation tool for IT infrastructure management."
date = "2020-10-03"
draft = false
toc = false
tags = ["ansible"]
categories = ["ansible"]
image = "ansible.png"
author = "Fabio M. Lopes"
+++

First, some terminology: With Ansible, a master server can configure a slave server. To do this, the master connects to the slave via SSH and then executes tasks. Each task describes a configuration step, for example installing a package using yum. Each task calls a module that implements the current task, for example the yum module. If a file is to be copied, the copy module is used; the systemd module can be used to manage systemd services, etc. Ansible version 2.7 comes with around 2,100 modules. In addition, additional modules can be easily imported.

# First steps
The first step in using Ansible is to write an inventory. There, users specify which hosts should be orchestrated and they can also be grouped together. Inventories can be written in either YAML or INI format. In the following example, a web server is to be deployed; to do this, create the following inventory:

```yaml
---
all:
  hosts:
    webserver1:
      ansible_host: 10.0.0.2
```

The dict keys all and hosts are specified and reserved by Ansible, so they must not be used for other purposes. A new server is now added to the list of all hosts, which should be known in Ansible as webserver1. Ansible is also informed that it should be available under the IP 10.0.0.2. The ansible_host parameter is used for this. If you want to manage not just one web server, but three and also a database server, you also add these servers to the inventory:

```yaml
---
all:
  hosts:
    webserver1:
      ansible_host: 10.0.0.2
    webserver2:
      ansible_host: 10.0.0.3
    webserver3:
      ansible_host: 10.0.0.4
    dbserver:
      ansible_host: 10.0.1.1
```

In principle, the inventory is finished at this point, but it is recommended to define inventory groups straight away, for example to address all web servers collectively. To do this, a children dict-key is introduced:

```yaml
---
all:
  hosts:
    webserver1:
      ansible_host: 10.0.0.2
    webserver2:
      ansible_host: 10.0.0.3
    webserver3:
      ansible_host: 10.0.0.4
    dbserver1:
      ansible_host: 10.0.1.1
  children:
    webservers:
      hosts:
        webserver1:
        webserver2:
        webserver3:
    dbservers:
      dbserver1:
```

After defining an inventory, Ansible can generally be used in two ways: The ad hoc mode allows you to execute individual tasks, i.e. one-time module calls. For example, you can first test whether all servers in the inventory are accessible to Ansible:

`$ ansible -i inventory.yaml all -m ping`

The inventory to be used is specified with -i. Since Ansible should address all hosts in the inventory, the keyword all is used. Alternatively, you could also write group names webservers and dbservers or the names of individual hosts (webserver1, ...) here. The module for the task is specified with -m. The Ping module does more than a classic ICMP ping. It checks whether an SSH connection between master and slave is possible and whether a compatible version of Python is installed on the slave server.

The output of this command might look like this:

```bash
webserver1 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

After this successful check, further ad hoc commands can now be executed, such as installing a package:

```bash
$ ansible -i inventory.yaml webservers -m package -a "name=nginx state=present" -b

webserver1 | SUCCESS => {
    "cache_update_time": 1553085209,
    "cache_updated": false,
    "changed": true,
    "stderr": "",
    "stderr_lines": [],
    "stdout": "Reading package lists...\nBuilding dependency tree...\nReading state information...\nThe following additional packages will be installed:\n  libnginx-mod-http-geoip libnginx-mod-http-image-filter\n  libnginx-mod-http-xslt-filter libnginx-mod-mail libnginx-mod-stream\n  nginx-common nginx-core\nSuggested packages:\n  fcgiwrap nginx-doc\nThe following NEW packages will be installed:\n  libnginx-mod-http-geoip libnginx-mod-http-image-filter\n  libnginx-mod-http-xslt-filter libnginx-mod-mail libnginx-mod-stream nginx\n  nginx-comm
    .........
}
```

The -b flag causes a privilege escalation so that, for example, a new package can be installed. The -a flag is used to pass the arguments that a module call should contain. In this case, this is the name of the package and the desired state, for example that a package should be installed.

Like most other tools of this type, Ansible complies with the idempotence principle. Users do not write specific commands, but rather define which state a system should reach, i.e. that a package should be installed. If - tailored to the specific case - nginx should be present on a web server, Ansible will either reinstall the package or simply do nothing if the package is already present. This behavior can also be observed when the call is made a second time:

```bash
$ ansible -i inventory.yaml webservers -m package -a "name=nginx state=present" -b

webserver1 | SUCCESS => {
    "cache_update_time": 1553085209,
    "cache_updated": false,
    "changed": false
}

webserver2 | SUCCESS => {
    "cache_update_time": 1553085209,
    "cache_updated": false,
    "changed": false
}

webserver3 | SUCCESS => {
    "cache_update_time": 1553085209,
    "cache_updated": false,
    "changed": false
}
```

Ansible – like any configuration management system – requires information about the host it is supposed to manage:

- Operating system
- CPU
- RAM
- Network
- Installed packages
- ...

The setup module is used to collect and display this:

```bash
$ ansible  -i inventory.yaml webserver1 -m setup

webserver2 | SUCCESS => {
    "ansible_facts": {
        "ansible_all_ipv4_addresses": [
            "10.0.0.3",
            "10.0.122.1",
        ],
        "ansible_all_ipv6_addresses": [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "2001:db8:3333:4444:5555:6666:7777:8888",
        ],
        "ansible_apparmor": {
            "status": "enabled"
        },
        "ansible_architecture": "x86_64",
        "ansible_bios_date": "03/01/2019",
        "ansible_bios_version": "1.5.0",
        ...
      }
}
```

# Installation and configuration
Installing and configuring a web server usually involves more than one task:

- Configuring the firewall
- Installing the nginx package
- Adjusting the nginx configuration
- Restarting the nginx service
- Setting a message-of-the-day per server

If you want to combine several tasks, you use a playbook. In this, the hosts key is first used to define in YAML syntax which hosts of the inventory the playbook should run on; in the example below, on all members of the webservers group. Then all tasks are defined under the tasks key, which should also run in exactly this order. Below is the finished playbook, which will be explained in its individual steps.

```bash
- hosts: webservers
  tasks:
    - name: Open port 80
      become: true
      firewalld:
        service: http
        permanent: true
        state: enabled
      register: firewall_setting

    - name: Restart the firewalld service
      become: true
      service:
        name: firewalld
        state: restarted
      when: firewall_setting.changed

    - name: Install nginx
      become: true
      package:
        name: "nginx-{{ nginx_version }}"
        state: present

    - name: Copy stylesheet in place
      become: true
      copy:
        src: stylesheet.css
        dest: "{{ nginx_root }}/stylesheet.css"
      register: stylesheet

    - name: Create default page
      become: true
      template:
        src: index.html.j2
        dest: "{{ nginx_root }}/index.html"
      register: indexfile

    - name: Restart nginx service
      become: true
      service:
        name: nginx
        state: restarted
      when: indexfile.changed or stylesheet.changed

    - name: Setup motd
      become: true
      template:
        src: motd.j2
        dest: /etc/motd
```

The folder structure now looks like this:

```bash
.
|
├── inventory.yaml
└── playbook.yaml
```

The first task uses the firewalld module to allow the http service within the firewall. The task also has a register parameter. If you specify this, Ansible saves the result of the task in a variable. The task also contains the parameter become: true. This means that this task is executed with rights escalation (the default is sudo). This authorization can also be set globally for the entire playbook, but for security and audit reasons it is recommended to work in a fine-grained manner and "authorize" each task individually.

After reconfiguring the firewall, it should be restarted - for this purpose the service module is used, which is intended for systemd-based services, among other things.

However, the restart should only happen if the previous task has resulted in a change: This behavior is controlled by the when parameter and the query of the firewall_setting variable, which was defined in the first task.

In the third task, the package module installs the nginx package on the web servers. To do this, the desired state is passed on - in this case present - and the name of the nginx package. Alternatively, the latest state could also be used, which would reference the latest version that the system gets from its respective package sources. In this case, the name is {{ nginx_version | default("1.15.5")}}. This is the first example of how variables can be used in Ansible.

Jinja syntax is used for this in Ansible. Variables are always put in {{ }} blocks. A variable called nginx_version must therefore be defined here. This can be saved in a file `./group_vars/webservers.yaml`, for example:

```yaml
---
nginx_version: 1.1.15
```

The folder structure now looks like this:

```bash
.
|
├── group_vars
│   └── webservers.yaml
├── inventory.yaml
└── playbook.yaml
```

Variables will be discussed in more detail later. For now, however, it should be mentioned that all variables defined in `group_vars/webservers.yaml` are available to all hosts that belong to the inventory group webservers. Similarly, you can create a `group_vars/all.yaml` file whose values ​​then apply to all hosts in all inventory groups.

The next two tasks should now deliver a static website that should display information about the server's operating system. To do this, first use the copy module to copy a CSS stylesheet into the root folder of the nginx web server, which the static website should later use. Before this can happen, the nginx_root variable must be set:

```yaml
#group_vars/all.yaml
---
nginx_version: 1.12.2
nginx_root: "/usr/share/nginx/html"
```

For the website itself, the host facts that were previously used in connection with the setup module are used. If not explicitly prevented, Ansible collects these facts as the very first "internal" task in every playbook run, before the first user-defined task runs. Therefore, variables such as `ansible_distribution`, `ansible_os_family`, `ansible_all_ipv4_adresses`, etc. are available during the playbook.

The following template is used for the website:

```html
<html>
<head>
<title>Information page: {{ ansible_hostname }}</title>
<style type="text/css">@import url('./stylesheet.css') all;</style>
</head>
<body>
<h1>Information about running host</h1>

<table>
  <tr> <th colspan='2'>OS Facts</th> </tr>
  <tr> <td>This system is running on</td> <td>{{ ansible_distribution }}</td> </tr>
  <tr> <td>Version:</td> <td>{{ ansible_distribution_version }}</td> </tr>
  <tr> <td>OS Family:</td> <td>{{ ansible_os_family}}</td> </tr>
  <tr> <td>Used package manager:</td> <td>{{ ansible_pkg_mgr }}</td> </tr>
  <tr> <td>AppArmor</td> <td>{{ ansible_apparmor['status'] }}</td> </tr>
  <tr> <td>Selinux</td> <td>{{ ansible_selinux['status'] }}</td> </tr>
  <tr> <td>Python Version</td> <td>{{ ansible_python_version }}</td> </tr>
</table>

<table style='float:left;margin-right:50px'>
  <tr> <th colspan='2'>Network information</th> </tr>
  <tr> <td>Hostname</td> <td>{{ ansible_nodename }}</td> </tr>
  <tr> <td>IPv4 addresses</td> <td>{{ ", ".join(ansible_all_ipv4_addresses) }}</td> </tr>
  <tr> <td>IPv6 addresses</td> <td>{{ ", ".join(ansible_all_ipv6_addresses) }}</td> </tr>
  <tr> <td>DNS servers</td>    <td>{{ ", ".join(ansible_dns['nameservers']) }}</td> </tr>
  <tr> <td>DNS search domain</td> <td>{{ ", ".join(ansible_dns['search']) }}</td> </tr>
  {% for key, value in ansible_default_ipv4.iteritems() %}
  <tr> <td>Default IPv4 interface -- {{ key }}</td> <td>{{ value }}</td> </tr>
  {% endfor %}
  {% for key, value in ansible_default_ipv6.iteritems() %}
  <tr> <td>Default IPv6 interface -- {{ key }}</td> <td>{{ value }}</td> </tr>
  {% endfor %}
  <tr> <td>Hostname</td> <td>{{ ansible_hostname }}</td> </tr>
  <tr> <td>FQDN</td> <td>{{ ansible_fqdn }}</td> </tr>
</table>

<table>
  <tr> <th colspan='2'>Environment variables</th> </tr>
  {% for key, value in ansible_env.iteritems() %}
  <tr> <td>{{ key }}</td><td>{{ value }}</td> </tr>
  {% endfor %}
</table>

</body>
</html>
```

The variables included in Jinja syntax are then filled in by Ansible when the file is copied to the desired location using the template module. Template files are given the file extension .j2. With the template file and the stylesheet you then get the following folder structure:

```bash
.
|
├── group_vars
│   └── webservers.yaml
├── index.html.j2
├── inventory.yaml
├── playbook.yaml
└── stylesheet.css
```

The following task is similar to restarting the firewall service: If the index file or the stylesheet changes during deployment, nginx should be restarted. This is not necessarily necessary; the delivered files can also be changed during operation. The last task should now set a message of the day, i.e. a message that is displayed when logging into the server via SSH. Here, too, the template module is used to copy the desired file to etc/motd. A motd.j2 template file is added:

```bash
.
|
├── group_vars
│   └── webservers.yaml
├── index.html.j2
├── inventory.yaml
├── motd.j2
└── playbook.yaml

# motd.j2
Hello and welcome on {{ ansible_hostname }}.
This is a {{ ansible_distribution }}-Server running in Version {{ ansible_distribution_version }}.
This is the {{ webserver_name }} instance.
Please note: This server is deployed and managed with Ansible.
```

The ansible_* variables come from the host facts, similar to the website template. However, this does not apply to webserver_name. Since this variable should be different for each server, it must also be set accordingly. There are several ways to do this. Two of them will be presented here.

1. Analogous to the variables defined for inventory groups in the group_vars folder, this can also happen for individual hosts:

```bash
.
|
├── group_vars
│   └── webservers.yaml
├── host_vars
│   ├── webserver1.yaml
│   ├── webserver2.yaml
│   └── webserver3.yaml
├── index.html.j2
├── inventory.yaml
├── motd.j2
└── playbook.yaml
```

```yaml
# host_vars/webserver1.yaml
---
webserver_name: "Webserver 1"
```

```yaml
# host_vars/webserver2.yaml
---
webserver_name: "Webserver 2"
```

```yaml
# host_vars/webserver3.yaml
---
webserver_name: "Webserver 3"
```

Variables defined in this way only apply to the host with the same name as the file.

2. Variables at host level can also be defined in the inventory file:

```yaml
# inventory.yaml
---
all:
  hosts:
    webserver1:
      ansible_host: 10.0.0.2
      webserver_name: "Webserver 1"
    webserver2:
      ansible_host: 10.0.0.3
      webserver_name: "Webserver 2"
    webserver3:
      ansible_host: 10.0.0.4
      webserver_name: "Webserver 3"
    dbserver1:
      ansible_host: 10.0.1.1
  children:
    webservers:
      hosts:
        webserver1:
        webserver2:
        webserver3:
    dbservers:
      dbserver1:
```

The playbook is now basically finished and ready to run:

```bash
$ ansible-playbook playbook.yaml -i inventory.yaml

PLAY [webservers] *************************************************************

TASK [Gathering Facts] ********************************************************
ok: [webserver1]
ok: [webserver2]
ok: [webserver3]

TASK [Open port 80] *******************************************
changed: [webserver1]
changed: [webserver2]
changed: [webserver3]

TASK [Restart the firewalld service] **********
changed: [webserver1]
changed: [webserver2]
changed: [webserver3]

TASK [Install ginx] *********************************************
changed: [webserver1]
changed: [webserver2]
changed: [webserver3]

TASK [Create default page] ****************************************************
changed: [webserver1]
changed: [webserver2]
changed: [webserver3]

TASK [Restart nginx service] **************************************************
changed: [webserver1]
changed: [webserver2]
changed: [webserver3]

TASK [Setup motd] *************************************************************
changed: [webserver1]
changed: [webserver2]
changed: [webserver3]

PLAY RECAP ********************************************************************
webserver1                 : ok=7    changed=6    unreachable=0    failed=0
webserver2                 : ok=7    changed=6    unreachable=0    failed=0
webserver3                 : ok=7    changed=6    unreachable=0    failed=0
```

Collecting the facts is considered the first task, and this is the only task that does not cause any changes when it is initially executed. So that you do not always have to specify the inventory when executing a playbook, you can also create a configuration file `ansible.cfg`:

```bash
.
|
├── ansible.cfg
├── group_vars
│   └── webservers.yaml
├── host_vars
│   ├── webserver1.yaml
│   ├── webserver2.yaml
│   └── webserver3.yaml
├── index.html.j2
├── inventory.yaml
├── motd.j2
└── playbook.yaml
```

```bash
# ansible.cfg
[defaults]
inventory=./inventory
```

By default, Ansible creates a default configuration file in `/etc/ansible.cfg`. However, this can be overwritten with a file `~/.ansible.cfg` or a local one, as in this case. Ansible prioritizes these files in reverse order:

- path specified in ANSIBLE_CONFIG environment variable
- local in `./ansible.cfg`
- `~/.ansible.cfg`
- `/etc/ansible.cfg`

In the file, you can not only specify one (or any number of additional) inventories, but also configure Ansible in numerous other ways:

- SSH parameters, options
- additional external modules
- connection parameters
- ...

Many of these parameters can also be set as environmental variables. A complete list can be displayed using the CLI tool ansible-config.

# The role concept

The final playbook now contains a number of tasks, but these are not easily reusable. To solve this problem and generally create more modularity, Ansible offers the role concept. If you transfer this to the nginx example, the folder structure changes:

```bash
.
├── ansible.cfg
├── group_vars
│   └── webservers.yaml
├── host_vars
│   └── webserver1.yaml
├── inventory.yaml
├── playbook.yaml
└── roles
    └── nginx
        ├── defaults
        │   └── main.yaml
        ├── files
        │   └── stylesheet.css
        ├── tasks
        │   └── main.yaml
        ├── templates
        │   ├── index.html.j2
        │   └── motd.j2
        └── vars
            └── main.yaml
```

The playbook also looks different now:

```yaml
- hosts: webservers
  roles:
    - nginx
```

Tasks are no longer called there, but a list of roles. In this case, this list only contains one element: the role for the nginx installation. This role can be found in the nginx subfolder of the new roles folder. The main entry point for a role is the main.yaml file in the tasks folder. All tasks that were previously in the playbook can now be found there:

```yaml
# roles/nginx/tasks/main.yaml
---
- name: Open port 80
  become: true
  firewalld:
    service: http
    permanent: true
    state: enabled
  register: firewall_setting

  [...]
```

In addition, a role has the following folders:

- files: This is where you can find files (except templates!) that the role uses. In this case, stylesheet.css.
- templates: This is where you can find templates that the role uses. In this case, the website itself and the motd template.
- `vars/defaults`: This is where you can find variables that a role uses. Depending on the purpose, these can be stored in both `/vars/main.yaml` and `defaults/main.yaml`.

When placing variables in different places, it is important to understand the order of these definition places. The following list contains (in ascending order) only the places that have been mentioned so far in this article. A complete list can be found in the Ansible documentation [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#id36).

- variables in `/role/defaults/main.yaml`,
- variables in `inventory.yaml`,
- variables in `group_vars/*.yaml`,
- variables in `host_vars/*.yaml`,
- variables that were automatically determined from the setup module and
- variables in `/role/vars/main.yaml`.

If you imagine a role that is supposed to install an Apache web server on Debian, the following options for variable placement arise:

The standard version number of the Apache installation is set in `roles/apache/defaults/main.yaml`. This can easily be overwritten later if necessary. The standard path for the root directory of the web server and the ports that are to be used are also set.

```yaml
--- roles/apache/defaults/main.yaml
apache_root: "/var/www/html"
apache_version: 2.4.29
apache_listen_port: 80
apache_listen_ssl_port: 443
```

`roles/apache/vars/main.yaml` contains the name of the packages that are installed during the role. These are fixed, i.e. overwriting is not necessary.

```yaml
---
apache_packages:
  - apache2
  - apache2-utils

```

A good role is reusable and transferable, which means that it is not limited to a single operating system, for example. If we take the Apache example again, there are differences in the package naming for Debian and Redhat, for example. In order to be able to use a role generically for this, we once again make use of Ansible facts.

The following examples can be found [here](https://github.com/geerlingguy/ansible-role-apache). The directory structure looks simplified as follows:

```bash
.
├── playbook.yaml
└── roles
    └── apache
        ├── handlers
        │   └── main.yaml
        ├── tasks
        │   └── main.yaml
        └── vars
            ├── Debian.yaml
            └── RedHat.yaml
```

Depending on the operating system, either the variables from `roles/apache/vars/Debian.yaml` or `roles/apache/vars/RedHat.yaml` should be included:

```yaml
---
#roles/apache/vars/Debian.yaml
apache_server_root: /etc/apache2
apache_service_name: apache2
apache_packages:
  - apache2
  - apache2-utils
```

```yaml
--- 
#roles/apache/vars/RedHat.yaml
apache_server_root: /etc/httpd
apache_service_name: httpd
apache_packages:
  - httpd
  - httpd-devel
  - mod_ssl # Debian already ships the SSL module in `apache2`
```

In roles/apache/tasks/main.yaml findet sich folgendes:

```yaml
---
- name: Include OS-specific parameters
  include_vars: {{ ansible_os_family }}.yaml

- name: Install apache packages
  package:
    name: "{{ apache_packages }}"
    state: present
  notify: restart apache

- name: Activate mod_ssl if Debian
  file:
    src: "{{ apache_server_root }}/mods-available/mod_ssl"
    dest: "{{ apache_server_root }}/mods-enabled/mod_ssl"
    state: link
  notify: restart apache
  when: ansible_os_family == 'Debian'"
```

The first task uses the include_vars module to include the variable file appropriate for the current distribution. The second task then installs the packages defined in the respective file. The last task is a Debian peculiarity:

The Apache installation already includes various modules by default. To activate them, you can either use the CLI tool `a2enmod`, or you can create file links "by hand" from

```
/etc/apache2/mods-available/<mod_name> 
```
after

```
/etc/apache2/mods-enabled/<mod_name>
```

The latter also happens in the task shown here, with the help of the file module. The when line ensures that a task is only executed if the following condition is evaluated as true. In this case, an operating system from the Debian family.

After activating a module, the server must be restarted. The handler concept is used here for this. Handlers are tasks that can be triggered at any point in the playbook. After the playbook has been completed, all handlers that were triggered during the playbook are processed in the order in which they were defined. In the Apache example, there is exactly one handler task:

```yaml
#/roles/apache/handlers/main.yaml
---
- name: restart apache
  service:
    name: "{{ apache_service_name }}"
    state: restarted
```

A handler is triggered in the context of a task with the key notify and the task name of the handler. If you look more closely, you will notice that the task that installs the Apache packages also calls the same handler. This is due to the fact that in the RedHat scenario the Apache SSL module is installed as a separate package. In the Debian case, the handler is thus triggered twice. However, this does not mean that it is executed twice - even triggering a handler multiple times only results in it being executed once.

With the tag concept, Ansible can execute individual tasks of a playbook and skip all others. This can be explained well using an example: A company writes Java web applications, which it packages in war files using Maven and then deploys on a TomCat server. The latest test version is to be deployed and tested on a TomCat every night. Both the initial installation of TomCat and the nightly deployment of the latest version should be done with Ansible. The following playbook was written for this purpose:

```yaml
---
- name: Install Tomcat Server
  import_tasks: tomcat_setup.yaml
  tags:
    - inital_setup

- name: Deploy war file
   maven_artifact:
    group_id: com.company
    artifact_id: web-app
    version: latest
    extension: war
    repository_url: 'https://repo.company.com/maven'
    dest: /var/lib/tomcat7/webapps/web-app.war
  notify: restart_tomcat
  tags:
    - initial_setup
    - nightly_test
```

The first task uses `import_tasks` to import a yaml file that contains all the tasks for installing and configuring a TomCat server. The second task downloads the latest version of the webapp as a war file, puts it in the TomCat server's webapp folder, and triggers a handler that starts the TomCat server. In addition, both tasks have tags: the first only **initial_setup**, the second **initial_setup** and **nightly_test**.

This definition allows the following to be done:
 - ansible-playbook tomcat.yaml runs the playbook as usual, all tasks are executed.
 - ansible-playbook tomcat.yaml --tags <tag_name> executes all tasks that have been tagged with the corresponding tag.
 - ansible-playbook tomcat.yaml --tags initial_setup would also execute both tasks in this case. On the other hand, with `ansible-playbook tomcat.yaml --tags nightly_test`, only the new version of the web application can be deployed every night, without Ansible also checking the initial setup again for implementation and changes.

# Conclusion
This article is of course not intended to be and cannot be a comprehensive and complete presentation of Ansible: There is much more that can be said about each of the points mentioned here. If you are interested, you can either take a look at the official Ansible documentation [here](https://docs.ansible.com/) or the community: be it in the form of IRC channels (#ansible, #ansible-dev) or the numerous relevant meet-ups and lectures that now exist.

The ideas and concepts shown here are intended to convey enough to give an initial insight and to dare to get started - it's worth it.