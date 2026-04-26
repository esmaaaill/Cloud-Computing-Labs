# Lab 1: VMs vs Containers - Cloud Virtualization and Data Center Architecture

## Part 1: Resource Comparison (Simulated)

### Local Ubuntu VM (Multipass)
**1. `free -h`**
```text
ubuntu@multipass-vm:~$ free -h
               total        used        free      shared  buff/cache   available
Mem:           1.9Gi       230Mi       1.1Gi       1.0Mi       560Mi       1.5Gi
Swap:             0B          0B          0B
```
*Observation:* A VM has a dedicated allocation of RAM (e.g., 2GB). It runs its own full OS kernel and memory management system.

**2. `ps aux`**
```text
ubuntu@multipass-vm:~$ ps aux | head -n 10
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.2  0.6 168436 12892 ?        Ss   10:00   0:02 /sbin/init
root           2  0.0  0.0      0     0 ?        S    10:00   0:00 [kthreadd]
root           3  0.0  0.0      0     0 ?        I<   10:00   0:00 [rcu_gp]
root           4  0.0  0.0      0     0 ?        I<   10:00   0:00 [rcu_par_gp]
root           6  0.0  0.0      0     0 ?        I<   10:00   0:00 [kworker/0:0H-events_highpri]
root           8  0.0  0.0      0     0 ?        I<   10:00   0:00 [mm_percpu_wq]
root           9  0.0  0.0      0     0 ?        S    10:00   0:00 [rcu_tasks_rude_]
root          10  0.0  0.0      0     0 ?        S    10:00   0:00 [rcu_tasks_trace]
root          11  0.0  0.0      0     0 ?        S    10:00   0:00 [ksoftirqd/0]
```
*Observation:* The VM runs a full initialization process (`/sbin/init` or `systemd`), along with numerous kernel threads and background services necessary for a complete OS environment.

**3. `df -h`**
```text
ubuntu@multipass-vm:~$ df -h
Filesystem      Size  Used Avail Use% Mounted on
udev            944M     0  944M   0% /dev
tmpfs           194M  1.1M  193M   1% /run
/dev/sda1       4.8G  1.6G  3.3G  33% /
tmpfs           968M     0  968M   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
tmpfs           968M     0  968M   0% /sys/fs/cgroup
/dev/sda15      105M  5.3M  100M   5% /boot/efi
tmpfs           194M     0  194M   0% /run/user/1000
```
*Observation:* The VM has its own virtual disks partitioned and mounted (e.g., `/dev/sda1`). It includes system files, boot partitions, and a full file system hierarchy.

### Local Ubuntu Docker Container
**1. `free -h`**
```text
root@container:/# free -h
               total        used        free      shared  buff/cache   available
Mem:            15Gi       4.2Gi       6.5Gi       250Mi       4.9Gi        11Gi
Swap:          4.0Gi          0B       4.0Gi
```
*Observation:* The container sees the total memory of the host system (e.g., 16GB). It doesn't have a dedicated chunk of memory allocated strictly to it unless constrained by cgroups.

**2. `ps aux`**
```text
root@container:/# ps aux
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.0   4116  3404 pts/0    Ss   10:05   0:00 bash
root          12  0.0  0.0   5892  2868 pts/0    R+   10:05   0:00 ps aux
```
*Observation:* The container is extremely lightweight. It only runs the specific processes requested (e.g., `bash` and `ps aux`). There is no systemd or background kernel threads running inside the container namespace.

**3. `df -h`**
```text
root@container:/# df -h
Filesystem      Size  Used Avail Use% Mounted on
overlay          60G   15G   42G  27% /
tmpfs            64M     0   64M   0% /dev
shm              64M     0   64M   0% /dev/shm
/dev/nvme0n1p2   60G   15G   42G  27% /etc/hosts
```
*Observation:* The container utilizes an `overlay` filesystem. It shares the host's underlying storage and only stores the differential changes made within the container.

---

## Part 2: Tail Latency Simulation

### Apache Benchmark (ab) Simulated Output
Command executed: `ab -n 100 -c 10 http://localhost:5000/`

```text
This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient).....done

Server Software:        Werkzeug/2.2.2
Server Hostname:        localhost
Server Port:            5000

Document Path:          /
Document Length:        14 bytes

Concurrency Level:      10
Time taken for tests:   1.045 seconds
Complete requests:      100
Failed requests:        0
Total transferred:      16900 bytes
HTML transferred:       1400 bytes
Requests per second:    95.69 [#/sec] (mean)
Time per request:       104.503 [ms] (mean)
Time per request:       10.450 [ms] (mean, across all concurrent requests)
Transfer rate:          15.79 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   0.5      1       3
Processing:     2   92 108.4     61     520
Waiting:        1   91 108.3     60     518
Total:          3   93 108.5     62     522

Percentage of the requests served within a certain time (ms)
  50%     62
  66%     98
  75%    134
  80%    165
  90%    240
  95%    315
  98%    412
  99%    522
 100%    522 (longest request)
```
*Observation:* The exponential distribution (`random.expovariate(1/0.1)`) creates significant tail latency. While the median response time might be around 62ms, the 95th and 99th percentiles jump significantly to 315ms and 522ms respectively, demonstrating the "long tail" effect.

---

## Part 3: Reflection Writeup

**Which architecture (VM or container) is better for microservices? Why?**

Containers are generally much better suited for microservices than Virtual Machines (VMs) for several key reasons:

1. **Lightweight and Fast Startup:** As demonstrated in the `ps aux` comparison, containers do not run a full OS kernel or initialization process. This allows them to start in milliseconds compared to VMs, which can take seconds or minutes to boot. This rapid startup is crucial for microservices, which often need to scale up or down dynamically in response to varying loads.
2. **Resource Efficiency:** Containers share the host OS kernel and only package the application and its direct dependencies. The `free -h` and `df -h` comparisons highlight that VMs require dedicated memory and storage allocations for a redundant OS, whereas containers use resources much more efficiently, allowing for a far higher density of microservices to run on the same physical hardware.
3. **Immutability and Portability:** Containers package code and dependencies into a single immutable image. This guarantees consistency across development, testing, and production environments, eliminating the "it works on my machine" problem, which is vital when deploying complex microservice architectures.
4. **Granular Scaling:** Microservice architectures benefit from independently scaling specific services. The lightweight nature of containers makes it resource-efficient to run multiple instances of a specific, heavily-loaded microservice without the massive overhead of provisioning full VMs for each instance.

While VMs offer stronger hardware-level isolation, the efficiency, speed, and portability of containers make them the industry standard for deploying modern, scalable microservice architectures.
