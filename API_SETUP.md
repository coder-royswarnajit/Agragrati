# API Configuration Guide

This guide explains how to obtain and configure all the API keys used by Agragrati.

---

## Table of Contents

1. [Groq API (Required)](#groq-api-required)
2. [RapidAPI / JSearch (Optional)](#rapidapi--jsearch-optional)
3. [Adzuna API (Optional)](#adzuna-api-optional)
4. [Supabase (Optional)](#supabase-optional)
5. [Configuration Files](#configuration-files)

---

## Groq API (Required)

**Purpose**: Powers all AI features including resume analysis, career insights, interview prep, and cover letter generation.

**Model Used**: Llama 3.3 70B Versatile

**Free Tier**: 30 requests/minute, 6,000 requests/day

### Steps to Get API Key

1. Go to [console.groq.com](https://console.groq.com/)

2. Sign up or log in with:
  - Google account
  - GitHub account
  - Email

3. Navigate to [API Keys](https://console.groq.com/keys)

4. Click "Create API Key"

5. Give it a name (e.g., "Agragrati")

6. Copy the key immediately (it won't be shown again!)

### Configuration

Add to your `.env` file:
```env
GROQ_API_KEY=your_groq_key_here
```

### Rate Limits

| Tier | Requests/Minute | Requests/Day |
|------|-----------------|--------------|
| Free | 30 | 6,000 |
| Paid | Custom | Custom |

### Troubleshooting

**"Rate limit exceeded"**: Wait 1 minute or reduce request frequency

**"Invalid API key"**: Regenerate key and update `.env`

---

## RapidAPI / JSearch (Optional)

**Purpose**: Primary source for job listings. Provides real-time job data from multiple sources.

**Free Tier**: 500 requests/month

### Steps to Get API Key

1. Go to [rapidapi.com](https://rapidapi.com/)

2. Create an account or sign in

3. Go to [JSearch API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)

4. Click "Subscribe to Test"

5. Select the **Free** plan (or paid for more requests)

6. Go to your [Apps](https://rapidapi.com/developer/apps) page

7. Find your app and copy the **API Key**

### Configuration

Add to your `.env` file:
```env
RAPIDAPI_KEY=your_rapidapi_key_here
```

### Rate Limits

| Plan | Requests/Month | Price |
|------|----------------|-------|
| Basic | 500 | Free |
| Pro | 10,000 | $10/mo |
| Ultra | 100,000 | $50/mo |

### Usage Tips

- Each job search consumes 1 request
- Smart search may use 1-2 requests (skill extraction + search)
- Consider caching results to reduce API calls

---

## Adzuna API (Optional)

**Purpose**: Secondary job source. Provides additional job listings, especially for international markets.

**Free Tier**: 5,000 requests/month

### Steps to Get API Key

1. Go to [developer.adzuna.com](https://developer.adzuna.com/)

2. Click "Get started for free"

3. Fill out the registration form:
  - Name
  - Email
  - Company (can be personal)
  - Use case (Job search app)

4. Verify your email

5. Go to your [Dashboard](https://developer.adzuna.com/admin/access_details)

6. Find your:
  - **Application ID** (app_id)
  - **Application Key** (app_key)

### Configuration

Add to your `.env` file:
```env
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
```

### Rate Limits

| Tier | Requests/Month | Price |
|------|----------------|-------|
| Developer | 5,000 | Free |
| Production | Custom | Contact |

### Supported Countries

Adzuna covers 16 countries:
- United States
- United Kingdom
- Canada
- Australia
- Germany
- France
- India
- And more...

---

## Supabase (Optional)

**Purpose**: Database for storing job bookmarks and application tracking. Without Supabase, data is stored in browser localStorage only.

**Free Tier**: 500MB storage, 50,000 monthly active users

### Steps to Set Up

1. Go to [supabase.com](https://supabase.com/)

2. Sign up with GitHub or email

3. Click "New Project"

4. Configure:
  - **Organization**: Create or select
  - **Project name**: `agragrati`
  - **Database password**: Generate and save securely
  - **Region**: Choose closest to your users

5. Wait for project to provision (~2 minutes)

### Run Database Schema

1. In Supabase dashboard, go to **SQL Editor**

2. Click "New Query"

3. Paste the contents of `supabase_setup.sql`:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Saved Jobs Table
CREATE TABLE IF NOT EXISTS saved_jobs (
 id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
 user_id TEXT NOT NULL,
 job_title TEXT NOT NULL,
 company TEXT,
 location TEXT,
 job_type TEXT,
 salary TEXT,
 date_posted TEXT,
 apply_link TEXT NOT NULL,
 source TEXT,
 notes TEXT DEFAULT '',
 saved_at TIMESTAMPTZ DEFAULT NOW(),
 UNIQUE(user_id, apply_link)
);

-- Job Applications Table
CREATE TABLE IF NOT EXISTS job_applications (
 id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
 user_id TEXT NOT NULL,
 job_title TEXT NOT NULL,
 company TEXT NOT NULL,
 location TEXT,
 salary TEXT,
 apply_link TEXT,
 status TEXT NOT NULL DEFAULT 'saved',
 applied_date TIMESTAMPTZ,
 interview_date TIMESTAMPTZ,
 notes TEXT DEFAULT '',
 created_at TIMESTAMPTZ DEFAULT NOW(),
 updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_saved_jobs_user_id ON saved_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON job_applications(user_id);

-- Row Level Security
ALTER TABLE saved_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;

-- Allow all operations (anonymous mode)
CREATE POLICY "Allow all for saved_jobs" ON saved_jobs FOR ALL USING (true);
CREATE POLICY "Allow all for job_applications" ON job_applications FOR ALL USING (true);
```

4. Click "Run" (or Ctrl+Enter)

### Get API Credentials

1. Go to **Project Settings** → **API**

2. Copy:
  - **Project URL**: `https://xxxxx.supabase.co`
  - **anon public** key: `your_anon_key`

### Configuration

Add to `frontend/.env.local`:
```env
VITE_SUPABASE_URL=https://yourproject.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Storage Limits (Free Tier)

| Resource | Limit |
|----------|-------|
| Database | 500 MB |
| File Storage | 1 GB |
| Bandwidth | 2 GB/month |
| Edge Functions | 500K invocations |

---

## Configuration Files

### Backend (.env)

Location: Project root or `backend/` directory

```env
# Required
GROQ_API_KEY=your_groq_key_here

# Optional - Job Search APIs
RAPIDAPI_KEY=your_rapidapi_key_here
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key

# Production - Frontend URL for CORS
FRONTEND_URL=https://your-app.vercel.app
```

### Frontend (.env.local)

Location: `frontend/` directory

```env
# Required - Backend API URL
VITE_API_URL=http://localhost:8000

# Optional - Supabase for data persistence
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

### Environment Variable Naming

| Platform | Backend | Frontend |
|----------|---------|----------|
| Local | `.env` | `.env.local` |
| Vercel | Project Settings | Project Settings |
| Render | Environment tab | Environment tab |
| Docker | `docker-compose.yml` | Build args |

---

## API Usage Summary

| Feature | APIs Used |
|---------|-----------|
| Resume Analysis | Groq |
| Career Insights | Groq |
| Cover Letter | Groq |
| Interview Practice | Groq |
| Job Match Score | Groq |
| Resume Builder | Groq |
| Job Search | JSearch + Adzuna |
| Smart Job Search | Groq + JSearch + Adzuna |
| Bookmarks | Supabase |
| Application Tracker | Supabase |

---

## Cost Estimation

**Completely Free Setup**:
- Groq: Free tier (6,000 AI requests/day)
- JSearch: Free tier (500 job searches/month)
- Adzuna: Free tier (5,000 requests/month)
- Supabase: Free tier (500MB storage)
- Vercel: Free tier (100GB bandwidth)

**Estimated Monthly Cost**: $0

**For Higher Usage**:
- Groq: Custom pricing
- JSearch: $10-50/month
- Supabase: $25/month (Pro)
- Vercel: $20/month (Pro)

---

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Rotate keys** if accidentally exposed
4. **Use separate keys** for development and production
5. **Monitor usage** to detect unauthorized access
6. **Set up billing alerts** for paid APIs
