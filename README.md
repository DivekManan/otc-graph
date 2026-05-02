# Order-to-Cash Graph Explorer

A graph-based data intelligence system for SAP Order-to-Cash data.

## Live Demo
- Frontend: [Vercel URL]
- Backend: [Render URL]

## Architecture
- **Frontend**: React + Vis.js (graph visualization)
- **Backend**: FastAPI + SQLite
- **LLM**: Google Gemini (natural language → SQL)
- **Graph**: NetworkX

## Run Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
python seed_data.py
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## LLM Prompting Strategy
- Schema injection: full table schema sent with every query
- Two-step pipeline: SQL generation → natural language answer
- Domain guardrails: keyword filtering rejects off-topic prompts

## Database Choice
SQLite — zero config, file-based, portable for demo purposes.
Schema mirrors SAP OTC: customers → sales_orders → deliveries → billing → payments → journal_entries
