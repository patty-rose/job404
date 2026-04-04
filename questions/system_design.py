"""
System design question bank.
Prompts are calibrated to a mid-level backend engineer with distributed systems experience.
"""

FRAMEWORK = """\
SYSTEM DESIGN FRAMEWORK
═══════════════════════
Use this structure for every problem. Interviewers want to see you drive.

1. CLARIFY REQUIREMENTS (~3-5 min)
   Functional:   What exactly does the system do? Core features only.
   Non-functional: Scale (users, requests/sec, data volume)?
                   Latency requirements? Availability (99.9% vs 99.99%)?
                   Consistency vs availability trade-off?
                   Read-heavy or write-heavy?

2. CAPACITY ESTIMATION (back-of-envelope)
   DAU × requests/user/day = requests/day → requests/sec (÷ 86,400)
   Storage: records/day × record_size × retention_days
   Bandwidth: requests/sec × response_size
   Rule of thumb: 10M DAU × 10 req/day = 100M req/day ≈ 1,200 req/sec

3. HIGH-LEVEL DESIGN
   Draw the components: clients → load balancer → API servers → DB/cache
   Identify the data model early — it drives everything else
   Pick SQL vs NoSQL and justify it

4. DEEP DIVE (~15-20 min, interviewer-guided)
   The interviewer will steer. Common areas:
   - Database schema + indexing
   - Caching strategy (what to cache, eviction policy, invalidation)
   - How you handle scale (horizontal scaling, sharding, read replicas)
   - Handling failures (retries, circuit breakers, idempotency)
   - Message queues for async work
   - CDN for static assets

5. WRAP UP
   Identify bottlenecks
   Discuss monitoring/observability (you know Datadog — use it!)
   Talk about trade-offs you made

KEY CONCEPTS TO KNOW:
  Load Balancer     → distributes traffic, L4 (TCP) vs L7 (HTTP)
  Cache             → Redis/Memcached, read-through vs write-through vs write-behind
  CDN               → edge caching for static/geographic distribution
  Message Queue     → Kafka/SQS, decouples producers/consumers, async processing
  Database          → SQL (ACID, joins, strong consistency) vs NoSQL (scale, flexibility)
  Sharding          → horizontal DB partitioning by key (user_id, geo, hash)
  Read Replicas     → scale reads, slight replication lag
  Rate Limiting     → token bucket or leaky bucket algorithm
  API Gateway       → auth, rate limiting, routing (you've seen this with Istio/K8s)
  Consistent Hash   → distribute load across nodes with minimal redistribution on changes
"""

QUESTIONS = [
    {
        "id": "design_url_shortener",
        "title": "Design a URL Shortener (like bit.ly)",
        "difficulty": "medium",
        "relevance": "Classic intro problem. Tests: hashing, DB design, scale, redirects.",
        "prompt": """\
Design a URL shortening service.

Core features:
  - User submits a long URL, gets back a short URL (e.g. short.ly/aB3kQ)
  - Visiting the short URL redirects to the original

Scale target for this exercise:
  - 100M URLs created per day
  - 10:1 read/write ratio (1B redirects/day)
  - URLs stored for 5 years""",
        "framework_hints": """\
THINGS TO NAIL IN THIS PROBLEM:

Functional requirements: shorten URL, redirect, (optional: analytics, custom slugs, expiry)

Key design decision — how do you generate the short code?
  Option A: Hash (MD5/SHA256) → take first 6-7 chars → risk of collision
  Option B: Base62 encode an auto-increment ID (a-z, A-Z, 0-9 = 62 chars)
            6 chars of base62 = 62^6 ≈ 56 billion combinations

Data model:
  urls table: id (PK), short_code (indexed), long_url, created_at, expires_at, user_id

Capacity:
  100M writes/day = ~1,200 writes/sec
  1B reads/day    = ~12,000 reads/sec → READ HEAVY → cache!

Cache strategy:
  Cache short_code → long_url in Redis (LRU eviction)
  80/20 rule: 20% of URLs get 80% of traffic → cache that 20%

Redirect: HTTP 301 (permanent, browser caches) vs 302 (temporary, always hits your server)
  → Use 302 if you want analytics on every redirect

Scale:
  Multiple API servers behind load balancer
  Read replicas for the DB
  Redis cluster for cache""",
    },
    {
        "id": "design_rate_limiter",
        "title": "Design a Rate Limiter",
        "difficulty": "medium",
        "relevance": "Directly relevant — you've worked with Istio/API gateways. Tests: algorithms, distributed state.",
        "prompt": """\
Design a rate limiter that limits each user to N requests per time window.

Requirements:
  - Limit: 100 requests per minute per user
  - Should work across multiple API server instances
  - Low latency overhead (< 5ms per request)
  - Graceful handling when limit is exceeded (return 429)""",
        "framework_hints": """\
ALGORITHMS — know these:

Token Bucket (most common in interviews):
  Each user has a bucket with max N tokens
  Tokens refill at rate R per second
  Each request consumes 1 token
  If empty → 429. Allows bursting up to bucket size.

Sliding Window Counter:
  Redis: store count per user per minute window
  Key: rate:{user_id}:{current_minute}
  INCR + EXPIRE commands — atomic

Fixed Window Counter:
  Simpler but has edge case: 100 req at 00:59, 100 req at 01:01 = 200 in 2 seconds

WHERE to put rate limiting:
  API Gateway / middleware (you've done this with Istio)
  Before hitting your app servers

DISTRIBUTED STATE:
  Single server → in-memory dict works
  Multiple servers → need shared state → Redis
  Redis is single-threaded → INCR is atomic, no race condition

Headers to return:
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 37
  X-RateLimit-Reset: 1625097600
  Retry-After: 60 (on 429)

Your experience angle: you've configured Istio service mesh — mention you've seen
this at the infrastructure level, now you're designing it at the application level.""",
    },
    {
        "id": "design_ci_cd_pipeline",
        "title": "Design a CI/CD Pipeline System",
        "difficulty": "medium",
        "relevance": "You literally optimized CircleCI pipelines. Talk from real experience + formalize it.",
        "prompt": """\
Design a CI/CD pipeline system (similar to CircleCI, GitHub Actions).

Core features:
  - Developers push code → pipeline triggers automatically
  - Runs: build → test → deploy stages
  - Parallel job execution within a pipeline
  - Pipeline status visible in UI and via webhooks
  - Support 10,000 active repos, ~50,000 pipeline runs/day""",
        "framework_hints": """\
THIS IS YOUR HOME TURF — use your real experience.

Components:
  Webhook Receiver  → catches git push events, creates pipeline record
  Queue             → Kafka/SQS: decouples receiving from executing
  Scheduler         → pulls from queue, assigns jobs to workers
  Worker Pool       → containerized execution (Docker) — you know this!
  Artifact Store    → S3 for build outputs, test results
  State Store       → PostgreSQL for pipeline/job status
  Notification Svc  → webhooks out, Slack/email

Your real optimization: database caching in CircleCI → cache the layer between
builds so you're not re-downloading deps every run. Talk about this!

Key design decisions:
  Job isolation: each job runs in its own container (security + reproducibility)
  Parallel execution: DAG of jobs — run independent jobs concurrently
  Cancellation: if push happens mid-pipeline, cancel old run
  Retries: idempotent jobs with exponential backoff

Data model:
  pipelines: id, repo_id, commit_sha, status, created_at, triggered_by
  jobs: id, pipeline_id, name, status, started_at, finished_at, worker_id
  logs: job_id, timestamp, line (append-only, stream to S3)

Monitoring: you know Datadog — mention streaming metrics:
  queue depth, worker utilization, p95 job duration, failure rates

Scale: fan-out pattern — one push → one pipeline → many parallel jobs""",
    },
    {
        "id": "design_insurance_rating_api",
        "title": "Design a High-Traffic Insurance Rating API",
        "difficulty": "hard",
        "relevance": "You WERE the SME for this. Frame your real work in system design vocabulary.",
        "prompt": """\
Design an insurance premium rating API.

Requirements:
  - Input: driver profile, vehicle info, coverage selections
  - Output: quoted premium price in < 500ms
  - Rates computed from millions of database rows (rating factors)
  - ~5,000 quote requests/sec at peak
  - Rate tables updated monthly by actuaries""",
        "framework_hints": """\
THIS IS YOUR STORY — translate your real work into design vocabulary.

The core problem: computing premiums requires joining many rating factor tables
(age bands, zip codes, vehicle classes, etc.) — can't do this from scratch each request.

Caching strategy (this is the key insight):
  Rating tables change monthly (not per-request)
  → Pre-load rating factors into application memory (in-process cache) at startup
  → Quote computation becomes pure CPU: no DB calls per request
  → Monthly update: rolling restart deploys new rate tables with zero downtime

Architecture:
  Load Balancer → Rating API instances (stateless, horizontally scalable)
  Each instance: in-memory rating engine with cached factor tables
  PostgreSQL: source of truth for rate tables (not on the hot path)
  Redis: optional — cache recent quote results by input hash (dedup identical requests)
  Audit log: every quote written to append-only store (compliance!)

Data model considerations:
  rating_factors: (product_id, factor_type, band_key, multiplier)
  quotes: (id, input_hash, premium, computed_at, rate_version)

Consistency:
  "Eventually consistent" for rates is acceptable (monthly cadence)
  Quote audit log must be durable — write to DB synchronously before returning

Observability (you ran this!):
  Track p99 latency per product line
  Alert on rating engine errors vs not-found factors
  Dashboard: quotes/sec, cache hit rate, error rate by carrier

Your real differentiator: mention the debugging diff tool you built for the
Django admin — tool that made a 1-hour investigation into seconds. That's
operational excellence, and it's what distinguishes engineers at this level.""",
    },
    {
        "id": "design_notification_system",
        "title": "Design a Notification System",
        "difficulty": "medium",
        "relevance": "Tests: async queues, fan-out, multi-channel delivery. Very common interview problem.",
        "prompt": """\
Design a notification system that sends messages across channels.

Requirements:
  - Channels: email, SMS, push notification
  - Triggered by events in other services (e.g., payment processed, claim approved)
  - 10M notifications/day
  - User preferences: users can opt out of certain channels
  - Delivery guarantees: at-least-once (no silent drops)""",
        "framework_hints": """\
CORE PATTERN: Event-driven fan-out with per-channel queues

Flow:
  Source service → Event Bus (Kafka/SQS) → Notification Service
  Notification Service:
    1. Look up user preferences
    2. Fan out to per-channel queues: [email_queue, sms_queue, push_queue]
  Channel workers consume their queue and call provider APIs
    Email: SendGrid/SES
    SMS:   Twilio
    Push:  FCM (Android), APNs (iOS)

Why separate queues per channel?
  Email is slower than push — don't let email backlog block SMS
  Each channel can scale independently
  Channel outages are isolated

Data model:
  notification_templates: (id, name, body_template, channel)
  user_preferences: (user_id, channel, opted_in)
  notification_log: (id, user_id, channel, status, sent_at, event_id)

Idempotency:
  Store event_id in notification_log
  Before sending, check if already sent (dedup) — prevents double-sends on retry

Retry strategy:
  Exponential backoff: 1s, 5s, 30s, 5min, 30min
  Dead letter queue after N failures → alert on-call
  Mark notification as failed in log

Rate limiting per user:
  Don't spam users — max N notifications/hour
  Per-channel caps (SMS is expensive!)

Monitoring:
  Queue depth per channel (spike = downstream outage)
  Delivery success rate by channel and provider
  P95 time from event to delivery""",
    },
    {
        "id": "design_key_value_store",
        "title": "Design a Distributed Key-Value Store",
        "difficulty": "hard",
        "relevance": "Tests distributed systems fundamentals: consistency, replication, partitioning.",
        "prompt": """\
Design a distributed key-value store (like Redis or DynamoDB at a high level).

Requirements:
  - get(key) → value
  - put(key, value)
  - delete(key)
  - Horizontally scalable to handle 1M req/sec
  - High availability (tolerate node failures)
  - Tunable consistency (eventual vs strong)""",
        "framework_hints": """\
THIS IS A CS THEORY PROBLEM — good for building vocabulary around concepts you've used.

PARTITIONING (Sharding):
  Consistent hashing: place nodes on a hash ring
  Each key hashes to a position → assigned to nearest node clockwise
  Adding/removing nodes only moves 1/N of keys (vs naive mod-N which moves everything)
  Virtual nodes: each physical node = multiple ring positions (better load distribution)

REPLICATION:
  Each key replicated to N nodes (e.g., N=3)
  Replication factor chosen at creation time
  Leader-follower vs leaderless (Dynamo-style)

CONSISTENCY LEVELS (tunable):
  W = number of nodes that must acknowledge a write
  R = number of nodes that must respond to a read
  If W + R > N → strong consistency (overlap guarantees seeing latest write)
  W=1, R=1 → eventual consistency (fast but may read stale)

CONFLICT RESOLUTION (for eventual consistency):
  Last-write-wins (timestamp) — simple but loses data
  Vector clocks — track causality, detect true conflicts
  Application-level merge

FAILURE DETECTION:
  Heartbeats between nodes
  Gossip protocol: nodes share membership info peer-to-peer (scales better than centralized)
  Temporary failure → hinted handoff (store writes for unavailable node, replay later)
  Permanent failure → anti-entropy (Merkle trees to efficiently diff and sync replicas)

Your experience angle: you've used Redis, deployed on K8s, configured Istio service mesh.
Connect concepts: K8s node failures → you've debugged this → that's why replication factor > 1.

Key terms interviewers want to hear:
  CAP theorem, consistent hashing, quorum, vector clocks, gossip protocol,
  Merkle tree, read repair, hinted handoff""",
    },
]


def get_by_id(question_id: str) -> dict | None:
    return next((q for q in QUESTIONS if q["id"] == question_id), None)


def get_all_ids() -> list[str]:
    return [q["id"] for q in QUESTIONS]
