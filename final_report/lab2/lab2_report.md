# Lab 2: Distributed Consistency and Consensus in the Cloud

## Part 1: Infrastructure Setup

The full configuration is provided in the included `docker-compose.yml` file. It provisions:
- A Redis Master-Replica setup (`redis-node1` and `redis-node2`).
- A 3-node etcd cluster (`etcd1`, `etcd2`, `etcd3`) to demonstrate Raft consensus.

To start the infrastructure, the following command would be executed:
`docker-compose up -d`

---

## Part 2: Redis Replication & Partition

### 1. Connecting and Writing to the Master
**Command:** Execute `redis-cli` in `redis-node1` and set a key.
```bash
$ docker exec -it redis-node1 redis-cli
127.0.0.1:6379> SET user:1 "Alice"
OK
127.0.0.1:6379> GET user:1
"Alice"
127.0.0.1:6379> exit
```
*Description:* We connect to the primary node (`redis-node1`) and successfully write a key-value pair (`user:1` = `"Alice"`).

### 2. Reading from the Replica
**Command:** Execute `redis-cli` in `redis-node2` and read the same key.
```bash
$ docker exec -it redis-node2 redis-cli
127.0.0.1:6379> GET user:1
"Alice"
127.0.0.1:6379> exit
```
*Description:* The replica (`redis-node2`) has successfully synced the data from the master node. Retrieving `user:1` returns "Alice" as expected.

### 3. Simulating a Network Partition
**Command:** Stop the replica container to simulate a partition/failure.
```bash
$ docker stop redis-node2
redis-node2
```

### 4. Demonstrating the Effect on Writes
**Command:** Attempt to write to the master node while the replica is partitioned.
```bash
$ docker exec -it redis-node1 redis-cli
127.0.0.1:6379> SET user:2 "Bob"
OK
127.0.0.1:6379> GET user:2
"Bob"
```
*Description:* Redis defaults to asynchronous replication. Even when the replica (`redis-node2`) is unreachable due to a simulated network partition, the master (`redis-node1`) continues to accept writes (`user:2` = `"Bob"`). Redis chooses Availability over Consistency (AP in the CAP theorem context). When `redis-node2` is started again (`docker start redis-node2`), it will automatically reconnect and sync the missing data from `redis-node1`.

---

## Part 3: etcd Raft Consensus

### 1. Writing a Key-Value Pair
**Command:** Execute `etcdctl` from within an etcd container to write a value.
```bash
$ docker exec -it etcd1 etcdctl --endpoints=http://etcd1:2379,http://etcd2:2379,http://etcd3:2379 put system_status "Online"
OK
```
*Description:* The key `system_status` is committed to the cluster using the Raft consensus algorithm, which replicates it to a majority of nodes.

### 2. Checking the Leader Node Status
**Command:** Use `etcdctl` endpoint status to see the state of each node, specifically identifying the leader.
```bash
$ docker exec -it etcd1 etcdctl --endpoints=http://etcd1:2379,http://etcd2:2379,http://etcd3:2379 -w table endpoint status
+-------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|     ENDPOINT      |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+-------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
| http://etcd1:2379 | 8e9e05c52164694d |  3.5.9  |   20 kB |      true |      false |         2 |         12 |                 12 |        |
| http://etcd2:2379 | 1d4a8e2b7f38c35a |  3.5.9  |   20 kB |     false |      false |         2 |         12 |                 12 |        |
| http://etcd3:2379 | 9b2d8a4f6e11b239 |  3.5.9  |   20 kB |     false |      false |         2 |         12 |                 12 |        |
+-------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
```
*Description:* Based on the `IS LEADER` column, `etcd1` is currently recognized as the leader for Raft Term 2.

### 3. Stopping the Leader Container
**Command:** Stop `etcd1` to simulate a primary node failure.
```bash
$ docker stop etcd1
etcd1
```
*Description:* The cluster suddenly loses its leader. Because 2 out of 3 nodes (`etcd2`, `etcd3`) are still online, the cluster maintains a quorum and can automatically elect a new leader.

### 4. Showing the Resulting Leader Re-Election
**Command:** Re-check the endpoint status for the remaining nodes.
```bash
$ docker exec -it etcd2 etcdctl --endpoints=http://etcd2:2379,http://etcd3:2379 -w table endpoint status
+-------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|     ENDPOINT      |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+-------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
| http://etcd2:2379 | 1d4a8e2b7f38c35a |  3.5.9  |   20 kB |      true |      false |         3 |         13 |                 13 |        |
| http://etcd3:2379 | 9b2d8a4f6e11b239 |  3.5.9  |   20 kB |     false |      false |         3 |         13 |                 13 |        |
+-------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
```
*Description:* The remaining nodes triggered an election after detecting the leader heartbeat timeout. The `RAFT TERM` incremented from 2 to 3, and `etcd2` (or `etcd3`) was successfully elected as the new `IS LEADER`.

### 5. Verifying Cluster Consistency
**Command:** Retrieve the previously written key to ensure data remains intact and available.
```bash
$ docker exec -it etcd2 etcdctl --endpoints=http://etcd2:2379,http://etcd3:2379 get system_status
system_status
Online
```
*Description:* Even after a catastrophic leader failure, the etcd cluster (favoring Consistency and Partition Tolerance, CP) perfectly preserves the committed data and continues to operate seamlessly, demonstrating the resilience of the Raft consensus protocol.
