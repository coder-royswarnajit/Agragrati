<p align="center">
 <img src="frontend/public/icons/icon-192x192.png" alt="Agragrati Logo" width="120" height="120" />
</p>

<h1 align="center"> Agragrati</h1>

<p align="center">
 <strong>AI-Powered Resume Analysis & Job Search Platform</strong>
</p>

<p align="center">
 <a href="#features">Features</a> •
 <a href="#demo">Demo</a> •
 <a href="#quick-start">Quick Start</a> •
 <a href="#deployment">Deployment</a> •
 <a href="#api-keys">API Keys</a>
</p>

 <img src="https://img.shields.io/badge/React-18.3-blue?logo=react" alt="React" />
 <img src="https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi" alt="FastAPI" />
 <img src="https://img.shields.io/badge/TypeScript-5.8-blue?logo=typescript" alt="TypeScript" />
 <img src="https://img.shields.io/badge/Tailwind-3.4-cyan?logo=tailwindcss" alt="Tailwind" />
 <img src="https://img.shields.io/badge/Groq-Llama%203.3-orange" alt="Groq AI" />
 <img src="https://img.shields.io/badge/Framer%20Motion-11-purple?logo=framer" alt="Framer Motion" />
 <br/>
 <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white" alt="Python" />
 <img src="https://img.shields.io/badge/Vite-5.0-646CFF?logo=vite&logoColor=white" alt="Vite" />
 <img src="https://img.shields.io/badge/Supabase-Database-3ECF8E?logo=supabase&logoColor=white" alt="Supabase" />
 <img src="https://img.shields.io/badge/Zustand-State-orange" alt="Zustand" />
 <img src="https://img.shields.io/badge/shadcn%2Fui-Components-000000" alt="shadcn/ui" />
 <img src="https://img.shields.io/badge/Vercel-Deployment-000000?logo=vercel&logoColor=white" alt="Vercel" />
 <img src="https://img.shields.io/badge/Docker-Container-2496ED?logo=docker&logoColor=white" alt="Docker" />
</p>

---

## Features

### Resume Analysis
Upload your resume (PDF/TXT) and get comprehensive AI-powered feedback including:
- ATS compatibility scoring
- Skills extraction and evaluation
- Actionable improvement suggestions
- Target role identification

### Smart Job Search
- **AI-Powered Search**: Automatically extracts skills from your resume to find matching jobs
- **Manual Search**: Traditional keyword-based job search
- Real job listings from JSearch & Adzuna APIs
- Filter by company, source, job type
- Export results to CSV
- Bookmark jobs for later

### Career Insights (6 AI Tools)
| Tool | Description |
|------|-------------|
| **Career Paths** | Discover potential career trajectories based on your experience |
| **Skill Gaps** | Identify skills to develop for your target role |
| **Salary Insights** | Understand your market value with data-backed estimates |
| **Interview Prep** | Get personalized interview preparation strategies |
| **Learning Resources** | Curated courses, certifications, and books |
| **Industry Trends** | Market outlook and emerging opportunities |

### Job Match Score
- Compare your resume against specific job descriptions
- Detailed keyword matching analysis
- Skills breakdown (technical & soft skills)
- ATS optimization tips
- Cover letter talking points

### Cover Letter Generator
- AI-generated personalized cover letters
- Multiple tone options (professional, enthusiastic, formal)
- Uses your uploaded resume for context
- Copy to clipboard or download as text

### Interview Practice
- AI-generated interview questions tailored to your background
- Practice with real-time response evaluation
- Scoring and improvement tips
- Multiple question categories

### Application Tracker
Track all your job applications with:
- Status management (Saved → Applied → Interviewing → Offered)
- Timeline and notes
- Supabase database integration
- Search and filter capabilities

### Resume Builder
- Create professional resumes from scratch
- AI-enhanced section writing
- Drag-and-drop section ordering
- Download completed resume

### Modern UI/UX
- **Framer Motion animations** throughout
- Dark/Light/System theme support
- Responsive mobile-first design
- Keyboard shortcuts (press `?` for help)
- PWA support - install as desktop/mobile app

---



## Project Structure

```
Agragrati/
├── frontend/         # React frontend
│  ├── src/
│  │  ├── pages/      # 10 page components
│  │  ├── components/   # UI components + layout
│  │  ├── hooks/      # Custom hooks (theme, PWA, shortcuts)
│  │  ├── lib/       # API, Supabase, utilities, animations
│  │  └── store/      # Zustand state management
│  ├── public/       # PWA assets (manifest, icons, sw.js)
│  ├── vercel.json     # Vercel deployment config
│  └── package.json
│
├── backend/         # FastAPI backend
│  ├── main.py       # API server (16+ endpoints)
│  ├── requirements.txt   # Python dependencies
│  ├── vercel.json     # Vercel serverless config
│  └── Dockerfile      # Docker deployment
│
├── job_search.py      # Core AI & job search logic
├── supabase_setup.sql    # Database schema
├── docker-compose.yml    # Docker multi-container setup
├── .env.example       # Environment variables template
└── README.md        # This file
```

---

## Quick Start

### Prerequisites
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Python 3.11+** - [Download](https://python.org/)
- **Groq API Key** (required) - [Get free key](https://console.groq.com/keys)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/agragrati.git
cd agragrati
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env
# Edit .env and add your GROQ_API_KEY

# Start backend server
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 3. Frontend Setup

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
# Default settings work for local development

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

### 4. Quick Start (Windows)

Double-click `start.bat` or run:
```powershell
.\start.ps1
```

---

## API Keys

### Required

| API | Purpose | Get Key |
|-----|---------|---------|
| **Groq** | Powers all AI features | [console.groq.com/keys](https://console.groq.com/keys) |

### Optional (Enhanced Features)

| API | Purpose | Get Key | Free Tier |
|-----|---------|---------|-----------|
| **RapidAPI (JSearch)** | Primary job listings | [rapidapi.com/jsearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) | 500 req/month |
| **Adzuna** | Secondary job listings | [developer.adzuna.com](https://developer.adzuna.com/) | 5,000 req/month |
| **Supabase** | Database for bookmarks | [supabase.com](https://supabase.com) | 500MB storage |

---

## Deployment

### Deploy to Vercel (Recommended)

#### Frontend Deployment

1. **Push to GitHub**
  ```bash
  git init
  git add .
  git commit -m "Initial commit"
  git remote add origin https://github.com/yourusername/agragrati.git
  git push -u origin main
  ```

2. **Import to Vercel**
  - Go to [vercel.com/new](https://vercel.com/new)
  - Import your GitHub repository
  - Set **Root Directory** to `frontend`
  - Framework will be auto-detected as Vite

3. **Configure Environment Variables**
  In Vercel Project Settings → Environment Variables:
  ```
  VITE_API_URL=https://your-backend-url.vercel.app
  VITE_SUPABASE_URL=your_supabase_url (optional)
  VITE_SUPABASE_ANON_KEY=your_supabase_key (optional)
  ```

4. **Deploy**
  - Click Deploy
  - Your frontend will be live at `https://your-project.vercel.app`

#### Backend Deployment (Vercel Serverless)

1. **Create new Vercel project for backend**
  - Import same repository
  - Set **Root Directory** to `backend`

2. **Configure Environment Variables**
  ```
  GROQ_API_KEY=your_groq_key
  RAPIDAPI_KEY=your_rapidapi_key (optional)
  ADZUNA_APP_ID=your_adzuna_id (optional)
  ADZUNA_APP_KEY=your_adzuna_key (optional)
  FRONTEND_URL=https://your-frontend.vercel.app
  ```

3. **Deploy**
  - Backend will be live at `https://your-api.vercel.app`
  - Update frontend's `VITE_API_URL` with this URL

#### Alternative: Deploy Backend to Render

1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Configure:
  - **Root Directory**: `backend`
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

### Deploy with Docker

```bash
# Build and start both services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

## Database Setup (Supabase)

Optional but recommended for persisting bookmarks and applications.

1. **Create Supabase Project**
  - Go to [supabase.com](https://supabase.com)
  - Create new project

2. **Run Database Schema**
  - Go to SQL Editor in Supabase dashboard
  - Paste contents of `supabase_setup.sql`
  - Click Run

3. **Get API Credentials**
  - Go to Project Settings → API
  - Copy **Project URL** and **anon public** key

4. **Configure Frontend**
  Add to `frontend/.env.local`:
  ```env
  VITE_SUPABASE_URL=https://yourproject.supabase.co
  VITE_SUPABASE_ANON_KEY=your_anon_key
  ```

---

## Keyboard Shortcuts

Press `?` in the app to see all shortcuts.

| Shortcut | Action |
|----------|--------|
| `?` | Show shortcuts help |
| `Alt + H` | Go to Home |
| `Alt + R` | Go to Resume Analysis |
| `Alt + J` | Go to Job Search |
| `Alt + M` | Go to Job Match |
| `Alt + C` | Go to Career Insights |
| `Alt + L` | Go to Cover Letter |
| `Alt + I` | Go to Interview Prep |
| `Alt + B` | Go to Bookmarks |
| `Alt + A` | Go to Applications |
| `Ctrl + /` | Focus search |
| `Escape` | Close modal |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/upload-resume` | POST | Upload PDF/TXT resume |
| `/analyze-resume` | POST | AI resume analysis |
| `/search-jobs` | POST | Manual job search |
| `/search-jobs-by-resume` | POST | AI-powered job search |
| `/career-insights/paths` | POST | Career path analysis |
| `/career-insights/skill-gaps` | POST | Skill gap analysis |
| `/career-insights/salary` | POST | Salary insights |
| `/career-insights/interview-prep` | POST | Interview preparation |
| `/career-insights/learning` | POST | Learning recommendations |
| `/career-insights/industry` | POST | Industry trends |
| `/job-match` | POST | Resume-job matching |
| `/generate-cover-letter` | POST | AI cover letter |
| `/interview-questions` | POST | Generate questions |
| `/evaluate-answer` | POST | Evaluate interview response |
| `/enhance-resume-section` | POST | AI-enhance resume section |

Full API documentation: `http://localhost:8000/docs`

---

## PWA Support

Agragrati can be installed as a Progressive Web App:

- **Chrome/Edge Desktop**: Click install icon in address bar
- **Mobile**: "Add to Home Screen" from browser menu

Features:
- Works offline (cached pages)
- App shortcuts for quick access
- Native app-like experience
- Automatic updates

---

## Theming

Three theme options available via the sun/moon icon:

- **Dark Mode** (default) - Easy on the eyes
- **Light Mode** - For bright environments 
- **System Mode** - Follows OS preference

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
 <strong>Agragrati</strong> - AI-Powered Career Platform
 <br/>
 Made with ❤️ for job seekers everywhere
 <br/><br/>
 Powered by <a href="https://groq.com">Groq AI</a> • <a href="https://react.dev">React</a> • <a href="https://fastapi.tiangolo.com">FastAPI</a>
</p>
