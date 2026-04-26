# Lab 4: Microservices and Cloud-Native Design

## Part 1: Simulated Execution & Screenshots

### 1. Bringing Up the Microservices
**Command:** `docker compose up --build -d`
```text
[+] Building 20.5s (16/16) FINISHED
 => [product-service internal] load build definition from Dockerfile
 => => transferring dockerfile: 184B
 => [order-service internal] load build definition from Dockerfile
 ...
[+] Running 3/3
 ✔ Network lab4_default              Created
 ✔ Container product-service         Started
 ✔ Container order-service           Started
```

### 2. Creating an Order (Successful Communication)
**Command:** `curl -X POST -H "Content-Type: application/json" -d '{"product_id": "1"}' http://localhost:5002/orders`
```json
{
  "message": "Order created successfully",
  "order": {
    "product": {
      "name": "Laptop",
      "price": 999.99
    },
    "status": "confirmed"
  }
}
```
*Observation:* The `order-service` successfully reached out to the `product-service` via the internal Docker network (`http://product-service:5001`) to retrieve the product details before confirming the order.

### 3. Graceful Degradation / Failure Simulation
**Command:** Stop the product service.
`docker stop product-service`
```text
product-service
```

**Command:** Try to create an order again.
`curl -X POST -H "Content-Type: application/json" -d '{"product_id": "1"}' http://localhost:5002/orders`
*(The request hangs for about ~6 seconds as it exhausts the 3 retries with 2-second timeouts)*
```json
{
  "details": "HTTPConnectionPool(host='product-service', port=5001): Max retries exceeded with url: /products/1...",
  "error": "Product service unavailable"
}
```
*Observation:* Instead of crashing or returning a generic 500 error, the `order-service` attempts to retry the connection. Upon complete failure, it handles the exception and returns a graceful `503 Service Unavailable` response, maintaining the stability of the order service itself.

---

## Part 2: Reflection Report

**1. Which parts show benefits over a monolith?**
- **Independent Deployability:** `product-service` and `order-service` can be deployed, scaled, and updated independently. If we need 10 instances of `product-service` but only 2 of `order-service`, we can scale them separately.
- **Fault Isolation:** Even though `product-service` went down, `order-service` remained alive and functional (handling its own health checks and returning a managed error instead of crashing the entire system).

**2. What new complexities were introduced?**
- **Network Unreliability:** In a monolith, services communicate via fast, reliable in-memory function calls. In this lab, we had to introduce network logic (retries, timeouts, and error handling) because network calls can fail.
- **Service Discovery & Routing:** We had to configure Docker Compose networks and inject environment variables (`PRODUCT_SERVICE_URL`) so services know how to find each other.

**3. What breaks if latency increases?**
If network latency between `order-service` and `product-service` exceeds the configured 2-second timeout, `order-service` will assume `product-service` has failed. It will retry and eventually throw a 503 error, even if `product-service` is perfectly healthy but just slow. This can cause a cascading failure if not managed with circuit breakers.

**4. Which 12-factor principles are visible?**
- **III. Config (Store config in the environment):** We passed `PRODUCT_SERVICE_URL` as an environment variable to `order-service` rather than hardcoding it.
- **VII. Port binding (Export services via port binding):** Both Flask apps are self-contained and bind to specific ports (`5001` and `5002`), avoiding reliance on external web servers like Apache for execution.
- **VIII. Concurrency (Scale out via the process model):** The architecture allows us to horizontally scale the containers easily using orchestration tools like Docker Compose or Kubernetes.
