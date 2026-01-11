# RFP-AI Analyzer: Universal Dynamic RAG Engine 🚀

A high-fidelity, dual-LLM powered analysis platform designed to automate the evaluation of Request for Proposals (RFPs) against company performance data. This system utilizes a "Neural Data Pipeline" to provide semantic matching, industry-agnostic requirement extraction, and professional compliance reporting.

## 🧠 Neural Architecture

The platform is powered by a **Double-Lock Intelligence System**:

### 1. Dual-LLM Strategy
- **Primary Brain**: **Google Gemini 1.5 Pro** — Leverages massive context windows for deep semantic matching across 100+ page documents.
- **Failover Logic**: **Mistral Large** — Automatically takes over in case of API latency or rate limits, ensuring 100% uptime for analysis.

### 2. Universal Dynamic RAG
- **Zero-Trust Extraction**: No hardcoded checklists. The AI dynamically scans the RFP to identify "High Importance" requirements specific to the industry (IT, Staffing, Construction, etc.).
- **Score Guard Fail-Safe**: A backend verification layer in FastAPI that enforces a strict **45% disqualification cap** if mandatory items are missing, while guaranteeing a **70% safety floor** for eligible, compliant documents.

---

## 🛠️ Technical Stack

- **Frontend**: React (Vite), Tailwind CSS, Framer Motion (Animations), html2canvas/jspdf (Export).
- **Backend**: FastAPI (Python), Uvicorn, PyPDF2/python-docx (File Processing).
- **AI/RAG**: Google Generative AI SDK, Mistral AI SDK, Custom Neural Prompt Orchestration.

---

## 📁 Directory Structure

```text
RFP-AI-Analyzer/
├── backend/
│   ├── main.py             # FastAPI App & Universal Score Guard
│   ├── llm_utils.py        # Gemini/Mistral Dual-LLM Pipeline
│   ├── data_utils.py       # File Parsing & Text Extraction
│   ├── .env                # API Keys (Gemini & Mistral)
│   ├── requirements.txt    # Backend Dependencies
│   └── company_profile.json # Static Company Fallback Context
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Application Root & UI Logic
│   │   ├── components/
│   │   │   └── Dashboard.jsx # High-Fidelity Insights & Match Index
│   │   └── index.css       # Neon-Corporate Design System
│   ├── index.html          # Entry Point
│   ├── package.json        # Frontend Dependencies
│   ├── tailwind.config.js  # UI Styling Configuration
│   └── vite.config.js      # Build Configuration
└── README.md               # Project Documentation
```

---

## 🚀 Getting Started

### Backend Setup
1. Navigate to `/backend`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure `.env` with `GEMINI_API_KEY` and `MISTRAL_API_KEY`.
4. Start the server: `python -m uvicorn main:app --reload`.

### Frontend Setup
1. Navigate to `/frontend`.
2. Install dependencies: `npm install`.
3. Launch the dashboard: `npm run dev`.

---

## 🎯 Key Features
- **Dynamic Percentage Gauge**: Real-time visual feedback of match hierarchy.
- **Neural Insights**: Bulleted strengths (Winnable Factors) and risks (Risk Vertices).
- **Compliance Matrix**: Industry-agnostic verification of extracted requirements.
- **Vibrant UI**: Neon-corporate aesthetic with premium glassmorphism.
- **Neural PDF Export**: Professional report generation directly from the UI.

---

## 🌩️ Vercel Deployment Guide (Beginner Friendly)

Since this project is a Monorepo (both Frontend and Backend), follow these steps to deploy it for free on Vercel:

### 1. Push to GitHub
- Initialize a git repo in the project root: `git init`.
- Commit your code: `git add . && git commit -m "Vercel ready"`.
- Push to a new GitHub repository.

### 2. Connect to Vercel
- Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
- Import your **RFP-AI-Analyzer** repository.

### 3. Configure Project Settings
- **Framework Preset**: Other (Our `vercel.json` handles the heavy lifting).
- **Build Command**: `cd frontend && npm install && npm run build`.
- **Output Directory**: `frontend/dist`.
- **Install Command**: `npm install`.

### 4. Set Environment Variables
In the Vercel dashboard, go to **Settings > Environment Variables** and add:
- `GEMINI_API_KEY`: Your Google Gemini key.
- `MISTRAL_API_KEY`: Your Mistral AI key.

### 5. Deploy!
- Click **"Deploy"**. Vercel will build the frontend and host the Python backend as serverless functions.
- Once finished, you will get a production URL (e.g., `rfp-ai-analyzer.vercel.app`).
