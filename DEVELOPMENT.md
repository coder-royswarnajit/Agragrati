# Local Development Guide

This guide covers setting up Agragrati for local development with hot reloading, debugging, and best practices.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Running the Application](#running-the-application)
4. [Development Workflow](#development-workflow)
5. [Project Architecture](#project-architecture)
6. [Adding New Features](#adding-new-features)
7. [Testing](#testing)
8. [Debugging](#debugging)
9. [Code Style](#code-style)

---

## Prerequisites

### Required Software

| Software | Version | Download |
|----------|---------|----------|
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| Python | 3.11+ | [python.org](https://python.org/) |
| Git | Latest | [git-scm.com](https://git-scm.com/) |
| VS Code | Latest | [code.visualstudio.com](https://code.visualstudio.com/) |

### Recommended VS Code Extensions

```json
{
 "recommendations": [
  "ms-python.python",
  "ms-python.vscode-pylance",
  "dbaeumer.vscode-eslint",
  "esbenp.prettier-vscode",
  "bradlc.vscode-tailwindcss",
  "formulahendry.auto-rename-tag",
  "christian-kohler.path-intellisense"
 ]
}
```

---

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/agragrati.git
cd agragrati
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp ../.env.example .env

# Edit .env with your API keys
# At minimum, add GROQ_API_KEY
```

### 3. Frontend Setup

```bash
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Default values work for local development
```

### 4. Verify Setup

```bash
# Backend - should start without errors
cd backend
uvicorn main:app --reload --port 8000

# Frontend - in new terminal
cd frontend
npm run dev
```

---

## Running the Application

### Option 1: Separate Terminals (Recommended for Development)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate # or venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Option 2: Using Start Scripts (Windows)

```powershell
# From project root
.\start.ps1
# or double-click start.bat
```

### Option 3: Docker (Production-like)

```bash
docker-compose up --build
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | React application |
| Backend | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |

---

## Development Workflow

### Hot Reloading

Both frontend and backend support hot reloading:

- **Frontend**: Vite HMR - changes reflect instantly
- **Backend**: Uvicorn `--reload` - restarts on file changes

### Making Changes

1. **Frontend Changes**:
  - Edit files in `frontend/src/`
  - Browser updates automatically
  - Check browser console for errors

2. **Backend Changes**:
  - Edit files in `backend/`
  - Server restarts automatically
  - Check terminal for errors

3. **API Changes**:
  - Update endpoint in `backend/main.py`
  - Update client in `frontend/src/lib/api.ts`
  - Update types if needed

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: add my feature"

# Push and create PR
git push origin feature/my-feature
```

---

## Project Architecture

### Frontend Architecture

```
frontend/src/
├── pages/         # Page components (routes)
│  ├── Index.tsx     # Home page
│  ├── ResumeAnalysis.tsx
│  ├── JobSearch.tsx
│  ├── Bookmarks.tsx
│  ├── Applications.tsx
│  ├── CoverLetter.tsx
│  ├── InterviewPrep.tsx
│  ├── CareerInsights.tsx
│  ├── JobMatch.tsx
│  ├── ResumeBuilder.tsx
│  └── NotFound.tsx
│
├── components/
│  ├── layout/      # Layout components
│  │  ├── Layout.tsx  # Main layout wrapper
│  │  ├── Header.tsx  # Navigation header
│  │  ├── Footer.tsx
│  │  └── MobileNav.tsx
│  └── ui/        # shadcn/ui components
│
├── hooks/        # Custom React hooks
│  ├── useTheme.ts
│  ├── usePWA.ts
│  └── useKeyboardShortcuts.ts
│
├── lib/         # Utilities
│  ├── api.ts      # Backend API client
│  ├── supabase.ts   # Supabase client
│  ├── utils.ts     # Helper functions
│  └── animations.ts  # Framer Motion variants
│
├── store/        # Zustand state
│  └── useStore.ts
│
└── types/        # TypeScript types
  └── index.ts
```

### Backend Architecture

```
backend/
├── main.py       # FastAPI application
│            # - Routes and endpoints
│            # - Request/Response models
│            # - CORS configuration
│
└── requirements.txt   # Python dependencies

# Parent directory
job_search.py      # Core AI and job search logic
            # - JobSearcher class
            # - API integrations
            # - AI prompts
```

### State Management

**Frontend (Zustand)**:
```typescript
// frontend/src/store/useStore.ts
interface AppState {
 resumeText: string;
 targetRole: string;
 analysisResult: string;
 // ... actions
}
```

**Persistence**: Zustand with `persist` middleware saves to localStorage

### API Communication

```typescript
// frontend/src/lib/api.ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const analyzeResume = async (text: string): Promise<AnalysisResponse> => {
 const response = await fetch(`${API_URL}/analyze-resume`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ resume_text: text }),
 });
 return response.json();
};
```

---

## Adding New Features

### Adding a New Page

1. **Create page component**:
  ```typescript
  // frontend/src/pages/NewPage.tsx
  import { Layout } from "@/components/layout/Layout";
  import { motion } from "framer-motion";
  import { fadeInUp, staggerContainer } from "@/lib/animations";

  const NewPage = () => {
   return (
    <Layout>
     <motion.div
      variants={staggerContainer}
      initial="initial"
      animate="animate"
      className="container py-8"
     >
      <motion.h1 variants={fadeInUp} className="text-3xl font-bold">
       New Page
      </motion.h1>
     </motion.div>
    </Layout>
   );
  };

  export default NewPage;
  ```

2. **Add route**:
  ```typescript
  // frontend/src/App.tsx
  import NewPage from "./pages/NewPage";
  
  // In routes
  <Route path="/new-page" element={<NewPage />} />
  ```

3. **Add navigation** (optional):
  ```typescript
  // frontend/src/components/layout/Header.tsx
  { name: "New Page", path: "/new-page", icon: NewIcon }
  ```

### Adding a New API Endpoint

1. **Add to backend**:
  ```python
  # backend/main.py
  class NewRequest(BaseModel):
    data: str

  @app.post("/new-endpoint")
  async def new_endpoint(request: NewRequest):
    # Process request
    result = process_data(request.data)
    return {"result": result}
  ```

2. **Add to frontend API client**:
  ```typescript
  // frontend/src/lib/api.ts
  export interface NewResponse {
   result: string;
  }

  export const newEndpoint = async (data: string): Promise<NewResponse> => {
   const response = await fetch(`${API_URL}/new-endpoint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data }),
   });
   if (!response.ok) throw new Error('Request failed');
   return response.json();
  };
  ```

### Adding a UI Component

Use shadcn/ui CLI:

```bash
cd frontend
npx shadcn@latest add [component-name]

# Examples:
npx shadcn@latest add alert
npx shadcn@latest add calendar
npx shadcn@latest add dropdown-menu
```

---

## Testing

### Manual Testing Checklist

- [ ] Resume upload (PDF and TXT)
- [ ] Resume analysis completes
- [ ] Job search returns results
- [ ] Smart search extracts skills
- [ ] Career insights load
- [ ] Cover letter generates
- [ ] Interview questions generate
- [ ] Job match calculates score
- [ ] Bookmarks save/delete
- [ ] Applications CRUD works
- [ ] Theme toggle works
- [ ] Mobile responsive
- [ ] Keyboard shortcuts work

### API Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Upload resume
curl -X POST http://localhost:8000/upload-resume \
 -F "file=@resume.pdf"

# Analyze resume
curl -X POST http://localhost:8000/analyze-resume \
 -H "Content-Type: application/json" \
 -d '{"resume_text": "Your resume text here"}'

# Job search
curl -X POST http://localhost:8000/search-jobs \
 -H "Content-Type: application/json" \
 -d '{"search_term": "software engineer", "location": "San Francisco"}'
```

---

## Debugging

### Frontend Debugging

1. **Browser DevTools**:
  - Console for errors
  - Network tab for API calls
  - React DevTools for component state

2. **VS Code Debugging**:
  ```json
  // .vscode/launch.json
  {
   "version": "0.2.0",
   "configurations": [
    {
     "type": "chrome",
     "request": "launch",
     "name": "Debug Frontend",
     "url": "http://localhost:5173",
     "webRoot": "${workspaceFolder}/frontend/src"
    }
   ]
  }
  ```

### Backend Debugging

1. **Add print statements**:
  ```python
  print(f"DEBUG: {variable}")
  ```

2. **VS Code Debugging**:
  ```json
  {
   "version": "0.2.0",
   "configurations": [
    {
     "name": "Debug Backend",
     "type": "debugpy",
     "request": "launch",
     "module": "uvicorn",
     "args": ["main:app", "--reload", "--port", "8000"],
     "cwd": "${workspaceFolder}/backend"
    }
   ]
  }
  ```

3. **API Logs**: Check terminal running uvicorn

### Common Issues

**CORS Errors**:
- Ensure backend is running
- Check FRONTEND_URL in backend .env
- Clear browser cache

**API Timeouts**:
- Check network connection
- Verify API keys are valid
- Check rate limits

**Build Errors**:
- Clear node_modules and reinstall
- Check TypeScript errors
- Verify import paths

---

## Code Style

### TypeScript/React

- Use functional components with hooks
- Use TypeScript for all new code
- Follow ESLint rules
- Use Tailwind for styling
- Add Framer Motion animations

### Python

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Use Pydantic models for validation

### Commit Messages

Follow conventional commits:

```
feat: add new feature
fix: fix bug
docs: update documentation
style: formatting changes
refactor: code refactoring
test: add tests
chore: maintenance tasks
```

---

## Quick Reference

### Common Commands

```bash
# Frontend
npm run dev     # Start dev server
npm run build    # Production build
npm run lint     # Run linter
npm run preview   # Preview build

# Backend
uvicorn main:app --reload  # Start with hot reload
pip freeze > requirements.txt # Update deps

# Docker
docker-compose up --build  # Build and start
docker-compose down     # Stop
docker-compose logs -f    # View logs
```

### File Locations

| What | Where |
|------|-------|
| API Client | `frontend/src/lib/api.ts` |
| Routes | `frontend/src/App.tsx` |
| State | `frontend/src/store/useStore.ts` |
| Animations | `frontend/src/lib/animations.ts` |
| Backend Routes | `backend/main.py` |
| AI Logic | `job_search.py` |
| DB Schema | `supabase_setup.sql` |
