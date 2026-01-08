-- Supabase SQL Setup for Agragrati
-- Run these commands in your Supabase SQL Editor

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
  
  -- Prevent duplicate saves
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
  status TEXT NOT NULL DEFAULT 'saved' CHECK (status IN ('saved', 'applied', 'interviewing', 'offered', 'rejected', 'withdrawn')),
  applied_date TIMESTAMPTZ,
  interview_date TIMESTAMPTZ,
  notes TEXT DEFAULT '',
  resume_version TEXT DEFAULT '',
  cover_letter TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Profiles Table (for future auth)
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE,
  full_name TEXT,
  resume_text TEXT,
  target_role TEXT,
  location TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_saved_jobs_user_id ON saved_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_jobs_apply_link ON saved_jobs(apply_link);
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON job_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON job_applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_updated ON job_applications(updated_at DESC);

-- Row Level Security (RLS) - Optional but recommended
-- Enable RLS
ALTER TABLE saved_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;

-- Policies for anonymous access (based on user_id in localStorage)
-- For a production app, you'd want proper auth

-- Allow all operations for now (anonymous mode)
CREATE POLICY "Allow all for saved_jobs" ON saved_jobs FOR ALL USING (true);
CREATE POLICY "Allow all for job_applications" ON job_applications FOR ALL USING (true);

-- If you want to restrict by user_id later:
-- CREATE POLICY "Users can only see their own saved jobs" 
--   ON saved_jobs FOR SELECT 
--   USING (user_id = current_setting('app.current_user_id', true));
