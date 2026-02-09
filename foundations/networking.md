# Networking Fundamentals

## Playlists
- [Networking Fundamentals Playlist](https://www.youtube.com/playlist?list=PLDQaRcbiSnqF5U8ffMgZzS7fq1rHUI3Q8)

---

## Forward Proxy vs Reverse Proxy (AWS Terms, First Principles)

### The baseline: no proxy
You have a backend service with a public IP.

```
Internet Client
  |
  v
EC2 / ECS / EKS service (public)
```

What this implies:
- Your backend must terminate TLS.
- Your backend must handle spikes.
- Your backend IP is directly exposed.
- Deployments are risky (one box/service, no traffic control).

In production, we almost never keep it this way.

---

## Reverse Proxy (what it really means on AWS)

### Plain definition
A reverse proxy is the “front door” in front of your servers/services. Clients connect to the reverse proxy, and the reverse proxy decides which backend receives the request.

On AWS, the reverse-proxy role is commonly played by:
- CloudFront (edge reverse proxy + CDN)
- ALB (Layer 7 reverse proxy + routing + load balancing)
- NLB (Layer 4 proxy/load balancer)
- API Gateway (front door for APIs; not called a proxy in day-to-day, but behaves like one)

### Canonical modern AWS request path
This is the most common “real” picture you’ll see in companies.

```
Client
  |
  v
Route53 (DNS)
  |
  v
CloudFront (reverse proxy at the edge; optional)
  |
  v
WAF (often attached to CloudFront or ALB)
  |
  v
ALB (reverse proxy; L7 routing + load balancing)
  |
  v
Target Group
  |
  v
ECS tasks / EKS pods / EC2 ASG
```

Key mindset:
- CloudFront/ALB are the “public contract”.
- Backends are private, replaceable, and scaled independently.

---

## Why Reverse Proxy Exists (Real AWS Use Cases)

### 1) Load balancing + scaling
Without it:

```
All traffic -> one service instance -> overload -> timeouts
```

With ALB:

```
Traffic -> ALB -> healthy targets A/B/C
```

How ALB makes this work:
- Health checks decide which targets receive traffic.
- It spreads traffic across targets.
- Autoscaling can add/remove targets without changing the client URL.

Interview soundbite:
- “ALB decouples client endpoint from backend fleet and allows horizontal scaling via target groups and health checks.”

### 2) TLS termination (HTTPS handling)
Instead of managing certificates on every backend:
- TLS terminates at CloudFront and/or ALB using ACM certificates.
- Backends can run HTTP internally, or TLS again if required.

Flow:

```
Client HTTPS
  -> CloudFront/ALB decrypts
  -> (optional re-encrypt)
  -> Backend
```

Common gotchas:
- Backend generates redirects using the wrong scheme unless you honor forwarded headers.

### 3) Routing (path/host based)
ALB can route based on:
- host: `api.example.com` vs `app.example.com`
- path: `/v1/*` vs `/v2/*` vs `/health`
- headers: for canary rollouts

Example:

```
/api/*    -> api-service target group
/images/* -> image-service target group
/         -> web target group
```

### 4) Zero-downtime deploys (blue/green, canary)
Reverse proxies enable controlled rollout.

Example (canary):
- 90% traffic to v1 target group
- 10% traffic to v2 target group
- rollback by flipping weights

On AWS you’ll see this via:
- ALB weighted target groups
- CodeDeploy blue/green (common for ECS)

### 5) Security shielding (hide backends)
Backends should not be reachable directly.

Typical pattern:
- ALB is public.
- Backends are in private subnets.
- Security groups allow inbound only from ALB.

This makes:
- IP scanning less useful.
- Fewer direct attack surfaces.

### 6) Rate limiting / bot protection (WAF)
Reverse proxy layer is where you attach:
- AWS WAF rules
- IP reputation blocks
- request rate limits

You don’t want to implement these separately in every service.

---

## Forward Proxy (AWS Terms)

### Plain definition
A forward proxy sits in front of clients and represents clients when they access the internet.

Typical corporate story:

```
Employee laptop
  -> corporate forward proxy
  -> internet
```

On AWS, common forward-proxy scenarios:
- Instances in private subnets needing controlled outbound internet access.
- Centralized egress filtering.
- Auditing outbound requests.

Common AWS building blocks used around this:
- NAT Gateway (not a proxy with HTTP features, but central outbound path)
- Egress proxy on EC2/ECS (Squid, Envoy) for L7 controls
- VPC endpoints / PrivateLink to avoid internet for AWS services

Key mindset:
- Forward proxy is about outbound control.
- Reverse proxy is about inbound traffic management.

---

## The “On the Wire” Details That Matter in Interviews

### Forwarded headers (why apps behave differently in prod)
When TLS terminates at CloudFront/ALB, your backend might see:
- inbound scheme as `http` (even though client used `https`)
- client IP as the load balancer IP

Fix is to rely on forwarded headers.

Common headers:
- `X-Forwarded-For`: original client IP chain
- `X-Forwarded-Proto`: `http` or `https`
- `X-Forwarded-Host`: original host
- `X-Request-Id` (or `X-Amzn-Trace-Id`): request correlation

Common bug:
- “redirect loop” or wrong absolute URLs because backend thinks scheme is `http`.

### Timeouts (classic 502/504/499 issues)
There are multiple timeouts:
- Client timeout
- CloudFront timeout
- ALB idle timeout
- Backend server read/connection timeout

Typical failure patterns:
- Backend slow -> ALB returns 504
- Backend resets connection -> ALB returns 502
- Client gives up early -> ALB logs 499 (depending on stack)

Interview-friendly approach:
- Always state: “We need consistent timeout and retry policies across client, proxy, and upstream; otherwise we get retry storms or phantom failures.”

### Retries and idempotency
Reverse proxies and clients may retry.
- Retrying non-idempotent operations (like “create order”) can double-write.

Staff-level statement:
- “Retries are safe only if the operation is idempotent or guarded by idempotency keys.”

---

## Debugging Playbook (AWS-First)

### Symptom: users see 502
Check in order:
- CloudFront error logs (if in front) and origin health
- ALB target health status
- Backend logs for connection resets, crashes, TLS mismatch (if ALB->backend TLS)

Most common root causes:
- wrong target port/security group
- bad health check path
- backend crash loop

### Symptom: users see 504
Check:
- ALB idle timeout vs backend processing time
- backend saturation (CPU/memory), thread pool exhaustion
- downstream dependencies (DB) slow

Common fixes:
- optimize backend
- increase timeout (only if justified)
- introduce async processing

### Symptom: works in local, fails in prod
Proxy-related usual suspects:
- missing forwarded header handling
- path rewrite rules
- request/response size limits
- CORS/host header differences

---

## Reverse Proxy vs Forward Proxy (30-second answer)
- Reverse proxy: inbound, represents servers, handles routing/TLS/load balancing. On AWS: CloudFront + ALB.
- Forward proxy: outbound, represents clients, controls/filters/caches egress. On AWS: egress proxy pattern; NAT for routing, plus L7 proxy when you need filtering.

---

## Interview Questions You Should Be Able to Answer
1. Where does TLS terminate in your AWS design and why?
2. How do you preserve client IP to the backend?
3. What’s the difference between ALB and NLB and when do you use each?
4. How do you do blue/green or canary with ALB?
5. What causes 502 vs 504, and how do you debug it?
6. How do timeouts and retries interact across client, CloudFront, ALB, and backend?
7. How would you add WAF and rate limiting?

