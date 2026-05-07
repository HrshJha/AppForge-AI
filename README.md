<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2d0b5a,50:6b21a8,100:a855f7&height=220&section=header&text=⚡️%20AppForge%20AI&fontSize=52&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Compiler-grade%20Natural%20Language%20to%20Production-App%20generation%20engine&descAlignY=58&descSize=16&descColor=ccccff" width="100%"/>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-14.2-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js"/>
  <img src="https://img.shields.io/badge/Cerebras-Primary_LLM-f3f4f6?style=for-the-badge&logo=ai&logoColor=black" alt="Cerebras LLaMA3"/>
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License"/>
</div>

<br/>

> *"Stop hallucinating architectures. Start compiling applications."*

## 📌 Overview

AppForge AI is a compiler-grade Natural Language to App configuration generator. Unlike standard LLM coding assistants that output raw, frequently broken code, AppForge AI treats prompt-to-app generation as a compilation problem. It enforces a strict 5-stage pipeline, utilizing intermediate representations (IR), cross-layer validation, and deterministic repair loops.

## 🚀 Current Architecture & Features

- 🧠 **Cerebras Primary LLM Engine**: Leverages lightning-fast inference on `llama3.1-8b` via Cerebras, with automatic fallback to Groq (`llama-3.3-70b-versatile`) and OpenAI (`gpt-4o-mini`).
- 🛡️ **5-Stage Sequential Pipeline**:
  1. **Intent Extraction**: NL → IntentIR
  2. **System Design**: IntentIR → SystemDesignIR
  3. **Sequential Schema Generation**: SystemDesignIR → DB, API, UI, Auth (Sequential execution to respect TPM limits).
  4. **Validation + Repair Loop**: Cross-layer validation and LLM-assisted repair (max 3 loops).
  5. **Boot Repair Engine**: Packager that automatically repairs structural discrepancies and normalizes JSON structures.
- 🎨 **Modern Animated Dashboard**: Premium dark-themed UI built with Next.js, Framer Motion, and TailwindCSS. Features persistent compile history, interactive reload, real-time health checks, and animated metrics.
- 🔒 **Railway Deployment Ready**: Native `Procfile` and `railway.toml` support for seamless deployment on Railway. Features a hard **55-second pipeline timeout** to prevent proxy gateway timeouts.
- 💸 **Token Budget Enforcement**: Built-in limits, sleep buffers, and JSON repair logic for truncated responses to prevent failing on free-tier limits.

## 🛠 Tech Stack

| Layer | Technology | Details |
|---|---|---|
| **API Framework** | FastAPI | High-performance async backend execution. |
| **Validation Engine**| Pydantic v2 | Extremely strict, typed schema validation. |
| **Frontend** | Next.js 14 | React framework for UI rendering. |
| **Styling & Motion** | Tailwind CSS + Framer Motion | Glassmorphism, animated statuses, rich metrics. |
| **LLM Provider** | Cerebras (Primary) / Groq / OpenAI | Fast, cost-tracked token generation. |
| **Database** | SQLite + SQLAlchemy | Synchronous persistence layer. |

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- [Cerebras API Key](https://cerebras.net/) (Primary)
- [Groq API Key](https://console.groq.com/) (Fallback)

### Backend Setup
```bash
git clone https://github.com/HrshJha/AppForge-AI.git
cd AppForge-AI/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
Add your API keys to `.env`:
```env
LLM_PROVIDER="groq" # Ignored if Cerebras key is present
CEREBRAS_API_KEY="your-cerebras-key"
GROQ_API_KEY="your-groq-key"
DATABASE_URL="sqlite:///./appforge.db"
```

Start the backend:
```bash
uvicorn app.main:app --port 8000 --reload
```

### Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```

## 🧪 Usage

### Core API Endpoints

- `GET /api/v1/health` - Check service status.
- `POST /api/v1/generate` - Execute the full 5-stage pipeline.
- `POST /api/v1/validate` - Validate existing schemas against cross-layer rules.
- `POST /api/v1/repair` - Trigger the surgical LLM repair loop.
- `GET /api/v1/metrics` - Fetch real-time animated pipeline metrics.

### Configuration Variables (.env)
- `CEREBRAS_API_KEY`: Primary LLM integration
- `GROQ_API_KEY`: Fallback LLM integration
- `PIPELINE_TIMEOUT_SECONDS`: Hardcoded internally to 55s to accommodate Railway's edge timeouts.
- `AMBIGUITY_THRESHOLD`: Defaults to 0.6. Prompts with a higher ambiguity score are rejected.

## 📦 Deployment (Railway)
AppForge AI is optimized for Railway deployment. Vercel deployment configurations have been deprecated/removed.
1. Connect your GitHub repository to Railway.
2. The provided `railway.toml` and `Procfile` will automatically provision and build the backend.
3. Ensure backend environment variables (API keys) are set in the Railway dashboard.

## 🤝 Contributing
Contributions are welcome. All new logic must strictly adhere to Pydantic v2 schemas and the 5-stage deterministic pattern. Ensure the test suite (39+ tests) passes locally before submitting a PR.

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

<div align="center">
**Made with 💖 by Harsh Kumar Jha**
</div>
