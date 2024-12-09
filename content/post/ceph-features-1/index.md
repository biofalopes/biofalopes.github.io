+++
title = "Ceph features and its relation to the client kernel version"
description = "How the kernel version used on rbd/cephfs clients reflects on ceph features from the cluster perspective"
date = "2020-11-16"
draft = false
toc = false
categories = ["ceph"]
tags = ["ceph"]
image = "ceph_banner.png"
+++

While working on an upgrade on one of our ceph cluster from Luminous to Nautilus, i needed to come up with a way to detect any client with older versions, and check if we could break anything after the upgrade.
<!--more--->  
I started checking the documentation as always, but all i found was a command called `ceph features`, which gives a summarized output:

```
[root@mon-1 ~]# ceph features
{
    "mon": {
        "group": {
            "features": "0x3ffddff8eeacfffb",
            "release": "luminous",
            "num": 3
        }
    },
    "mds": {
        "group": {
            "features": "0x3ffddff8eeacfffb",
            "release": "luminous",
            "num": 3
        }
    },
    "osd": {
        "group": {
            "features": "0x3ffddff8eeacfffb",
            "release": "luminous",
            "num": 192
        }
    },
    "client": {
        "group": {
            "features": "0x27018fb86aa42ada",
            "release": "jewel",
            "num": 422
        },
        "group": {
            "features": "0x2f018fb86aa42ada",
            "release": "luminous",
            "num": 95
        },
        "group": {
            "features": "0x3ffddff8eeacfffb",
            "release": "luminous",
            "num": 18
        }
    }
}
```

So that got me worried, since I was now looking at 422 clients apparently using jewel and we were already using Nautilus for a while. Since this specific cluster was "born" in jewel, I thought that it might be the case that many clients didn't get any upgrades since.

Another way to see who's connected to the cluster is the command `ceph tell mds.\`hostname\` client ls`, but it shows only cephfs clients, which solves only a part of the problem. At least we can see the client's IP address (adresses and names omitted with [...]):

```
"inst": "client.1400410 v1:[...]]:0/1769731892",
        "completed_requests": [],
        "prealloc_inos": [],
        "used_inos": [],
        "client_metadata": {
            "features": "0x00000000000001ff",
            "entity_id": [...],
            "hostname": [...],
            "kernel_version": "4.19.[...]",
            "root": [...]
        }
```

**Short note**: there's no documentation explaining those codes and its respective features, so I'm going to look at the source code and try to come up with a table. I'll post it as soon as I manage to.

Searching further i came across the command `ceph daemon mon.hostname sessions`:

```
[root@mon-1 ~]# ceph daemon mon.`hostname` sessions | grep jewel
    "MonSession(client.354037 v1:[...]]:0/3173650400 is open allow profile rbd, features 0x27018fb86aa42ada (jewel))",
    "MonSession(client.394132 v1:[...]:0/295867623 is open allow profile rbd, features 0x27018fb86aa42ada (jewel))",
    "MonSession(client.785407 v1:[...]:0/507474248 is open allow profile rbd, features 0x27018fb86aa42ada (jewel))",
    "MonSession(client.367883 v1:[...]:0/3274665177 is open allow profile rbd, features 0x27018fb86aa42ada (jewel))",
    "MonSession(client.812187 v1:[...]:0/733157529 is open allow profile rbd, features 0x27018fb86aa42ada (jewel))",
    "MonSession(client.1390811 v1:[...]:0/1470215921 is open allow r, features 0x27018fb86aa42ada (jewel))",
    "MonSession(client.1400452 v1:[...]:0/3851374868 is open allow r, features 0x27018fb86aa42ada (jewel))",
```

Now i started to see some light at the end, since that command gave me the ip address and the version for each client connected. I knew that we didn't have any clients using ceph-fuse, so it was safe to assume that everyone was using the kernel module to mount either RBD or cephfs. That cleared some confusion I had at the beginning between the `ceph-common` package version and the kernel version. It is not required to have that package installed in order to use the kernel module, so i then pointed my efforts at checking the clients' kernel versions.

The documentation also recommended some debugging at mon:

> The ceph features command that reports the total number of clients and daemons and their features and releases.
> If the debugging level for Monitors is set to 10 (debug mon = 10), addresses and features of connecting and disconnecting clients are logged to log file on a local file system.

So i tried that and here's what we get with `debug mon = 10`:

```
2020-11-10 08:55:59.084 7f31c9015700  0 --1- [v2:[...]:3300/0,v1:[...]:6789/0] >>  conn(0x561a94aed180 0x561a94ba5000 :6789 s=ACCE
PTING pgs=0 cs=0 l=0).handle_client_banner accept peer addr is really - (socket is v1:[...]:40764/0)
2020-11-10 08:55:59.085 7f31c500d700 10 mon.ceph-1@0(leader) e1 ms_handle_accept con 0x561a94aed180 no session
2020-11-10 08:55:59.085 7f31c500d700 10 mon.ceph-1@0(leader) e1 _ms_dispatch new session 0x561a94adcd80 MonSession(unknown.0 - is open , featu
res 0x27018fb86aa42ada (jewel)) features 0x27018fb86aa42ada
2020-11-10 08:55:59.085 7f31c500d700 10 mon.ceph-1@0(leader).auth v3676 preprocess_query auth(proto 0 34 bytes epoch 0) from unknown.0 -
2020-11-10 08:55:59.085 7f31c500d700 10 mon.ceph-1@0(leader).auth v3676 prep_auth() blob_size=34
2020-11-10 08:55:59.085 7f31c500d700 10 mon.ceph-1@0(leader).auth v3676 _assign_global_id 34110 (max 44096)
2020-11-10 08:55:59.085 7f31c500d700  2 mon.ceph-1@0(leader) e1 send_reply 0x561a958ba780 0x561a95246fc0 auth_reply(proto 2 0 (0) Success) v1
2020-11-10 08:55:59.086 7f31c500d700 10 mon.ceph-1@0(leader).auth v3676 preprocess_query auth(proto 2 32 bytes epoch 0) from unknown.0 -
2020-11-10 08:55:59.086 7f31c500d700 10 mon.ceph-1@0(leader).auth v3676 prep_auth() blob_size=32
2020-11-10 08:55:59.086 7f31c500d700 10 mon.ceph-1@0(leader) e1 ms_handle_authentication session 0x561a94adcd80 con 0x561a94aed180 addr - MonSession(unknown.0 - is open , features 0x27018fb86aa42ada (jewel))
```

Without `debug mon = 10`, only the first line is logged.

That is very useful to detect the clients' features when they are connecting, but not so much when you can't have the luxury to reset everyone's connection. Besides, leaving that level of debugging enabled all the time would flag our node as an abuser at the log server in a matter of hours.

What i knew already about our clients was that there was some elastic nodes using RBD, probably with CentOS 7 and consequently using kernel 3.x; Some other stuff also using RBD on either CentOS 7 or CentOS 8; and a kubernetes cluster using CoreOS and Flatcar with kernel 4.x. So after some checking, I compared the output from a client using kernel 4.19.x and another with 5.4.x:

**4.19.x:**
```
[root@mon-1 ~]# ceph daemon mon.`hostname` sessions | grep [...]
    "MonSession(client.95408384 [...]:0/923650579 is open allow r, features 0x27018fb86aa42ada (jewel))",
    "MonSession(client.95446387 [...]:0/421761626 is open allow r, features 0x27018fb86aa42ada (jewel))",
    "MonSession(client.95427342 [...]:0/1106672011 is open allow r, features 0x27018fb86aa42ada (jewel))",
    "MonSession(unknown.0 [...]:0/2823489235 is open allow r, features 0x27018fb86aa42ada (jewel))",
    "MonSession(unknown.0 [...]:0/4141488860 is open allow r, features 0x27018fb86aa42ada (jewel))",
    "MonSession(unknown.0 [...]:0/662892667 is open allow r, features 0x27018fb86aa42ada (jewel))",
    "MonSession(unknown.0 [...]:0/940509445 is open allow r, features 0x27018fb86aa42ada (jewel))",
    "MonSession(unknown.0 [...]:0/1147570690 is open allow r, features 0x27018fb86aa42ada (jewel))",
```

**5.4.x:**
```
root@mon-1 ~]# ceph daemon mon.`hostname` sessions | grep [...]
    "MonSession(unknown.0 [...]:0/2258512824 is open allow r, features 0x2f018fb86aa42ada (luminous))",
    "MonSession(unknown.0 [...]:0/4186418195 is open allow r, features 0x2f018fb86aa42ada (luminous))",
    "MonSession(unknown.0 [...]:0/232634731 is open allow r, features 0x2f018fb86aa42ada (luminous))",
    "MonSession(client.95587947 [...]:0/3963151684 is open allow r, features 0x2f018fb86aa42ada (luminous))",
    "MonSession(unknown.0 [...]:0/1164059037 is open allow r, features 0x2f018fb86aa42ada (luminous))",
    "MonSession(unknown.0 [...]:0/1228306108 is open allow r, features 0x2f018fb86aa42ada (luminous))",
    "MonSession(unknown.0 [...]:0/2811111809 is open allow r, features 0x2f018fb86aa42ada (luminous))",
    "MonSession(unknown.0 [...]:0/4254695077 is open allow r, features 0x2f018fb86aa42ada (luminous))",
    "MonSession(client.95587926 [...]:0/479729343 is open allow r, features 0x2f018fb86aa42ada (luminous))",
    "MonSession(unknown.0 [...]:0/340770437 is open allow r, features 0x2f018fb86aa42ada (luminous))",
    "MonSession(unknown.0 [...]:0/425381347 is open allow r, features 0x2f018fb86aa42ada (luminous))",
```

After that I could come with some conclusion. We'll probably keep seeing jewel features for a long time, since CentOS/RHEL 8 and most of the main distros uses kernel 4.x on their latest LTS versions. I expected that at kernel 3.x i'd get Jewel features and from 4.x on we would get Luminous, but apparently the latest features are only available on kernels 5.x and beyond. I'm not sure if there is any feature that would be marked as nautilus or any newer ceph version, so I still need to dig deeper on that subject.

**References:**

https://ceph.io/community/new-luminous-upgrade-complete/

https://docs.ceph.com/en/latest/rados/operations/upmap/#enabling

https://docs.ceph.com/en/latest/man/8/ceph/#osd

https://access.redhat.com/documentation/en-us/red_hat_ceph_storage/3.0/html/release_notes/major_updates