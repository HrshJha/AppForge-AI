<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2d0b5a,50:6b21a8,100:a855f7&height=220&section=header&text=⚡️%20AppForge%20AI&fontSize=52&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Compiler-grade%20Natural%20Language%20to%20Production-App%20generation%20engine&descAlignY=58&descSize=16&descColor=ccccff" width="100%"/>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-14.2-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js"/>
  <img src="https://img.shields.io/badge/Groq-LLaMA3-f3f4f6?style=for-the-badge&logo=ai&logoColor=black" alt="Groq LLaMA3"/>
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/github/stars/HrshJha/AppForge-AI?style=for-the-badge&color=gold" alt="GitHub Stars"/>
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=for-the-badge" alt="PRs Welcome"/>
</div>

<br/>

<div align="center">
  <table>
    <tr>
      <td align="center">🧠<br/><b>5-Stage Pipeline</b><br/>Deterministic generation</td>
      <td align="center">🛡️<br/><b>Cross-Layer Validation</b><br/>10 rigorous rule checks</td>
      <td align="center">⚕️<br/><b>Self-Healing</b><br/>LLM + Boot repair loop</td>
      <td align="center">⚡️<br/><b>GroqCloud</b><br/>Lightning fast generation</td>
      <td align="center">📦<br/><b>Bootability</b><br/>Execution Packager</td>
    </tr>
  </table>
</div>

<br/>

> *"Stop hallucinating architectures. Start compiling applications."*

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### 📌 The Problem

Current LLM coding assistants operate as glorified text generators. When asked to build an application, they hallucinate inconsistent database schemas, miss foreign key constraints, forget to link API endpoints to frontend UI elements, and produce code that fundamentally fails to boot.

This status quo leaves developers constantly performing "AI janitor work"—manually stitching together mismatched components, fixing broken imports, and reconciling conflicting assumptions across different layers of the stack.

```
Problem → Naive LLM Generation → Consequence
```

| Type | Failure Mode | Severity |
|---|---|---|
| 🔴 **Structural** | Database columns missing for defined domain entities | Critical |
| 🔴 **Security** | API endpoints exposed without required authentication | Critical |
| 🟡 **Functional** | Frontend UI components referencing non-existent API routes | High |
| 🟠 **Logical** | Payment gateways omitted for premium tier features | Medium |

**AppForge AI solves this by treating application generation as a compiler problem: utilizing intermediate representations (IR), strict cross-layer validation rules, and deterministic repair loops to guarantee structural consistency.**

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### 💡 The Solution

AppForge AI forces the LLM to adhere to a strict, multi-stage "compilation" pipeline. Instead of generating raw code in one shot, it first extracts the intent, designs an Intermediate Representation (IR), generates schemas in parallel, and then runs them through a deterministic validation engine. If inconsistencies are found, it surgically repairs them in a loop before packaging.

```text
               ┌────────────────────────┐
               │  3. Parallel Schema Gen│
               │    ├── DB Schema       │
NL Input  ───► │    ├── API Spec        │ ───►  4. Validate + Repair  ───► 5. Execution Packager ───► Output
 1. Intent     │    ├── UI Mockup       │       (10 Rules + LLM)         (Boot Repair)
 2. System IR  │    └── Auth Policy     │
               └────────────────────────┘
```

**Because AppForge AI enforces 10 strict cross-layer validation rules (e.g., *every UI data source must map to an API endpoint*), it guarantees that the resulting application configuration is structurally sound and bootable.**

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### 🚀 Features

- 🧠 **Deterministic 5-Stage Pipeline** — Compiles natural language into consistent schemas using sequential & parallel execution.
- 📐 **Canonical System Design IR** — Uses an Intermediate Representation as the source of truth to avoid downstream hallucinations.
- 🛡️ **10 Cross-Layer Validation Rules** — Strict Pydantic checks ensuring DB, API, UI, and Auth components align perfectly.
- ⚕️ **Self-Healing Repair Loop** — Automatically feeds validation errors back to the LLM for surgical, per-layer fixes (up to 3 passes).
- 📦 **Boot Repair Engine** — Deterministic local fallback for type casting, primary key linking, and structural fixes.
- ⚡️ **GroqCloud Integration** — Leverages `Llama3-70b/8b-instant` for lightning-fast, ultra-low latency schema generation.
- 🛡️ **Ambiguity Gate** — Detects vague prompts (score > 0.6) and requests clarification before burning tokens.
- 💸 **Token Budget Enforcement** — Tracks tokens and cost per stage, managing API limits gracefully.
- 🔒 **Non-Negotiable Security** — Hardcoded constraints for JWT auth, bcrypt hashing, and rate-limiting.

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### 🛠 Tech Stack

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white" alt="Pydantic"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/>
  <img src="https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js&logoColor=white" alt="Next.js"/>
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white" alt="Tailwind"/>
  <img src="https://img.shields.io/badge/Groq-f3f4f6?style=flat-square&logo=ai&logoColor=black" alt="Groq"/>
  <img src="https://img.shields.io/badge/Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white" alt="Pytest"/>
</div>

<br/>

| Component | Technology | Why |
|---|---|---|
| **API Framework** | FastAPI | High performance async execution, native OpenAPI |
| **Validation Engine**| Pydantic v2 | Extremely strict, typed schema validation |
| **Database** | SQLite + SQLAlchemy | Lightweight synchronous persistence |
| **Frontend** | Next.js 14 | React framework for robust UI rendering |
| **Styling** | Tailwind CSS | Rapid, utility-first UI styling |
| **LLM Provider** | GroqCloud (LLaMA3) | Ultra-fast token generation for complex JSON |
| **Test Runner** | Pytest | Comprehensive validation of the 39-test suite |

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### 📂 Project Structure

```text
📦 AppForge-AI
 ┣ 📁 backend
 ┃ ┣ 📁 app
 ┃ ┃ ┣ 📁 api              # 🌐 FastAPI routers and endpoints
 ┃ ┃ ┣ 📁 core             # 📋 App config and BaseSettings
 ┃ ┃ ┣ 📁 db               # 🗄️ SQLAlchemy DB setup
 ┃ ┃ ┣ 📁 llm              # 🤖 Unified Groq/OpenAI client & prompts
 ┃ ┃ ┣ 📁 pipeline         # 🚀 5-Stage Orchestrator (Intent -> Packager)
 ┃ ┃ ┣ 📁 schemas          # 📐 Pydantic models for AppConfig & Validation
 ┃ ┃ ┣ 📁 services         # ⚙️ Business logic
 ┃ ┃ ┣ 📁 validation       # 🛡️ JSON repair and structural checks
 ┃ ┃ ┗ 🐍 main.py          # 🚀 Application entry point
 ┃ ┣ 📁 tests              # 🧪 Pytest test suite (39 passing)
 ┃ ┣ 📋 requirements.txt   # 📦 Python dependencies
 ┃ ┗ 📋 .env.example       # 🔧 Template for environment variables
 ┣ 📁 frontend
 ┃ ┣ 📁 src                # 🌐 Next.js React components
 ┃ ┣ 📋 package.json       # 📦 Node dependencies & scripts
 ┃ ┣ 📋 tailwind.config.js # 🎨 Tailwind styling config
 ┃ ┗ 📋 next.config.js     # ⚙️ Next.js settings
 ┗ 📋 README.md            # 📖 Documentation
```

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### ⚙️ Installation & Setup

#### Prerequisites
| Tool | Version | Link |
|---|---|---|
| Python | 3.9+ | [Download](https://www.python.org/downloads/) |
| Node.js | 18+ | [Download](https://nodejs.org/) |
| Groq API Key | | [GroqCloud](https://console.groq.com/) |

---

**1. Clone the Repository**
```bash
git clone https://github.com/HrshJha/AppForge-AI.git
cd AppForge-AI
```

---

**2. Setup Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
*Edit `.env` and add your `GROQ_API_KEY` or `OPENAI_API_KEY`.*

---

**3. Start the Backend Server**
```bash
uvicorn app.main:app --port 8000 --reload
```

---

**4. Setup & Start Frontend**
```bash
cd ../frontend
npm install
npm run dev
```

---

**5. Verify it works**
```bash
curl http://localhost:8000/api/v1/health
# Expected: {"service": "appforge-ai", "status": "ok"}
```

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### 🧪 Usage

#### API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health check |
| `POST` | `/api/v1/generate` | Run full 5-stage NL compilation pipeline |
| `POST` | `/api/v1/validate` | Run cross-layer validation on raw schemas |
| `POST` | `/api/v1/repair` | Trigger surgical LLM repair loop |
| `GET` | `/api/v1/metrics` | View aggregate pipeline latency/cost stats |

#### Code Examples

**Compile an Application from Prompt:**
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Build a task management app with users, projects, and tasks. Premium users can have unlimited projects."}'
```

**Expected JSON Response (abbreviated):**
```json
{
  "job_id": "a1b2c3d4-e5f6...",
  "status": "success",
  "app_config": {
    "metadata": {
      "app_name": "TaskFlow",
      "version": "1.0.0"
    },
    "domain": {
      "entities": [...]
    },
    "api": {...},
    "db": {...},
    "ui": {...},
    "auth": {...}
  },
  "metrics": {
    "total_latency_ms": 4250,
    "total_cost_usd": 0.0012,
    "repair_count": 0,
    "consistency_score": 1.0
  }
}
```

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### 🔬 Pipeline Architecture Deep Dive

```text
[Natural Language Prompt]
         │
         ▼
[Stage 1: Intent Extraction] ──(Gate: Ambiguity Score > 0.6?)──► Clarification Requested
         │
         ▼
[Stage 2: System Design] (Outputs Canonical SystemDesignIR)
         │
         ├──────────────────────┬──────────────────────┬──────────────────────┐
         ▼                      ▼                      ▼                      ▼
[Stage 3: DB Schema]   [Stage 3: API Spec]    [Stage 3: UI Mockup]   [Stage 3: Auth Policy]
         │                      │                      │                      │
         └──────────────────────┴──────────┬───────────┴──────────────────────┘
                                           ▼
                            [Stage 4: Validation Engine]
                                   (10 CL Rules)
                                           │
                                ◀──(Fail)──┴──(Pass)──▶
                                │                     │
                        [LLM Repair Loop]             │
                                                      ▼
                                         [Stage 5: Boot Repair Packager]
                                                      │
                                                      ▼
                                       [Validated Executable AppConfig]
```

**Validation & Repair Rules:**
| Rule ID | Condition Checked | Action on Failure |
|---|---|---|
| `CL-001` | API endpoints reference valid Domain Entities | Trigger LLM Repair (API layer) |
| `CL-002` | UI Data Sources map to defined API endpoints | Trigger LLM Repair (UI layer) |
| `CL-004` | DB Columns backed by Domain Entity Fields | Trigger LLM Repair (DB layer) |
| `CL-010` | All endpoints have explicit auth rules | Boot Repair Engine fixes locally |

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### ⚙️ Configuration

The application is configured via `.env` files using Pydantic `BaseSettings`.

```python
# .env
LLM_PROVIDER="groq"
GROQ_API_KEY="gsk_..."
DATABASE_URL="sqlite:///./appforge.db"
JWT_SECRET="appforge-dev-secret-change-in-prod"
DEBUG=True
MAX_REPAIR_PASSES=3
AMBIGUITY_THRESHOLD=0.6
```

| Setting | Default | Effect |
|---|---|---|
| `LLM_PROVIDER` | `groq` | Switches between `groq` and `openai` |
| `MAX_PROMPT_LENGTH` | `2000` | Truncates input prompts exceeding limit |
| `MAX_REPAIR_PASSES` | `3` | Maximum LLM loop iterations before fallback |
| `AMBIGUITY_THRESHOLD`| `0.6` | Prompt clarity score required to proceed |

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### 📦 Scope & Limitations

- **What it DOES NOT do:** AppForge AI does not execute raw arbitrary python files or deploy containers natively. It outputs a rigorously validated `AppConfig` schema that *represents* a bootable app.
- **Performance dependencies:** Speed depends entirely on the LLM API limit. Using GroqCloud free tier currently limits to ~6000 Tokens Per Minute (TPM), requiring built-in sleeps between pipeline stages.
- **Ideal Use Case:** Rapid prototyping of monolithic SaaS architectures where structural consistency (DB → API → UI) is critical and manual scaffolding is too slow.

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### 📈 Future Roadmap

| Status | Feature |
|---|---|
| ✅ | 5-Stage Orchestrator Pipeline |
| ✅ | GroqCloud LLaMA3 Integration |
| 🔜 | Multi-Agent Swarm (Stage 3 split among distinct agents) |
| 🔜 | AST-based Code Generation Output (from AppConfig) |
| 🔜 | Docker Compose Generation |

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### 🤝 Contributing

1. **Fork** the repository on GitHub
2. **Clone** your fork (`git clone https://github.com/your-name/AppForge-AI.git`)
3. **Branch** out (`git checkout -b feature/cool-new-idea`)
4. **Commit** your changes (`git commit -m "feat: added cool idea"`)
5. **Push** to the branch (`git push origin feature/cool-new-idea`)
6. **Pull Request** back to the main repository

**Contribution Standards:**
- ✅ All code must pass the 39 pytest suite tests.
- ✅ Use `pydantic` v2 strictly for all new schemas.
- ❤️ Keep LLM prompt tokens minimal to respect rate limits.

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### 📜 License

```text
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">

### 🌟 Support the Project

<div align="center">

| Action | Impact |
|---|---|
| **Star** | Boosts project visibility and credibility |
| **Fork** | Allows you to experiment and build upon the core engine |
| **Issue** | Helps identify edge cases and validation rule failures |
| **Share** | Spreads the word to other developers |
| **Feedback** | Shapes the roadmap for future generative features |

<br/>

<a href="https://github.com/HrshJha/AppForge-AI/stargazers"><img src="https://img.shields.io/github/stars/HrshJha/AppForge-AI?style=for-the-badge&color=gold" alt="Stars"/></a>
<a href="https://github.com/HrshJha/AppForge-AI/network/members"><img src="https://img.shields.io/github/forks/HrshJha/AppForge-AI?style=for-the-badge&color=blue" alt="Forks"/></a>
<a href="https://github.com/HrshJha/AppForge-AI/issues"><img src="https://img.shields.io/github/issues/HrshJha/AppForge-AI?style=for-the-badge&color=brightgreen" alt="Issues"/></a>

</div>

<br/>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2d0b5a,50:6b21a8,100:a855f7&height=130&section=footer&animation=fadeIn" width="100%"/>

**Made with 💖 by Harsh Kumar Jha**

*"Stop hallucinating. Start compiling."*
</div>
