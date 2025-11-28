
# 3 — Data model (Postgres schema)

Start simple for production; evolve as you learn:

```sql
-- users
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  whatsapp_number TEXT UNIQUE NOT NULL,
  name TEXT,
  preferred_language TEXT DEFAULT 'hi-IN',
  plan TEXT DEFAULT 'free',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- transactions
CREATE TABLE transactions (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  customer_name TEXT,
  description TEXT,
  amount NUMERIC(12,2),
  currency TEXT DEFAULT 'INR',
  category TEXT,   -- sale, buy, credit, expense
  source TEXT,     -- text, image, voice, email
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- media (receipts)
CREATE TABLE attachments (
  id BIGSERIAL PRIMARY KEY,
  transaction_id BIGINT REFERENCES transactions(id),
  user_id BIGINT REFERENCES users(id),
  file_url TEXT,
  parsed_text TEXT,
  ocr_json JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- conversations (short-term session context)
CREATE TABLE conversations (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  last_message TEXT,
  context JSONB,
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- embeddings (long-term memory)
CREATE TABLE memory (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  key TEXT,
  value TEXT,
  embedding_vector BYTEA,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

Use `alembic` for migrations.

---

# 4 — Message flow & responsibilities (detailed)

1. WhatsApp Cloud API forwards incoming message to your configured webhook (`/webhook/whatsapp`).

   * Messages include text, media_id, contact number.

2. FastAPI webhook:

   * Authenticates the request (verify signature if supported).
   * Looks up or creates `users` by `whatsapp_number`.
   * Normalizes language hints (lang detection).
   * Enqueues light pre-checks (spam rate, length).

3. LangGraph orchestrator:

   * Node 1: Message classifier (determine `text` vs `media` vs `voice` vs `email-forward`).
   * Node 2: If voice → Whisper STT (sync or background worker).
   * Node 3: If media → download from Meta API to S3, enqueue OCR worker.
   * Node 4: NLU node uses IndicBERT/MuRIL to detect intent (`add_txn`, `query_total`, `query_customer`, `clarify`).
   * Node 5: Entity extractor (sequence labeler or rule-based augmenter to extract amount, customer name, category).
   * Node 6: Transaction engine validates & persists transaction; produce aggregation results if query intent.
   * Node 7: Response composer (LLM templates or rule-based replies), optionally produce TTS.
   * Send reply via Meta Cloud API.

4. Background jobs:

   * Heavy OCR parsing, embedding extraction (for memory), and any third-party LLM calls run in Celery workers.

---

# 5 — NLU: fine-tuned IndicBERT / MuRIL — training & deployment

## Data & labels

* Intents: `add_transaction`, `add_receipt`, `query_total_day`, `query_total_period`, `query_customer_balance`, `clarify`, `greet`, `help`.
* Entities: `amount`, `currency`, `customer_name`, `category`, `date`, `invoice_no`.

Collect ~2k–10k examples for robust performance: combine synthetic examples, user logs (with consent), crowdsource Hinglish utterances. Add variations (numerals, rupees symbol, spelled numbers, common typos).

## Training approach

1. Use HuggingFace Transformers. Choose model checkpoints:

   * IndicBERT (small, fast) — good for on-prem inference.
   * MuRIL — performs well for Indian languages.
2. Two tasks:

   * Intent classification (sequence classification head).
   * Entity extraction (token classification/NER head) or use a dedicated spaCy/conditional random field if smaller.

Example fine-tune script outline (pseudo):

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments

tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-bert")
model = AutoModelForSequenceClassification.from_pretrained("ai4bharat/indic-bert", num_labels=num_intents)

# dataset prepare: texts, labels
training_args = TrainingArguments(output_dir="./model_out",
                                  per_device_train_batch_size=16,
                                  num_train_epochs=3,
                                  fp16=True)
trainer = Trainer(model=model, args=training_args, train_dataset=train_ds, eval_dataset=val_ds)
trainer.train()
```

Entity extraction: fine-tune a token classification model similarly.

## Deployment

* Option A (preferred): Host the model as a dedicated model server (FastAPI with `transformers`/`accelerate`) behind autoscaling. Keep models in GPU-enabled instances for low latency if using large models.
* Option B: Use Hugging Face Inference API or a managed inference (cost vs latency tradeoff).
* Cache predictions for repeat patterns.

**Quantization/Optimization:** Use ONNX, `bitsandbytes` 8-bit, or `torch.compile` where possible. For CPU inference, convert to `onnxruntime` and use CPU optimizations.

---

# 6 — LangGraph orchestration design

LangGraph gives you a node/graph style control flow for conversational agents. Design nodes:

* Input Router Node: route by message type (text, image, audio).
* Preprocessing Node: normalize text (Hinglish transliteration), remove salutations, detect digits.
* STT Node: call Whisper or OpenAI Whisper API.
* NLU Node: call IndicBERT/MuRIL model server for intent+entities.
* Clarifier Node: if missing entity (amount/customer), ask follow-up.
* Transaction Node: persist, add metadata, compute quick aggregate.
* Memory Node: push embeddings to Qdrant for long-term facts.
* Response Node: compose response using templates or LLM.
* TTS Node (optional): generate voice reply.

Implement each node as small microservices or functions, and have LangGraph tie them with retries/timeouts.

---

# 7 — OCR & Document parsing

* Use PaddleOCR or Tesseract for receipt extraction. PaddleOCR often more robust in multi-language contexts.
* Pipeline:

  1. Download image (Meta media endpoint) → store in S3.
  2. Pass image URL to OCR worker (Celery).
  3. Run OCR → get text blocks, detect amounts (regex), vendor name heuristics.
  4. Build structured object: `{amount: xxx, vendor: yyy, date: zzz, invoice_no: nnn}`.
  5. Send to transaction classifier to map to `sale`/`expense`/`inventory` etc.
* Use a small ML classifier to predict category from parsed text & Tfidf/embedding features.

---

# 8 — Whisper integration: options & tradeoffs

**Option A — OpenAI Whisper API (recommended for speed & maintenance)**
Pros: maintained model, easy to call, no GPU ops; Cons: API cost.

**Option B — Self-host Whisper (open-source)**

* Run `openai/whisper` or `openai/whisper.cpp` on GPU instances (NVIDIA). Use worker pool and expose simple REST for STT.
* Pros: control & lower per-call cost at scale; Cons: infra cost & maintenance, GPU requirement.

**Implementation tips:**

* Put STT as asynchronous background job. For short voice notes you can do near-real-time; for large audio push to background and post “I’m processing your voice note — I’ll update you soon”.
* Use language detection to choose model settings; send timestamps when ambiguous.

---

# 9 — Backend: FastAPI production setup (sample)

Use `Gunicorn` with `Uvicorn` workers.

`Dockerfile` (example):

```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "--bind", "0.0.0.0:8000", "--timeout", "120"]
```

`app/main.py` (minimal webhook outline):

```python
from fastapi import FastAPI, Request, BackgroundTasks
from app.services.whatsapp import process_whatsapp_event

app = FastAPI()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    # validate signature / source here
    background_tasks.add_task(process_whatsapp_event, payload)
    return {"status":"accepted"}
```

`app/services/whatsapp.py` should parse message, call LangGraph orchestrator, and reply using Meta Cloud API.

---

# 10 — Asynchronous & background processing

* Use Celery + Redis (or RQ) for:

  * OCR processing
  * Whisper STT
  * Embedding computation (for memory)
  * Large LLM calls and report generation
* Keep webhook fast: accept → ack → background processing → reply when ready (or send typing indicator).

---

# 11 — Storage, media & S3 handling

* Store receipts and media in S3 (or Supabase storage). Keep secure, signed URLs.
* Retain raw media for 30–90 days by default; move to cold storage if needed.
* Store parsed OCR output in DB (attachments.parsed_text, ocr_json).

---

# 12 — Vector memory (optional but recommended)

* Qdrant/Chroma: store embeddings for name resolution, customer similarity, repeat vendor detection.
* Compute embeddings with an embedding model (multilingual sentence-transformer).
* Use vector DB for “who owes the most like Ramesh?” fuzzy queries.

---

# 13 — Auth, multi-tenancy & rate limits

* Identify users by WhatsApp number — treat that as primary identifier (store hashed).
* Support multi-tenancy by `user_id` isolation in queries.
* Rate limits:

  * Throttle per-phone-number (e.g., 1 req/sec, 200 req/day) using Redis.
  * Protect model API calls via per-user quotas.
* Billing: plan field in `users` table; enforce transaction count limits with Redis counters.

---

# 14 — Security & compliance (production checklist)

* TLS everywhere (HTTPS enforced).
* Secrets in AWS Secrets Manager / HashiCorp Vault.
* Encrypt sensitive DB columns (e.g., PII) at rest using DB encryption or app-layer AES.
* Store only necessary personal data; keep retention policies & explain in privacy policy.
* Validate media downloads (limit types & sizes: max 10 MB).
* Protect webhooks: verify meta signature or IP allowlists.
* Regular vulnerability scanning & dependency updates.

---

# 15 — Observability & SLOs

* Logging: structured logs (JSON) to CloudWatch/ELK/Datadog. Include request_id and user_id.
* Errors: Sentry for exceptions & performance.
* Metrics: Prometheus scraping metrics; Grafana dashboards for latency, error rates, worker queue size.
* Traces: OpenTelemetry for request traces (end-to-end).
* SLAs/SLOs: e.g., 95% webhooks processed under 500ms (enqueue), 95% OCR tasks complete <3s for small receipts.

---

# 16 — CI / CD (GitHub Actions example)

* Pipeline steps:

  1. Run tests (unit & lint).
  2. Build Docker image and push to container registry (ECR / Docker Hub).
  3. Run migrations via `alembic upgrade head` on deploy.
  4. Deploy to AWS ECS Fargate / Railway / Vercel (if serverless).
  5. Run smoke tests (webhook ping, DB health).

Sample GitHub Actions outline:

```yaml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with: python-version: 3.11
      - name: Install deps
        run: pip install -r backend/requirements.txt
      - name: Run tests
        run: pytest
      - name: Build & push Docker
        uses: docker/build-push-action@v4
        with:
          push: true
          tags: ${{secrets.REGISTRY}}/munimji:${{github.sha}}
```

---

# 17 — Deployment options & recommendations

* **Backend (recommended):** AWS ECS Fargate (Docker). Easy autoscaling, integrates with RDS, ALB. Alternative: Railway for faster setup but less control for scale.
* **Model servers:** GPU instances (if you need low-latency heavy models). Consider separate service for model inference.
* **Database:** AWS RDS Postgres (Multi-AZ). Use read replicas for analytics if necessary.
* **Storage:** S3.
* **Vector DB:** Qdrant cloud or self-hosted on a small cluster.
* **Workers:** ECS tasks or separate EC2/GPU instances for Whisper/large OCR.
* **Vercel:** Good for web dashboard and frontend, not ideal for heavy backend.

---

# 18 — Testing & validation

* Unit tests: logic for transaction creation, parsing, entity extraction.
* Integration tests: webhook flow, DB writes, media download (mock Meta API).
* E2E tests: simulate WhatsApp events via a test harness (use Postman or scripts).
* Load tests: use k6 or locust to simulate webhook bursts; test Celery queue handling.
* A/B test UX prompts for follow-ups/clarifications in small user pilots.

---

# 19 — Cost considerations (early estimate pointers)

* PostgreSQL RDS (db.t3.small) — moderate cost.
* Model inference: large variable — fine-tuning smaller IndicBERT/MuRIL models and running CPU quantized servers is more cost-effective than large LLMs.
* Whisper self-hosted requires GPU (expensive). Use API for early phase.
* Use S3 + lifecycle rules to control storage cost.
* Monitor and cap LLM calls to limit API spend.

---

# 20 — Roadmap for M+1 months after launch

1. Collect real user utterances; expand training corpus; retrain models weekly-ish.
2. Add payments/UPI collection & receipts reconciliation.
3. Add multi-user business accounts & accountant access.
4. Add invoice generation and scheduled reminders.
5. Integrate with supplier APIs / GST for invoice matching.
6. Launch paid plans & analytics dashboards.

---

# 21 — Practical checklists & immediate next steps (actionable)

**Day 0 (prep)**

* Create GitHub repo, set branch protections.
* Create project in cloud (AWS account), create S3 bucket, RDS cluster placeholder.
* Acquire Meta WhatsApp Cloud API business account & phone number (or use test sandbox).

**Day 1–3 (core infra + hello world)**

* Implement FastAPI webhook that verifies request and logs payload.
* Dockerize FastAPI and run locally + via Docker Compose.
* Create basic DB models and run alembic migrations.
* Implement simple text handler: parse amounts with regex and store transaction.

**Day 4–7 (NLU + LangGraph)**

* Prepare NLU training data skeleton and fine-tune a small IndicBERT classifier. Start with few hundred examples.
* Stand up a model server (FastAPI) that returns intents & entities.
* Integrate LangGraph to orchestrate request flow.

**Day 8–11 (media & OCR + Whisper)**

* Implement media download flow, store file on S3, run OCR worker with PaddleOCR.
* Wire Whisper via API for voice notes; make STT worker.

**Day 12–14 (hardening + deploy)**

* Add Redis & Celery workers.
* Add rate limits & basic auth for webhooks.
* Deploy to chosen cloud (ECS Fargate or Railway).
* Run smoke tests; invite pilot users; instrument Sentry & metrics.

---

# 22 — Example code snippets (quick reference)

**Amount extractor (simple regex)**

```python
import re
def extract_amount(text):
    # Handles: 1500, ₹1500, 1,500, Rs. 1500
    match = re.search(r"₹\s?([\d,]+(?:\.\d+)?)|Rs\.?\s?([\d,]+(?:\.\d+)?)|([0-9][\d,]*\.?\d*)\s?rupee", text, re.I)
    if match:
        for group in match.groups():
            if group:
                return float(group.replace(',', ''))
    # fallback: any plain number
    m = re.search(r"([0-9][\d,]*\.\d+|[0-9][\d,]*)", text)
    return float(m.group(1).replace(',', '')) if m else None
```

**Call Meta Cloud API to send message**

```python
import requests
def send_whatsapp_text(phone, text):
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
    payload = {
      "messaging_product": "whatsapp",
      "to": phone,
      "type": "text",
      "text": {"body": text}
    }
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()
```

---

# 23 — Common pitfalls & how to avoid them

* **Not capturing vernacular edge-cases:** continuously log real user queries (with consent) and add to training data.
* **Blocking webhook while waiting for models/ocr:** always accept webhook quickly and process heavy tasks in background.
* **Under-estimating media sizes:** restrict file size and convert images to compressed formats before OCR.
* **No observability:** instrument early; first alerts should be obvious.
* **Hard coupling of services:** make components replaceable (e.g., model server behind API).

---

# 24 — Final recommendations & next deliverables I can produce for you

If you want, I can now generate one (pick one) **immediate runnable artifact**:

1. A **FastAPI starter repository** (Dockerized) with:

   * `/webhook/whatsapp` skeleton
   * SQLAlchemy models + alembic migration for the DB schema above
   * Redis + Celery sample task for OCR/Whisper
   * GitHub Actions CI workflow

2. A **LangGraph orchestration file** (node definitions) that wires the classifier, STT, OCR, transaction node, and response node.

3. A **fine-tuning script + small sample dataset template** for IndicBERT/MuRIL (intent classification + token classification).

4. A **Terraform skeleton** to provision RDS + S3 + ECS (Fargate) on AWS with minimal config.

Tell me which one you want first and I’ll produce it right away (code + Dockerfile + deployment snippets).
