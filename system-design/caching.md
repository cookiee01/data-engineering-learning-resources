# Caching (System Design Notes — AWS Terms)

## Goal (in 1 minute)
By the end of this note, you should be able to:
- Explain what caching is and why it helps.
- Choose the right cache layer on AWS (CloudFront vs Redis vs DAX vs local cache).
- Design cache keys, TTLs, and invalidation.
- Debug common cache failures (stale data, stampedes, hot keys).

---

## 1) Start From First Principles (No Cache)
Baseline system:

```
Client -> Service -> Database
```

What happens as traffic grows:
- DB becomes the bottleneck (CPU, IOPS, connection limits).
- P95/P99 latency rises.
- Spikes cause timeouts and cascading failures.

**Caching idea**: store the answer to a request somewhere faster/cheaper than the DB so repeated reads avoid recomputation.

---

## 2) What Caching Is (Plain Definition)
A cache is a fast storage layer that keeps copies of data so future reads are cheaper/faster.

Two important properties:
- Cached data can be **stale**.
- Cache is usually **best-effort** (your system must work even if cache is empty/down).

---

## 3) Common Cache Layers on AWS (Where to Cache)
Think in layers from "closest to the user" to "closest to the data":

### Layer A: Edge caching (CloudFront)
**When**: static assets, public content, API GET responses (carefully).

```
Client -> CloudFront (cache) -> Origin (ALB/API Gateway) -> Service
```

Good for:
- Reducing latency for global users.
- Offloading origin traffic.

Key knobs:
- TTL, cache policy, origin request policy.
- Cache key includes path, query strings, headers, cookies (be deliberate).

Pitfalls:
- Caching personalized responses accidentally.
- Wrong cache key = incorrect content returned.

### Layer B: Service-side cache (ElastiCache Redis/Memcached)
**When**: hot reads, expensive computations, session/token data, rate limits.

```
Client -> Service -> Redis (cache)
                -> DB (source of truth)
```

Good for:
- Lowering DB load.
- Faster P95 for frequently read objects.

Pitfalls:
- Hot keys causing uneven load.
- Cache stampede when popular keys expire.

### Layer C: Database accelerator (DynamoDB DAX)
**When**: DynamoDB heavy reads with microsecond latency goals.

```
Service -> DAX -> DynamoDB
```

### Layer D: In-process/local cache
**When**: tiny, very hot data; avoiding network hop.

Pitfalls:
- Each instance has its own cache (inconsistent).
- Memory pressure and eviction.

---

## 4) Cache Patterns (How Reads/Writes Work)

### 4.1 Cache-aside (lazy loading) — most common
**Read path**
1. Read from cache
2. If miss, read from DB
3. Write result to cache

Pros:
- Simple and widely used.
- Cache can be best-effort.

Cons:
- First request is slow.
- Stampedes possible.

### 4.2 Read-through
Cache library handles DB fetch on miss.

Pros:
- Cleaner app code.

Cons:
- Requires specific tooling; harder debugging.

### 4.3 Write-through
Write to cache and DB synchronously.

Pros:
- Cache stays fresh.

Cons:
- Higher write latency.

### 4.4 Write-back / write-behind
Write to cache first, DB later asynchronously.

Pros:
- Fast writes.

Cons:
- Risk of data loss; complex correctness.

---

## 5) TTL, Invalidation, and Freshness
This is where most real-world pain lives.

### TTL (time-to-live)
- Short TTL: fresher data, more DB load.
- Long TTL: stale risk, lower DB load.

Rule of thumb:
- Cache data that’s read often and can tolerate some staleness.

### Invalidation (when data changes)
Options:
- **Delete cache on write** (common): after updating DB, delete the cache key so next read repopulates.
- **Update cache on write**: after DB update, write the new value into cache.

Pitfalls:
- Invalidation across multiple keys (e.g., object + list + aggregates).

---

## 6) The Stuff That Breaks Production

### 6.1 Cache stampede (dogpile)
Many requests miss at once (popular key expired or cache restart) -> DB is hammered.

Mitigations:
- Add jitter to TTL (randomize expiry)
- Single-flight / request coalescing (one recompute, others wait)
- Stale-while-revalidate (serve stale briefly while refreshing)

### 6.2 Hot keys
A single key gets extreme traffic -> one Redis shard/node becomes bottleneck.

Mitigations:
- Key sharding (e.g., split into N keys)
- Multi-level caching (edge + redis + local)
- Precompute / denormalize

### 6.3 Cache poisoning / wrong cache key
If cache key ignores user identity, you can leak data.

Mitigations:
- Make cache key explicit and reviewed
- Separate public vs private caching
- Vary by auth/user/tenant where needed

### 6.4 Thundering herd after deploy
New version changes serialization or key format -> mass misses.

Mitigations:
- Versioned keys (`v1:...`, `v2:...`)
- Gradual rollout and warming

---

## 7) Cache Key Design (Interview-Ready)
A good cache key is:
- Deterministic
- Stable across deployments (unless versioned)
- Encodes the dimensions that change the answer

Examples:
- `user:{user_id}:profile:v1`
- `tenant:{tenant_id}:report:{report_id}:date:{yyyy-mm-dd}:v3`

Be careful with:
- Query strings order
- Floating timestamps
- Large keys

---

## 8) Observability (You *must* mention this in interviews and production)
Metrics:
- Hit rate / miss rate
- Evictions
- Latency (cache GET/SET)
- Error rate / timeouts
- DB QPS correlated with cache miss spikes

Logs:
- Cache key sampling (not full keys if sensitive)
- Miss reason (expired vs not found vs error)

Alarms:
- Miss spike + DB saturation
- Redis memory nearing limit

---

## 9) AWS Service Mapping Cheatsheet
- CDN/edge cache: CloudFront
- API caching: API Gateway caching (use cautiously)
- In-memory cache: ElastiCache Redis/Memcached
- DynamoDB cache: DAX
- Secrets/parameters: SSM/Secrets Manager (not a cache, but often confused)

---

## 10) Interview Questions + Strong Answers
1. **Where would you cache in AWS?**
   - “CloudFront for edge/static and safe GETs; Redis for service-side hot objects; DAX for DynamoDB acceleration.”

2. **How do you handle cache invalidation?**
   - “Prefer delete-on-write with short TTL + versioned keys for safety; for complex aggregates, invalidate dependent keys or rebuild asynchronously.”

3. **What causes 99th percentile spikes with caching?**
   - “Stampedes after TTL expiry, hot keys, or cache node issues; mitigations include jitter, request coalescing, stale-while-revalidate.”

4. **How do you prevent data leaks?**
   - “Correct cache key design; never cache personalized responses at edge without varying on identity; enforce separation of public/private caching.”
