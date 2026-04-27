# AppForge AI

**Compiler-grade NL → Production-Ready Application Generator**

A deterministic, multi-stage LLM orchestration pipeline that compiles natural language app descriptions into cross-layer consistent, validated, executable application configurations.

---

## Architecture

```
NL Prompt → Stage 1 (Intent) → Stage 2 (Design) → Stage 3 (4× Parallel Gen) → Stage 4 (Validate + Repair) → Stage 5 (Execution Check)
```

| Stage | Input | Output | Key Feature |
|-------|-------|--------|-------------|
| 1. Intent Extraction | NL prompt | IntentIR | Ambiguity gate (score > 0.6 → clarify) |
| 2. System Design | IntentIR | SystemDesignIR | Canonical source of truth |
| 3. Schema Generation | SystemDesignIR | DB + API + UI + Auth | 4 parallel generators via asyncio |
| 4. Validation & Repair | Raw schemas | Validated AppConfig | 10 cross-layer rules + oscillation detection |
| 5. Execution Packager | AppConfig | ExecutionReport | Bootability validation (no file I/O) |

## Tech Stack

- **Backend**: FastAPI + Pydantic v2 + SQLAlchemy (sync SQLite)
- **Frontend**: Next.js 14 + Tailwind CSS + TypeScript
- **LLM**: Anthropic Claude / OpenAI GPT-4o (unified client)
- **Validation**: 10 cross-layer consistency rules (CL-001 → CL-010)
- **Repair**: Surgical per-layer repair with MD5 oscillation detection

## Quick Start

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your ANTHROPIC_API_KEY
uvicorn app.main:app --port 8000 --reload

# Frontend
cd frontend
npm install
npm run dev  # Port 3000, proxies /api → localhost:8000

# Tests
cd backend
pytest tests/ -v
```

## Cross-Layer Validation Rules

| Rule | Check |
|------|-------|
| CL-001 | API entities exist in domain |
| CL-002 | UI data sources map to API endpoints |
| CL-003 | Logic rule roles exist in auth |
| CL-004 | DB columns backed by domain entity fields |
| CL-005 | Premium features require payment flow |
| CL-006 | Admin role requires admin endpoint |
| CL-007 | Payment entities require Stripe webhook |
| CL-008 | JWT expiry set and ≤ 24h |
| CL-009 | No nullable FKs without annotation |
| CL-010 | All endpoints have explicit auth_required |

## Non-Negotiable Security

- `strategy` = JWT (enforced at Pydantic level)
- `password_storage` = bcrypt (Literal type — cannot be overridden)
- Token expiry ≤ 24h
- Rate limiting always enabled

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/generate` | Full pipeline compile |
| POST | `/api/v1/validate` | Validation-only |
| POST | `/api/v1/repair` | Surgical repair |
| GET | `/api/v1/metrics` | Aggregate pipeline stats |

## Test Results

**39/39 tests passing** — JSON repair, schema validation, all 10 cross-layer rules.

## License

MIT
