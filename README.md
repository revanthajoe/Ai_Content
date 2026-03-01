# Content DNA OS

## Evolutionary AI Operating System for Digital Content

Content DNA OS treats digital content as a **living organism**, not a static post. It extracts content DNA, generates mutations across 6 structural strategies, scores them via a fitness function, rejects repetitive variants through a similarity guard, and selects the strongest evolutionary candidate.

---

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    Content DNA OS                          │
├──────────────┬──────────────────┬─────────────────────────┤
│  Intelligence│   Evolution      │   Visualization          │
│  Layer       │   Layer          │   Layer                  │
├──────────────┼──────────────────┼─────────────────────────┤
│ DNA Extractor│ Multi-branch     │ Create Page              │
│ Mutation Eng │ Fitness selection│ Evolution Lab            │
│ Fitness Scorer Lineage tracking │ DNA Viewer               │
│ Similarity   │ Strategy tagging │ Fitness Charts           │
│ Guard        │ Drift analysis   │ DNA Drift Viz            │
└──────────────┴──────────────────┴─────────────────────────┘
```

## Quick Start

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up --build
```

**Backend:** http://localhost:8000  
**Frontend:** http://localhost:3000  
**API Docs:** http://localhost:8000/docs

---

## Mutation Strategies

| Strategy | Description |
|---|---|
| **Hook Amplification** | Bold, attention-grabbing opening lead |
| **Angle Shift** | Contrarian or alternative perspective |
| **Story Reframe** | Narrative arc (setup → conflict → resolution) |
| **Counterpoint Injection** | Devil's advocate tension + resolution |
| **Summary Distillation** | Essential core insight, stripped of fluff |
| **Platform Formatting** | Platform-optimized layout with emoji anchors |

## Fitness Function

Multi-dimensional scoring across:
- Length normalization
- Structural clarity
- Intent alignment
- Strategy diversity
- Novelty bonus
- Repetition penalty
- Similarity penalty

## Anti-Repetition Guard

- SequenceMatcher similarity threshold (65%)
- Used-text tracking across generations
- Strategy reuse prevention
- Hook/CTA deduplication
- Content cleaning pipeline

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/evolve` | Single content evolution |
| POST | `/api/evolve/lab` | Multi-generation evolution lab |
| POST | `/api/dna/extract` | Extract DNA profile |
| POST | `/api/fitness/score` | Compute fitness score |
| GET | `/api/strategies` | List mutation strategies |
| GET | `/api/platforms` | List supported platforms |

## AWS Deployment

```bash
cd infrastructure
chmod +x deploy.sh
./deploy.sh
```

**Services used:**
- Amazon Bedrock (Claude 3 Sonnet)
- AWS Lambda (mutation orchestration)
- Amazon DynamoDB (DNA storage + lineage)
- Amazon Titan Embeddings (semantic similarity)
- S3 (archival storage)

## Project Structure

```
DNA OS/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── models.py           # Pydantic data models
│   │   │   ├── dna_extractor.py    # DNA extraction engine
│   │   │   ├── mutation_engine.py  # 6 mutation strategies
│   │   │   ├── fitness_scorer.py   # Multi-dim fitness scoring
│   │   │   ├── similarity_guard.py # Anti-repetition layer
│   │   │   └── evolution_manager.py# Orchestrator
│   │   ├── api/
│   │   │   └── routes.py           # FastAPI endpoints
│   │   ├── aws/
│   │   │   ├── bedrock_client.py   # Claude 3 integration
│   │   │   ├── dynamo_client.py    # DynamoDB client
│   │   │   └── titan_embeddings.py # Titan embeddings
│   │   └── main.py                 # FastAPI app
│   ├── lambda_handler.py           # AWS Lambda entry
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LandingPage.jsx     # Hero + feature overview
│   │   │   ├── CreatePage.jsx      # Single evolution page
│   │   │   ├── EvolutionLab.jsx    # Multi-gen lab
│   │   │   ├── DNAViewer.jsx       # DNA analysis
│   │   │   ├── EvolutionTree.jsx   # Tree visualization
│   │   │   ├── FitnessChart.jsx    # Fitness over generations
│   │   │   ├── DNADrift.jsx        # Drift analysis
│   │   │   └── ...
│   │   └── api/
│   │       └── client.js           # API client
│   └── package.json
├── infrastructure/
│   ├── template.yaml               # AWS SAM template
│   └── deploy.sh                   # Deployment script
├── docker-compose.yml
└── README.md
```

## License

MIT
