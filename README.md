
<p align="center">
  <img src="assets/sententia_logo.png" alt="Sententia Logo" width="200"/>
</p>


📚 Sententia Core – Intelligent Requirements Management System
🧠 About Sententia
Sententia (Latin): "thought," "opinion," or "judgment."

Sententia Core is an intelligent, modular platform for mastering requirements engineering. It is designed to amplify the capabilities of software teams by making the full lifecycle of requirements — from elicitation, through validation, to documentation — dynamic, intelligent, and continuously improvable.

Built with simplicity at the core and designed for future AI-assistance integration, Sententia Core lets you start small and scale confidently.


[![Build](https://img.shields.io/github/actions/workflow/status/your-org/sententia-core/ci.yml?style=flat-square)](https://github.com/your-org/sententia-core/actions)
![Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green?style=flat-square)
![Built with Llama 4](https://img.shields.io/badge/built%20with-Llama%204-blueviolet?style=flat-square)


🛠️ Project Overview
This project includes:

🚀 FastAPI backend for requirements management (CRUD + Metadata APIs)

🎨 Streamlit frontend UI for easy interaction

🐳 Docker Compose for full local orchestration (app + UI + tests)

🧪 Pytest-based backend tests to ensure API reliability

🛡️ Enum-backed dynamic dropdowns for strict field validation

> Sententia turns dense source documents into clean, testable requirements and keeps them living, traceable, and export-ready throughout the build lifecycle.

---

## 🏗️ What’s Ready Today — a Real, Usable RM MVP (Zero AI Required)

| Module | Status | Why it matters |
|--------|--------|----------------|
| **FastAPI Requirements API** | ✅ CRUD & metadata routes with Swagger docs | Teams can start capturing requirements right now, no AI setup needed. |
| **Streamlit Front-End** | ✅ Browse, edit, and live-render SRD/SRS via `render_doc()` | Non-technical stakeholders don’t touch curl/Postman. |
| **Typed Data Model** | ✅ Pydantic schemes & enum validation | Every requirement has a stable ID & type — traceability ready. |
| **Export Engine** | ✅ Jinja2 → Markdown → DOCX/PDF/XLSX | One-click auditor-grade docs. |
| **Automated Tests & Docker Compose** | ✅ CI-green; one-liner `up --build` spin-up | Confidence to hack fast without breaking the core. |

**TL;DR—clone, `docker compose up`, and you have a functioning requirements-management tool today.**

---

## 🚀 AI-Enabled Roadmap (Hackathon Focus + Q3 Milestones)

| Milestone | Llama-Powered Magic | ETA |
|-----------|---------------------|-----|
| **SpecWiz Discovery Module** | Upload a 200-page PDF → Business-Model Canvas + Kano-ranked backlog in 90 s (Llama 4 Maverick 1 M-ctx). | **NYC Llama Hackathon demo** |
| **Ask-the-Spec Chat** | RAG over the uploaded doc; hybrid routing (GPT-4o mini for maths, Scout for fast chat). | +1 week |
| **Auto Trace Matrix** | Agent links SRD ↔ SRS ↔ pytest IDs, exports to Excel. | Q3-2025 |
| **Impact × Effort Re-prioritiser** | WSJF / RICE recalculated live as you toggle scope. | Q3-2025 |
| **Enterprise SaaS Console** | Usage analytics, RBAC, provider billing. | Q4-2025 |

The AI layer is **provider-agnostic**: switch OpenRouter ↔ Groq ↔ local vLLM by editing `config.yaml`.

---

## 🌐 Architecture

```txt
Browser
 │ Upload PDF
▼
Streamlit GUI ──► SpecWiz Agents (Llama 4) ──► Pydantic Context
                                         │
FastAPI API ◀─────────────────────────────┘
 │
└─▶ Jinja2 Render → SRD.md / backlog.xlsx / C4.svg
```

⚡ Quick Start (2 min)
```console
git clone https://github.com/your-org/sententia-core.git
cd sententia-core
docker compose up --build

# Browse
open http://localhost:8000/docs   # FastAPI Swagger
open http://localhost:8501        # Streamlit UI
```
🛠️ Dev Commands
| Task           | Command                                     |
| -------------- | ------------------------------------------- |
| Run stack      | `docker compose up --build`                 |
| Back-end tests | `docker compose run --rm tests`             |
| Force rebuild  | `docker compose build --no-cache app tests` |
| Logs           | `docker compose logs -f app`                |

📜 Licensing Model
| Part                                                                    | License                                                          | Rationale                                                                       |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **Sententia Core (this repo)**                                          | **Apache 2.0**                                                   | Max adoption & hackathon openness.                                              |
Maintainer: Chris Senanayake

“Better software starts with better questions.” — Sententia
