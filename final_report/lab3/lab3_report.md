# Lab 3: Containerization & Cluster Orchestration

## 1. Simulated Execution & Screenshots

### Inspecting Namespaces and cgroups Inside a Container
**Command:** `docker run -it --rm ubuntu bash` (to enter container)
**Command:** `ps -ef`
```text
root@container:/# ps -ef
UID          PID    PPID  C STIME TTY          TIME CMD
root           1       0  0 10:00 pts/0    00:00:00 bash
root          10       1  0 10:01 pts/0    00:00:00 ps -ef
```
*Observation:* The PID namespace isolates the process tree. `bash` runs as PID 1 inside the container, even though it has a different, much higher PID on the host system.

**Command:** `cat /proc/1/cgroup`
```text
root@container:/# cat /proc/1/cgroup
12:hugetlb:/docker/a1b2c3d4e5f6...
11:perf_event:/docker/a1b2c3d4e5f6...
10:cpuset:/docker/a1b2c3d4e5f6...
9:freezer:/docker/a1b2c3d4e5f6...
8:memory:/docker/a1b2c3d4e5f6...
7:pids:/docker/a1b2c3d4e5f6...
6:blkio:/docker/a1b2c3d4e5f6...
5:net_cls,net_prio:/docker/a1b2c3d4e5f6...
4:devices:/docker/a1b2c3d4e5f6...
3:cpu,cpuacct:/docker/a1b2c3d4e5f6...
2:net_mac:/
1:name=systemd:/docker/a1b2c3d4e5f6...
0::/docker/a1b2c3d4e5f6...
```
*Observation:* The output shows the control groups (cgroups) assigned to this container by Docker, managing memory, cpu, block I/O, etc., restricting the resources this container can consume.

### Deploying the App and Demonstrating Self-Healing
**Command:** `kubectl apply -f deployment.yaml`
```text
deployment.apps/lab3-web created
```

**Command:** `kubectl get pods`
```text
NAME                        READY   STATUS    RESTARTS   AGE
lab3-web-74d4b998f4-a1b2c   1/1     Running   0          10s
lab3-web-74d4b998f4-d3e4f   1/1     Running   0          10s
lab3-web-74d4b998f4-g5h6i   1/1     Running   0          10s
```

**Command:** `kubectl delete pod lab3-web-74d4b998f4-a1b2c`
```text
pod "lab3-web-74d4b998f4-a1b2c" deleted
```

**Command:** `kubectl get pods -w`
```text
NAME                        READY   STATUS        RESTARTS   AGE
lab3-web-74d4b998f4-a1b2c   1/1     Terminating   0          45s
lab3-web-74d4b998f4-d3e4f   1/1     Running       0          45s
lab3-web-74d4b998f4-g5h6i   1/1     Running       0          45s
lab3-web-74d4b998f4-z9y8x   0/1     Pending       0          1s
lab3-web-74d4b998f4-z9y8x   0/1     ContainerCreating   0    2s
lab3-web-74d4b998f4-z9y8x   1/1     Running       0          5s
```
*Observation:* Kubernetes immediately noticed that the current state (2 pods) did not match the desired state (3 replicas). It automatically scheduled and created a new pod (`z9y8x`) to replace the deleted one.

---

## 2. Docker Comparison Table

| Feature | `Dockerfile.basic` | `Dockerfile.multistage` |
| :--- | :--- | :--- |
| **Image Size** | Large (Includes all build tools, caches, and intermediate layers used to install dependencies). | Small (Only contains the compiled binaries/wheels and the application code). |
| **Security** | Lower (Includes build tools like `gcc` or `make` which could be exploited if the container is compromised). | Higher (Build tools are discarded in the first stage; production image surface area is minimized). |
| **Build Time** | Faster for initial single builds, but caches are less optimized. | Slightly longer initially due to multiple stages, but highly cacheable and optimized for CI/CD pipelines. |
| **Best For** | Local development and quick prototyping. | Production environments where image size, security, and deployment speed are critical. |

---

## 3. Reflection Questions

**1. Why do namespaces alone not guarantee fair resource use?**
Namespaces provide *isolation* (e.g., hiding processes, network interfaces, and mount points from other containers). However, they do not enforce *limits*. Without limits, a single container isolated in its own namespace could still consume 100% of the host's CPU or RAM, starving other containers.

**2. How do cgroups improve cluster stability?**
cgroups (control groups) enforce resource *limits* (CPU, Memory, Block I/O). By limiting how much RAM or CPU a container can use, cgroups prevent a single rogue or buggy container from crashing the entire host system (e.g., via Out-Of-Memory errors), thereby ensuring stability for all other containers on that host.

**3. Why is Docker image layering important for large-scale orchestration?**
Layering allows images to share common underlying layers (like the base OS or common dependencies). In a large cluster, if 100 pods use images based on `python:3.12-slim`, the node only downloads and stores that base layer once. This drastically reduces network bandwidth during image pulls, speeds up container startup times, and saves significant disk space on the worker nodes.

**4. What does Kubernetes mean by desired state?**
The "desired state" is the declarative configuration provided by the user (e.g., "I want exactly 3 replicas of the `lab3-web` pod running at all times"). Kubernetes continuously runs a control loop to observe the "current state" and makes changes to reconcile it with the "desired state".

**5. How is self-healing different from traditional manual operations?**
In traditional operations, a human operator or a custom script must detect a failure, manually intervene, and restart a server or service. Kubernetes self-healing is continuous and autonomous; the control plane automatically detects pod failures, node crashes, or unresponsiveness and instantly reschedules or restarts workloads without any human intervention.

**6. Why are readiness and liveness probes not interchangeable?**
- **Liveness Probes** determine if a container is *running properly*. If it fails, Kubernetes will kill and restart the container (used to break out of deadlocks).
- **Readiness Probes** determine if a container is *ready to accept traffic*. If it fails, Kubernetes leaves the container running but removes it from the Service load balancer so it doesn't receive user requests (used while an app is still booting up or temporarily overloaded).

**7. What is one limitation of observing scheduling in a single-node kind cluster?**
In a single-node cluster, there is only one place for pods to go. You cannot observe or test complex scheduling behaviors such as Node Affinity, Pod Anti-Affinity (ensuring two pods don't land on the same node), or how Kubernetes handles a full Node failure by migrating pods to a healthy Node.
