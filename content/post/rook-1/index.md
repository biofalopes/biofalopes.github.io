+++
title = "Using Rook to leverage Ceph storage on a Kubernetes cluster"
description = "Using Rook to leverage Ceph storage on a Kubernetes cluster with unused storage devices"
date = "2021-07-17"
draft = false
toc = false
categories = ["ceph", "kubernetes"]
tags = ["ceph", "kubernetes"]
image = "rook.png"
+++

I recently got 10 bare-metal servers to play with, they used to be part of our first Ceph cluster and got replaced with more powerful hardware. So i built two k8s clusters and decided to give Rook a try.
<!--more---> 
As the cluster grew bigger, we purchased not only more servers but with different configuration. But those Dell R530 servers still have pretty decent power to run many internal demands we have, so i built a Ceph cluster with four of them using CentOS 8, Ceph Octopus and deployed everything in containers. But i want to talk about what i did with the remaining six servers, that became two kubernetes clusters - one with Flatcar and the other with Centos, to replicate some production scenarios we have. Since the servers have 8 2TB HDD each and we use just one for the OS, that would be a perfect scenario to experiment with Rook. I tinkered with it previously with some labs but now i could really test its usability.

Getting Rook to run is pretty straightforward, it might not even be necessary to have great knowledge about ceph for the initial setup. However it would be mandatory to know about Ceph administration for a production environment. There are many administrative tasks that gets taken care of by Rook, but after working with Ceph for the past 3 years i can assure you that there will be many situations where the sysadmin will have to step up.

I used the quickstart guide as a reference, it can be found on the Rook GitHub page: https://rook.github.io/docs/rook/v1.6/ceph-quickstart.html.

The only parameter i changed from the defaults was the ROOK_ENABLE_DISCOVERY_DAEMON, since i wanted it to automatically detect and provision the OSDs on every empty device. It's important to erase the disks prior to the deployment, because it will skip any device with partitions. For that you can use `wipefs` or even `dd`. Be aware that if the device has LVM partitions and you want to avoid a reboot you might want to delete the LVs and VGs first. If you wipe the device the kernel might not release the mapped lvm volumes and you will not be able to delete after that. Needless to say that i made that mistake a few times before learning the lesson.

Commands i used:
```
git clone --single-branch --branch master https://github.com/rook/rook.git
git checkout release-1.6
cd rook/cluster/examples/kubernetes/ceph
sed -i s/"ROOK_ENABLE_DISCOVERY_DAEMON: \"false\""/"ROOK_ENABLE_DISCOVERY_DAEMON: \"true\""/ operator.yaml
kubectl create -f crds.yaml -f common.yaml -f operator.yaml
kubectl create -f cluster.yaml
```

Checking if the pods were created:
```
$ kubectl -n rook-ceph get pod
NAME                                              READY   STATUS      RESTARTS   AGE
csi-cephfsplugin-7tkgk                            3/3     Running     25         95d
csi-cephfsplugin-cv2kq                            3/3     Running     6          95d
csi-cephfsplugin-provisioner-bc5cff84-8h5b4       6/6     Running     19         95d
csi-cephfsplugin-provisioner-bc5cff84-cb477       6/6     Running     6          95d
csi-cephfsplugin-qvqjc                            3/3     Running     3          95d
csi-rbdplugin-2rqwk                               3/3     Running     25         95d
csi-rbdplugin-g5tkj                               3/3     Running     3          95d
csi-rbdplugin-provisioner-97957587f-gvn6r         6/6     Running     0          22d
csi-rbdplugin-provisioner-97957587f-lflc7         6/6     Running     8          95d
csi-rbdplugin-vcsdj                               3/3     Running     6          95d
rook-ceph-crashcollector-node1-7fcbcd7dc6-6fbq6   1/1     Running     2          73d
rook-ceph-crashcollector-node2-7f699c88c-78gvw    1/1     Running     0          22d
rook-ceph-crashcollector-node3-77777995d8-dtsrh   1/1     Running     1          95d
rook-ceph-mgr-a-8486cbdf64-dsdn2                  1/1     Running     0          24d
rook-ceph-mon-a-7758d4d54c-crq4s                  1/1     Running     2          95d
rook-ceph-mon-d-77db79f9b9-fcd5r                  1/1     Running     0          41d
rook-ceph-mon-e-7d44dcff6b-zjpfl                  1/1     Running     0          22d
rook-ceph-operator-66f7668857-sr8bw               1/1     Running     2          95d
rook-ceph-osd-0-57b7d8b47b-k5ps8                  1/1     Running     2          95d
rook-ceph-osd-1-548c7bc54d-zsp8r                  1/1     Running     1          95d
rook-ceph-osd-10-7875d885d8-h2wdt                 1/1     Running     0          22d
rook-ceph-osd-11-5585fb7856-gxjfx                 1/1     Running     2          95d
rook-ceph-osd-12-fd5bcb8f8-z9v4c                  1/1     Running     1          95d
rook-ceph-osd-13-784c797d46-qmxj4                 1/1     Running     0          22d
rook-ceph-osd-14-6b689bfb4-sfffq                  1/1     Running     2          95d
rook-ceph-osd-15-64984bf7db-h99q2                 1/1     Running     1          95d
rook-ceph-osd-16-6f66f68868-ft8d8                 1/1     Running     0          22d
rook-ceph-osd-17-66fcdfc8c8-rg76t                 1/1     Running     2          95d
rook-ceph-osd-18-85f9d5567b-6jjph                 1/1     Running     1          95d
rook-ceph-osd-19-969b58fb-ztzxx                   1/1     Running     0          22d
rook-ceph-osd-2-ffc69957b-846mj                   1/1     Running     2          95d
rook-ceph-osd-20-5c86c5d556-26kkp                 1/1     Running     0          22d
rook-ceph-osd-3-79cb4b8f78-wxczm                  1/1     Running     1          95d
rook-ceph-osd-4-9587d6994-z94l2                   1/1     Running     0          22d
rook-ceph-osd-5-74cb556886-sqp6g                  1/1     Running     2          95d
rook-ceph-osd-6-5fb96bcb-2lgqr                    1/1     Running     1          95d
rook-ceph-osd-7-85f8659c9d-7z5tn                  1/1     Running     0          22d
rook-ceph-osd-8-6765676bfb-kjxr5                  1/1     Running     2          95d
rook-ceph-osd-9-67b4f98cdb-h9bd8                  1/1     Running     1          95d
rook-ceph-osd-prepare-node1-6x7dr                 0/1     Completed   0          133m
rook-ceph-osd-prepare-node2-z6jl8                 0/1     Completed   0          133m
rook-ceph-osd-prepare-node3-rvhth                 0/1     Completed   0          133m
rook-ceph-tools-6f58686b5d-znnsg                  1/1     Running     0          24d
rook-discover-2684s                               1/1     Running     7          95d
rook-discover-2nlkj                               1/1     Running     1          95d
rook-discover-4rhxm                               1/1     Running     2          95d
```

The output is long but i wanted to show that Rook actually created a OSD por for every device in each node, and i configured kubernetes to allow that on the master node either.

We can see that we now have a bunch of new resource definitions, enabling us to interact with Ceph in a declarative way, instead of recurring to the CLI to manage users, filesystems, pools and many other resources:

```
$ kubectl get crd | grep 'rook\|objectbucket'
cephblockpools.ceph.rook.io                           2021-04-01T19:30:54Z
cephclients.ceph.rook.io                              2021-04-01T19:30:53Z
cephclusters.ceph.rook.io                             2021-04-01T19:30:53Z
cephfilesystems.ceph.rook.io                          2021-04-01T19:30:53Z
cephnfses.ceph.rook.io                                2021-04-01T19:30:53Z
cephobjectrealms.ceph.rook.io                         2021-04-01T19:30:54Z
cephobjectstores.ceph.rook.io                         2021-04-01T19:30:53Z
cephobjectstoreusers.ceph.rook.io                     2021-04-01T19:30:54Z
cephobjectzonegroups.ceph.rook.io                     2021-04-01T19:30:54Z
cephobjectzones.ceph.rook.io                          2021-04-01T19:30:54Z
cephrbdmirrors.ceph.rook.io                           2021-04-01T19:30:53Z
objectbucketclaims.objectbucket.io                    2021-04-01T19:30:54Z
objectbuckets.objectbucket.io                         2021-04-01T19:30:54Z
volumes.rook.io                                       2021-04-01T19:30:54Z
```

From that point we can access the Ceph CLI by interacting with the `rook-ceph-tools` pod:

```
$ kubectl exec -it -n rook-ceph rook-ceph-tools-6f58686b5d-znnsg -- ceph status
cluster:
  id:     72e9c4a9-4315-45e0-ad43-cd79d22fb2be
  health: HEALTH_OK

services:
  mon: 3 daemons, quorum a,d,e (age 7d)
  mgr: a(active, since 3w)
  osd: 21 osds: 21 up (since 3w), 21 in (since 3w)
  rgw: 1 daemon active (my.store.a)

task status:

data:
  pools:   30 pools, 401 pgs
  objects: 2.12k objects, 2.4 GiB
  usage:   29 GiB used, 38 TiB / 38 TiB avail
  pgs:     401 active+clean

io:
  client:   7.0 KiB/s rd, 72 KiB/s wr, 6 op/s rd, 16 op/s wr
```

Now we have two new StorageClasses to work with:

```
$ kubectl get storageclasses
NAME               PROVISIONER                     RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
rook-ceph-block    rook-ceph.rbd.csi.ceph.com      Delete          Immediate           false                  64d
rook-ceph-bucket   rook-ceph.ceph.rook.io/bucket   Delete          Immediate           false                  84d
```

And then we provisioned some volumes to a few applications running on the cluster:

```
$ kubectl get pv -A
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                                     STORAGECLASS      REASON   AGE
pvc-1c9151ae-3e9e-49ae-adbf-f365de4eb718   8Gi        RWO            Delete           Bound    cluster-spd/data-etcd-1                   rook-ceph-block            18d
pvc-39c5a513-1c50-48a9-9e4d-354ff84ea8b4   8Gi        RWO            Delete           Bound    cluster-spb/data-etcd-0                   rook-ceph-block            24d
pvc-53f2816a-e4c2-434d-8600-20206d3f6f75   8Gi        RWO            Delete           Bound    cluster-spc/data-etcd-0                   rook-ceph-block            18d
pvc-553c1a1b-0131-44a9-8a67-293dea40c161   5Gi        RWO            Delete           Bound    gitlab/redis-data-gitlab-redis-master-0   rook-ceph-block            56d
pvc-6c38a9b7-8e23-4478-a431-34fd4f9ec158   8Gi        RWO            Delete           Bound    cluster-spd/data-etcd-2                   rook-ceph-block            18d
pvc-76bfab8e-6ae6-4b11-8223-ea9e97bbccf4   8Gi        RWO            Delete           Bound    cluster-spc/data-etcd-2                   rook-ceph-block            18d
pvc-836c1ff1-c92d-467c-b45b-b970824e2b04   8Gi        RWO            Delete           Bound    cluster-spc/data-etcd-1                   rook-ceph-block            18d
pvc-87e7bd8e-250e-4bd4-8268-3fb49597d0ab   10Gi       RWO            Delete           Bound    gitlab/gitlab-minio                       rook-ceph-block            39d
pvc-bac3dc77-73ae-4800-821a-04faa15e627d   8Gi        RWO            Delete           Bound    cluster-spb/data-etcd-1                   rook-ceph-block            24d
pvc-ca087b82-038b-418a-a187-8e28617fbfae   8Gi        RWO            Delete           Bound    cluster-spd/data-etcd-0                   rook-ceph-block            18d
pvc-d255ca76-b62f-413b-82b8-184ff3cb0026   8Gi        RWO            Delete           Bound    cluster-spb/data-etcd-2                   rook-ceph-block            24d
pvc-d331d766-72d7-46c4-9cba-c0e8fea7a2b8   50Gi       RWO            Delete           Bound    gitlab/repo-data-gitlab-gitaly-0          rook-ceph-block            56d
pvc-e76d375b-03b5-4bc0-8725-bc406cb7ee94   8Gi        RWO            Delete           Bound    gitlab/data-gitlab-postgresql-0           rook-ceph-block            56d
```

This is how the pvc manifest looks like:

```
$ kubectl get pvc -n gitlab gitlab-minio -o yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: gitlab-minio
  namespace: gitlab
  labels:
    app: minio
spec:
  storageClassName: rook-ceph-block
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

We can also provision Buckets using S3 via Rook. We used this to provide a backend for a Hashicorp Vault we have on the same environment:

First we have to create the StorageClass:
```
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
   name: rook-ceph-bucket
provisioner: rook-ceph.ceph.rook.io/bucket
reclaimPolicy: Delete
parameters:
  objectStoreName: my-store
  objectStoreNamespace: rook-ceph
  region: us-east-1
```

Then we create a ObjectBucketClaim, which is a new resource type defined by the Rook CRD:
```
apiVersion: objectbucket.io/v1alpha1
kind: ObjectBucketClaim
metadata:
  name: ceph-bucket
  namespace: vault
spec:
  generateBucketName: ceph-bucket
  storageClassName: rook-ceph-bucket
```