# Cloud & Mobile Computing - Lab Portfolio

## Student Information
- **Name:** [Your Name]
- **Student ID:** [Your Student ID]
- **Course:** Cloud & Mobile Computing

## Overview
This repository contains the completed assignments and deliverables for Labs 1 through 4, covering fundamental cloud concepts, distributed systems, container orchestration, and microservice architectures.

---

## 📁 Repository Structure

### [Lab 1: VMs vs Containers](./lab1)
**Topics:** Cloud Virtualization, Data Center Architecture, Resource Management.
- **`app.py`:** Flask application simulating tail latency.
- **`latency_histogram.py`:** Script generating latency distribution graphs.
- **`lab1_report.md`:** Resource comparison (Multipass vs. Docker) and reflection on microservice architectures.

### [Lab 2: Distributed Consistency](./lab2)
**Topics:** CAP Theorem, Redis Replication, etcd Raft Consensus.
- **`docker-compose.yml`:** Infrastructure configuration for Redis and etcd clusters.
- **`lab2_report.md`:** Simulated terminal execution and analysis of network partitions and leader re-elections.

### [Lab 3: Containerization & Orchestration](./lab3)
**Topics:** Docker Layers, cgroups, namespaces, Kubernetes Deployments & Probes.
- **`Dockerfile.basic` & `Dockerfile.multistage`:** Containerization strategies.
- **`deployment.yaml`, `service.yaml`, `probe-deployment.yaml`:** Kubernetes manifests.
- **`lab3_report.md`:** Analysis of K8s self-healing and detailed reflection questions.

### [Lab 4: Microservices & Cloud-Native Design](./lab4)
**Topics:** 12-Factor App, Fault Isolation, Service-to-Service Communication.
- **`product-service/`:** Python Flask service managing the catalog.
- **`order-service/`:** Python Flask service with timeout/retry logic for robust communication.
- **`docker-compose.yml`:** Orchestration with network routing and health checks.
- **`lab4_report.md`:** Graceful failure simulation and architectural reflections.

---

## 🚀 How to Run Locally

Each lab directory contains its own specific source files, Dockerfiles, or docker-compose files. Generally, you can spin up the infrastructure for Labs 2 and 4 using:

```bash
cd <lab_directory>
docker compose up --build -d
```
