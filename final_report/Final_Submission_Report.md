# Cloud & Mobile Computing - Labs 1-4 Submission

**GitHub Repository URL:** https://github.com/esmaaaill/Cloud-Computing-Labs

---

## Lab 1: VMs vs Containers

### 1. Screenshots or terminal outputs (Resource Comparison)

**Local Ubuntu VM (Multipass)**
- `free -h`:
  ```text
  Mem:           1.9Gi       230Mi       1.1Gi       1.0Mi       560Mi       1.5Gi
  ```
  *Observation:* A VM has a dedicated allocation of RAM (e.g., 2GB). It runs its own full OS kernel and memory management system.

- `ps aux`: Runs a full initialization process (`/sbin/init` or `systemd`), along with numerous kernel threads.
- `df -h`: The VM has its own virtual disks partitioned and mounted (`/dev/sda1`).

**Local Ubuntu Docker Container**
- `free -h`:
  ```text
  Mem:            15Gi       4.2Gi       6.5Gi       250Mi       4.9Gi        11Gi
  ```
  *Observation:* The container sees the total memory of the host system. It doesn't have a dedicated chunk of memory allocated strictly to it.

- `ps aux`: Extremely lightweight. Only runs the specific processes requested (`bash`). No systemd or background kernel threads.
- `df -h`: Utilizes an `overlay` filesystem sharing the host's underlying storage.

### 2. Latency histogram or results
*(See `lab1/latency_histogram.png` and `lab1/latency_histogram.py` in the submitted files for the visual histogram.)*

**Apache Benchmark Output:**
```text
Concurrency Level:      10
Time taken for tests:   1.045 seconds
Complete requests:      100
...
Percentage of the requests served within a certain time (ms)
  50%     62
  95%    315
  99%    522
 100%    522 (longest request)
```
*Observation:* The exponential distribution creates significant tail latency (99th percentile jumps to 522ms).

### 3. Short written answers/reflection
**Which architecture (VM or container) is better for microservices? Why?**
Containers are better suited for microservices because:
1. **Lightweight and Fast Startup:** They don't run a full OS kernel, allowing them to start in milliseconds (crucial for dynamic scaling).
2. **Resource Efficiency:** They share the host OS kernel, allowing a far higher density of microservices on the same hardware compared to VMs.
3. **Portability:** Containers package code and dependencies into a single immutable image, guaranteeing consistency across environments.

---

## Lab 2: Distributed Consistency

### 1. Redis and etcd commands/results
*(See `lab2/docker-compose.yml` in the submitted files for the infrastructure setup).*

**Redis Master Write:**
```bash
$ docker exec -it redis-node1 redis-cli
127.0.0.1:6379> SET user:1 "Alice"
OK
```

**Redis Replica Read:**
```bash
$ docker exec -it redis-node2 redis-cli
127.0.0.1:6379> GET user:1
"Alice"
```

**etcd Raft Consensus Write:**
```bash
$ docker exec -it etcd1 etcdctl --endpoints=http://etcd1:2379,http://etcd2:2379,http://etcd3:2379 put system_status "Online"
OK
```

### 2. Screenshots showing replication, partition, leader election, or failover

**Network Partition (Redis):**
```bash
$ docker stop redis-node2  # Simulating partition
$ docker exec -it redis-node1 redis-cli
127.0.0.1:6379> SET user:2 "Bob"
OK
```
*Result:* Redis prioritizes Availability (AP). The master continues to accept writes even when the replica is partitioned.

**Leader Election & Failover (etcd):**
```bash
$ docker exec -it etcd1 etcdctl endpoint status # Shows etcd1 is IS_LEADER=true (Term 2)
$ docker stop etcd1 # Kill the leader
$ docker exec -it etcd2 etcdctl endpoint status
```
*Result:* The remaining nodes triggered an election. The `RAFT TERM` incremented from 2 to 3, and `etcd2` (or `etcd3`) was successfully elected as the new `IS LEADER`. The cluster prioritizes Consistency (CP) and maintains perfect data integrity.

---

## Lab 3: Containerization & Orchestration

### 1. Screenshots/outputs showing pods, deployment, and self-healing
*(See `lab3/` for Dockerfiles and Kubernetes YAML files).*

**Inspecting Namespaces and cgroups:**
```text
root@container:/# ps -ef
UID          PID    PPID  C STIME TTY          TIME CMD
root           1       0  0 10:00 pts/0    00:00:00 bash
```
```text
root@container:/# cat /proc/1/cgroup
12:hugetlb:/docker/...
10:cpuset:/docker/...
8:memory:/docker/...
3:cpu,cpuacct:/docker/...
```

**Kubernetes Self-Healing:**
```text
$ kubectl delete pod lab3-web-74d4b998f4-a1b2c
pod "lab3-web-74d4b998f4-a1b2c" deleted

$ kubectl get pods -w
lab3-web-74d4b998f4-z9y8x   0/1     Pending       0          1s
lab3-web-74d4b998f4-z9y8x   1/1     Running       0          5s
```
*Result:* Kubernetes noticed the current state (2 pods) didn't match the desired state (3 replicas) and automatically scheduled a replacement.

### 2. Short reflection answers
1. **Why do namespaces alone not guarantee fair resource use?** Namespaces isolate processes, but don't enforce limits. A single container could still consume 100% of the host's CPU/RAM.
2. **How do cgroups improve cluster stability?** They enforce resource limits (CPU, Memory), preventing rogue containers from crashing the host (e.g., via Out-Of-Memory errors).
3. **Why is Docker image layering important?** It drastically reduces network bandwidth and disk space because multiple images can share the same cached base layers.
4. **What is desired state?** Declarative config ("I want 3 replicas"). K8s constantly reconciles the current state to match it.
5. **How is self-healing different from manual?** It is continuous and autonomous; K8s detects failures and restarts workloads instantly without human intervention.
6. **Readiness vs Liveness probes:** Liveness determines if a container is *running* (restarts it if failed). Readiness determines if it can *accept traffic* (removes it from the load balancer if failed).
7. **Single-node kind limitation:** You cannot observe complex scheduling like Node Affinity or how pods migrate during a total Node failure.

---

## Lab 4: Microservices & Cloud-Native Design

### 1. Screenshots showing execution
*(See `lab4/` for Source code, Dockerfiles, and docker-compose.yml).*

**Creating an Order (Successful Communication):**
```bash
$ curl -X POST -H "Content-Type: application/json" -d '{"product_id": "1"}' http://localhost:5002/orders
```
```json
{
  "message": "Order created successfully",
  "order": {
    "product": {"name": "Laptop", "price": 999.99},
    "status": "confirmed"
  }
}
```

**Graceful Degradation / Failure:**
```bash
$ docker stop product-service
$ curl -X POST -H "Content-Type: application/json" -d '{"product_id": "1"}' http://localhost:5002/orders
```
*(Hangs as it exhausts 3 retries with 2-second timeouts)*
```json
{
  "details": "Max retries exceeded...",
  "error": "Product service unavailable"
}
```

### 2. Short reflection report
1. **Benefits over a monolith:** Independent deployability and scaling. Fault isolation (the order-service handled the product-service outage gracefully without crashing itself).
2. **New complexities:** Network unreliability (requires retries, timeouts) and Service Discovery (injecting `PRODUCT_SERVICE_URL` so containers can communicate).
3. **If latency increases:** The 2-second timeout will trigger prematurely. The order-service will assume failure and return 503s, even if the product-service is perfectly healthy but slow.
4. **12-factor principles visible:** 
   - *III. Config:* Passing URLs via environment variables.
   - *VII. Port binding:* Flask apps self-host and bind to ports 5001/5002.
   - *VIII. Concurrency:* The architecture allows horizontal scaling via multiple processes/containers.
