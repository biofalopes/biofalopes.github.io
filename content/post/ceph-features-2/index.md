+++
title = "Obtaining a list of Ceph features from the hexadecimal value"
description = "Simple python script that gets a hexadecimal value from the command 'ceph features' and outputs a list of the actual features."
date = "2020-11-16"
draft = false
toc = false
categories = ["ceph", "python"]
tags = ["ceph", "python"]
image = "cephalopod.png"
author = "Fabio M. Lopes"
+++

After some digging i found the list of possible features, its respective kernel version requirement and/or when it became available.
<!--more---> 
This can be found in `src/include/ceph_features.h`, and I got it by cloning the ceph repo at git://github.com/ceph/ceph .

That information might be useful when you are trying to determine if your clients might need a kernel upgrade and what kind of RBD or cephfs features you can enable on your server side without breaking compatibility. It's always ideal to have every new feature availabe whenever possible, but that is not always the case when you have a medium to large deployment, multiple clients with different workloads and scenarios - in other words, a Real World situation.

```
import sys

feature_list = [
    "( 0, 1, UID)",
    "( 1, 1, NOSRCADDR) // 2.6.35 req",
    "( 2, 3, SERVER_NAUTILUS)",
    "( 3, 1, FLOCK) // 2.6.36",
    "( 4, 1, SUBSCRIBE2) // 4.6 req",
    "( 5, 1, MONNAMES)",
    "( 6, 1, RECONNECT_SEQ) // 3.10 req",
    "( 7, 1, DIRLAYOUTHASH) // 2.6.38",
    "( 8, 1, OBJECTLOCATOR)",
    "( 9, 1, PGID64) // 3.9 req",
    "(10, 1, INCSUBOSDMAP)",
    "(11, 1, PGPOOL3) // 3.9 req",
    "(12, 1, OSDREPLYMUX)",
    "(13, 1, OSDENC) // 3.9 req",
    "(14, 2, SERVER_KRAKEN)",
    "(15, 1, MONENC)",
    "(16, 3, SERVER_OCTOPUS) | (16, 3, OSD_REPOP_MLCOD)",
    "(17, 3, OS_PERF_STAT_NS)",
    "(18, 1, CRUSH_TUNABLES) // 3.6",
    "(19, 2, OSD_PGLOG_HARDLIMIT)",
    "(20, 3, SERVER_PACIFIC)",
    "(21, 2, SERVER_LUMINOUS) // 4.13 | (21, 2, RESEND_ON_SPLIT) | (21, 2, RADOS_BACKOFF) | (21, 2, OSDMAP_PG_UPMAP) | (21, 2, CRUSH_CHOOSE_ARGS)",
    "(22, 2, OSD_FIXED_COLLECTION_LIST)",
    "(23, 1, MSG_AUTH) // 3.19 req (unless nocephx_require_signatures)",
    "(24, 2, RECOVERY_RESERVATION_2)",
    "(25, 1, CRUSH_TUNABLES2) // 3.9",
    "(26, 1, CREATEPOOLID)",
    "(27, 1, REPLY_CREATE_INODE) // 3.9",
    "(28, 2, SERVER_MIMIC)",
    "(29, 1, MDSENC) // 4.7",
    "(30, 1, OSDHASHPSPOOL) // 3.9",
    "DEPRECATED(31, 1, MON_SINGLE_PAXOS, NAUTILUS)",
    "(32, 3, STRETCH_MODE)",
    "RETIRED(33, 1, MON_SCRUB, JEWEL, LUMINOUS)",
    "RETIRED(34, 1, OSD_PACKED_RECOVERY, JEWEL, LUMINOUS)",
    "(35, 1, OSD_CACHEPOOL) // 3.14",
    "(36, 1, CRUSH_V2) // 3.14",
    "(37, 1, EXPORT_PEER) // 3.14",
    "RETIRED(38, 1, OSD_ERASURE_CODES, MIMIC, OCTOPUS)",
    "(39, 1, OSDMAP_ENC) // 3.15",
    "(40, 1, MDS_INLINE_DATA) // 3.19",
    "(41, 1, CRUSH_TUNABLES3) // 3.15 | (41, 1, OSD_PRIMARY_AFFINITY)",
    "(42, 1, MSGR_KEEPALIVE2) // 4.3 (for consistency)",
    "(43, 1, OSD_POOLRESEND) // 4.13",
    "RETIRED(44, 1, ERASURE_CODE_PLUGINS_V2, MIMIC, OCTOPUS)",
    "RETIRED(45, 1, OSD_SET_ALLOC_HINT, JEWEL, LUMINOUS)",
    "(46, 1, OSD_FADVISE_FLAGS)",
    "(47, 1, MDS_QUOTA) // 4.17",
    "(48, 1, CRUSH_V4) // 4.1",
    "RETIRED(49, 1, OSD_MIN_SIZE_RECOVERY, JEWEL, LUMINOUS)",
    "RETIRED(50, 1, MON_METADATA, MIMIC, OCTOPUS)",
    "RETIRED(51, 1, OSD_BITWISE_HOBJ_SORT, MIMIC, OCTOPUS)",
    "RETIRED(52, 1, OSD_PROXY_WRITE_FEATURES, MIMIC, OCTOPUS)",
    "RETIRED(53, 1, ERASURE_CODE_PLUGINS_V3, MIMIC, OCTOPUS)",
    "RETIRED(54, 1, OSD_HITSET_GMT, MIMIC, OCTOPUS)",
    "RETIRED(55, 1, HAMMER_0_94_4, MIMIC, OCTOPUS)",
    "(56, 1, NEW_OSDOP_ENCODING) // 4.13 (for pg_pool_t >= v25)",
    "(57, 1, MON_STATEFUL_SUB) // 4.13 | (57, 1, SERVER_JEWEL)",
    "(58, 1, CRUSH_TUNABLES5) // 4.5 | (58, 1, NEW_OSDOPREPLY_ENCODING) | (58, 1, FS_FILE_LAYOUT_V2)",
    "(59, 1, FS_BTIME) | (59, 1, FS_CHANGE_ATTR) | (59, 1, MSG_ADDR2)",
    "(60, 1, OSD_RECOVERY_DELETES) // *do not share this bit*",
    "(61, 1, CEPHX_V2) // 4.19, *do not share this bit*",
    "(62, 1, RESERVED) // do not use; used as a sentinel",
    "DEPRECATED(63, 1, RESERVED_BROKEN, LUMINOUS) // client-facing"
]

def settolist(featureset):
    '''Converts a featureset hex to a feature list.
    
    Parameters:
    int:featureset

    Returns:
    list:featureset_list
    '''
    featureset_hex = featureset
    featureset_list = []
    featureset_bin = bin(int(featureset_hex, 16))[2:].zfill(64)
    count = 0
    for bit in (featureset_bin):
        if bit == '1':
            featureset_list.append(feature_list[count])
        count += 1
    return featureset_list

output = settolist(str(sys.argv[1]))
print("\n".join(output))
```
A test run using an entry from my test cluster:

`MonSession(client.95280473 [IP]:0/110518927 is open allow profile rbd, features 0x27018fb86aa42ada (jewel))"`

```
python features.py 0x27018fb86aa42ada

( 2, 3, SERVER_NAUTILUS)
( 5, 1, MONNAMES)
( 6, 1, RECONNECT_SEQ) // 3.10 req
( 7, 1, DIRLAYOUTHASH) // 2.6.38
(15, 1, MONENC)
(16, 3, SERVER_OCTOPUS) | (16, 3, OSD_REPOP_MLCOD)
(20, 3, SERVER_PACIFIC)
(21, 2, SERVER_LUMINOUS) // 4.13 | (21, 2, RESEND_ON_SPLIT) | (21, 2, RADOS_BACKOFF) | (21, 2, OSDMAP_PG_UPMAP) | (21, 2, CRUSH_CHOOSE_ARGS)
(22, 2, OSD_FIXED_COLLECTION_LIST)
(23, 1, MSG_AUTH) // 3.19 req (unless nocephx_require_signatures)
(24, 2, RECOVERY_RESERVATION_2)
(26, 1, CREATEPOOLID)
(27, 1, REPLY_CREATE_INODE) // 3.9
(28, 2, SERVER_MIMIC)
RETIRED(33, 1, MON_SCRUB, JEWEL, LUMINOUS)
RETIRED(34, 1, OSD_PACKED_RECOVERY, JEWEL, LUMINOUS)
(36, 1, CRUSH_V2) // 3.14
RETIRED(38, 1, OSD_ERASURE_CODES, MIMIC, OCTOPUS)
(40, 1, MDS_INLINE_DATA) // 3.19
(42, 1, MSGR_KEEPALIVE2) // 4.3 (for consistency)
RETIRED(45, 1, OSD_SET_ALLOC_HINT, JEWEL, LUMINOUS)
RETIRED(50, 1, MON_METADATA, MIMIC, OCTOPUS)
RETIRED(52, 1, OSD_PROXY_WRITE_FEATURES, MIMIC, OCTOPUS)
RETIRED(54, 1, OSD_HITSET_GMT, MIMIC, OCTOPUS)
(56, 1, NEW_OSDOP_ENCODING) // 4.13 (for pg_pool_t >= v25)
(57, 1, MON_STATEFUL_SUB) // 4.13 | (57, 1, SERVER_JEWEL)
(59, 1, FS_BTIME) | (59, 1, FS_CHANGE_ATTR) | (59, 1, MSG_ADDR2)
(60, 1, OSD_RECOVERY_DELETES) // *do not share this bit*
(62, 1, RESERVED) // do not use; used as a sentinel
```