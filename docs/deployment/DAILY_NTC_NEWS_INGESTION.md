# Daily NTC news ingestion

The daily NTC news job runs **inside the deployed backend**. The scheduler never
opens a local SQLite file: it makes one authenticated request to the deployed
API, which uses that service's `DATABASE_URL` (PostgreSQL in production).

## What is fetched

The backend fetches the official NTC home page at `https://testcenter.kz/`,
where the NTC publishes its current news cards server-side. It parses the published `news-card`
records (title, excerpt, link, and date) without executing remote JavaScript.
Only complete cards are accepted. Responses are limited to 2 MB, redirects must
remain on `https://testcenter.kz/`, and the existing URL allow-list is enforced
again before insertion.

An empty card list is considered an upstream format failure, rather than a
successful no-op, so a template change cannot silently stop ingestion.

Each run stores the unmodified listing response in `source_documents`, and each
article keeps its canonical official URL in `news_sources`. The existing
SHA-256 content hash and canonical URL logic means repeats are skipped and
official edits create `news_versions` rather than duplicate articles.

## Deploy configuration

Set these on the Railway backend service (never commit their values):

| Variable | Required | Notes |
| --- | --- | --- |
| `ENVIRONMENT` | yes | `production` |
| `DATABASE_URL` | yes | Railway PostgreSQL URL; SQLite is rejected by the job in production. |
| `NEWS_INGESTION_SECRET` | yes | Random deployment-only secret, e.g. `python -c "import secrets; print(secrets.token_urlsafe(48))"`. |

After deployment, the endpoint is:

```text
POST https://<your-backend-domain>/api/v1/internal/jobs/daily-news-ingest
X-UNT-Ingestion-Key: <NEWS_INGESTION_SECRET>
```

It is intentionally excluded from OpenAPI and does not accept user JWTs. The
secret comparison is constant-time. Concurrent PostgreSQL invocations use an
advisory lock; a second invocation receives HTTP 409 rather than running a
second batch.

## Scheduler

The checked-in GitHub workflow is now a scheduler only; it has no Python setup,
does not run migrations, and has no database credentials. Add these repository
Actions secrets:

| GitHub Actions secret | Value |
| --- | --- |
| `INGESTION_ENDPOINT` | The complete endpoint URL above. |
| `NEWS_INGESTION_SECRET` | Exactly the Railway `NEWS_INGESTION_SECRET` value. |

It invokes the endpoint daily at 06:00 Asia/Almaty (01:00 UTC) and retries
transient HTTP failures twice. A platform scheduler (for example a Railway cron
service or an external scheduler) may call the same endpoint instead; do not
give it direct database credentials.

## Operator checks

1. Deploy migrations and confirm `GET /ready` reports a connected database.
2. Trigger the workflow manually, or make a one-time authenticated `POST`.
3. Confirm `ingestion_runs` has `job_name=daily_ntc_news_cron`, and inspect its
   counts/status.
4. Confirm `source_documents` contains the listing snapshot and that published
   articles link to `testcenter.kz` via `news_sources`.

Failures return a non-2xx response to the scheduler. The run itself records a
bounded error summary, so alerts should be configured on failed GitHub workflow
runs or equivalent scheduler failures.
