import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import groq
import os
from typing import List, Dict, Optional
from contextlib import contextmanager
import urllib.parse
import time
import random
import json

# Safe import of streamlit - only used if running in Streamlit context
try:
    import streamlit as st
    _STREAMLIT_AVAILABLE = True
except ImportError:
    _STREAMLIT_AVAILABLE = False

@contextmanager
def safe_spinner(message: str):
    """Safe spinner context manager that works with or without Streamlit."""
    if _STREAMLIT_AVAILABLE:
        try:
            with st.spinner(message):
                yield
        except:
            yield
    else:
        print(f"[INFO] {message}")
        yield

def safe_warning(message: str):
    """Safe warning that works with or without Streamlit."""
    if _STREAMLIT_AVAILABLE:
        try:
            st.warning(message)
        except:
            print(f"[WARNING] {message}")
    else:
        print(f"[WARNING] {message}")

def safe_error(message: str):
    """Safe error that works with or without Streamlit."""
    if _STREAMLIT_AVAILABLE:
        try:
            st.error(message)
        except:
            print(f"[ERROR] {message}")
    else:
        print(f"[ERROR] {message}")

class JobSearcher:
    def __init__(self, groq_api_key: str):
        """Initialize the JobSearcher with Groq API key for skill extraction."""
        self.groq_client = groq.Client(api_key=groq_api_key)

        # API configurations
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")  # For JSearch API
        self.adzuna_app_id = os.getenv("ADZUNA_APP_ID")  # For Adzuna API
        self.adzuna_app_key = os.getenv("ADZUNA_APP_KEY")  # For Adzuna API
        
    def extract_skills_from_resume(self, resume_text: str) -> List[str]:
        """Extract relevant skills and keywords from resume text using AI."""
        prompt = f"""
        Analyze the following resume and extract the most relevant skills, technologies, and keywords that would be useful for job searching. 
        Focus on:
        1. Technical skills (programming languages, frameworks, tools)
        2. Professional skills and competencies
        3. Industry-specific keywords
        4. Job titles and roles mentioned
        
        Return ONLY a comma-separated list of keywords/skills, no explanations.
        Maximum 15 most relevant terms.
        
        Resume content:
        {resume_text}
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting relevant job search keywords from resumes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            skills_text = response.choices[0].message.content
            if skills_text:
                skills_text = skills_text.strip()
                # Split by comma and clean up
                skills = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
                return skills[:15]  # Limit to 15 skills
            return []
            
        except Exception as e:
            safe_error(f"Error extracting skills: {str(e)}")
            return []
    
    def search_jobs_by_resume(self, resume_text: str, location: str = "United States",
                             results_wanted: int = 20, job_type: Optional[str] = None) -> pd.DataFrame:
        """Search for jobs based on resume content."""
        # Extract skills from resume
        skills = self.extract_skills_from_resume(resume_text)
        
        if not skills:
            safe_warning("Could not extract skills from resume. Please try manual search.")
            return pd.DataFrame()
        
        # Create search term from top skills
        search_term = " OR ".join(skills[:5])  # Use top 5 skills
        
        return self.search_jobs(search_term, location, results_wanted, job_type)
    
    def search_jobs(self, search_term: str, location: str = "United States",
                   results_wanted: int = 20, job_type: Optional[str] = None) -> pd.DataFrame:
        """Search for jobs using real APIs (JSearch and Adzuna)."""
        try:
            with safe_spinner("Searching for real job opportunities..."):
                all_jobs = []

                # Try JSearch API first (via RapidAPI)
                if self.rapidapi_key:
                    jsearch_jobs = self._search_jsearch_api(search_term, location, min(results_wanted, 10), job_type)
                    all_jobs.extend(jsearch_jobs)

                # Try Adzuna API as backup/additional source
                if self.adzuna_app_id and self.adzuna_app_key and len(all_jobs) < results_wanted:
                    remaining_results = results_wanted - len(all_jobs)
                    adzuna_jobs = self._search_adzuna_api(search_term, location, min(remaining_results, 10), job_type)
                    all_jobs.extend(adzuna_jobs)

                if not all_jobs:
                    if not self.rapidapi_key and not (self.adzuna_app_id and self.adzuna_app_key):
                        safe_warning("⚠️ No API keys configured. Showing sample data. Please add RAPIDAPI_KEY or ADZUNA_APP_ID/ADZUNA_APP_KEY to .env file for real job data.")
                    sample_jobs = self._generate_sample_jobs(search_term, location, results_wanted, job_type)
                    all_jobs.extend(sample_jobs)

                if not all_jobs:
                    safe_warning("No jobs found for the given criteria.")
                    return pd.DataFrame()

                # Convert to DataFrame and clean
                jobs_df = pd.DataFrame(all_jobs)
                jobs_df = self._clean_job_data(jobs_df)

                return jobs_df

        except Exception as e:
            safe_error(f"Error searching for jobs: {str(e)}")
            return pd.DataFrame()

    def _search_jsearch_api(self, search_term: str, location: str, results_wanted: int, job_type: Optional[str]) -> List[Dict]:
        """Search jobs using JSearch API via RapidAPI."""
        try:
            url = "https://jsearch.p.rapidapi.com/search"

            querystring = {
                "query": f"{search_term} {location}",
                "page": "1",
                "country": f"{location}",
                "num_pages": "1",
                "date_posted": "all"
            }

            # Add job type filter if specified
            if job_type and job_type.lower() != "any":
                employment_types = {
                    "full-time": "FULLTIME",
                    "part-time": "PARTTIME",
                    "contract": "CONTRACTOR",
                    "internship": "INTERN"
                }
                if job_type.lower() in employment_types:
                    querystring["employment_types"] = employment_types[job_type.lower()]

            headers = {
                "x-rapidapi-key": self.rapidapi_key,
                "x-rapidapi-host": "jsearch.p.rapidapi.com"
            }

            response = requests.get(url, headers=headers, params=querystring, timeout=10)


            if response.status_code == 200:
                data = response.json()
                jobs = []

                if "data" in data and data["data"]:
                    for job in data["data"][:results_wanted]:
                        job_data = {
                            "Job Title": job.get("job_title", "N/A"),
                            "Company": job.get("employer_name", "N/A"),
                            "Location": f"{job.get('job_city', '')}, {job.get('job_state', '')}".strip(", "),
                            "Job Type": job.get("job_employment_type", "N/A"),
                            "Salary": self._format_salary_jsearch(job),
                            "Date Posted": job.get("job_posted_at_datetime_utc", "N/A"),
                            "Apply Link": job.get("job_apply_link", "N/A"),
                            "Source": "JSearch API"
                        }
                        jobs.append(job_data)

                return jobs
            else:
                safe_warning(f"JSearch API returned status code: {response.status_code}")
                return []

        except Exception as e:
            safe_warning(f"JSearch API error: {str(e)}")
            return []

    def _search_adzuna_api(self, search_term: str, location: str, results_wanted: int, job_type: Optional[str]) -> List[Dict]:
        """Search jobs using Adzuna API."""
        try:
            # Convert location to country code (simplified)
            country = "us"  # Default to US
            if "uk" in location.lower() or "united kingdom" in location.lower():
                country = "gb"
            elif "canada" in location.lower():
                country = "ca"
            elif "australia" in location.lower():
                country = "au"

            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

            params = {
                "app_id": self.adzuna_app_id,
                "app_key": self.adzuna_app_key,
                "results_per_page": min(results_wanted, 20),
                "what": search_term,
                "where": location,
                "sort_by": "date"
            }

            # Add job type filter if specified
            if job_type and job_type.lower() != "any":
                job_type_mapping = {
                    "full-time": "permanent",
                    "part-time": "part_time",
                    "contract": "contract",
                    "internship": "graduate"
                }
                if job_type.lower() in job_type_mapping:
                    params["category"] = job_type_mapping[job_type.lower()]

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                jobs = []

                if "results" in data:
                    for job in data["results"]:
                        job_data = {
                            "Job Title": job.get("title", "N/A"),
                            "Company": job.get("company", {}).get("display_name", "N/A"),
                            "Location": f"{job.get('location', {}).get('display_name', 'N/A')}",
                            "Job Type": job.get("contract_type", "N/A"),
                            "Salary": self._format_salary_adzuna(job),
                            "Date Posted": job.get("created", "N/A"),
                            "Apply Link": job.get("redirect_url", "N/A"),
                            "Source": "Adzuna API"
                        }
                        jobs.append(job_data)

                return jobs
            else:
                safe_warning(f"Adzuna API returned status code: {response.status_code}")
                return []

        except Exception as e:
            safe_warning(f"Adzuna API error: {str(e)}")
            return []

    def _format_salary_jsearch(self, job: Dict) -> str:
        """Format salary from JSearch API response."""
        try:
            min_salary = job.get("job_min_salary")
            max_salary = job.get("job_max_salary")
            salary_period = job.get("job_salary_period", "year")

            if min_salary and max_salary:
                return f"${int(min_salary):,} - ${int(max_salary):,} per {salary_period}"
            elif min_salary:
                return f"${int(min_salary):,}+ per {salary_period}"
            elif max_salary:
                return f"Up to ${int(max_salary):,} per {salary_period}"
            else:
                return "Salary not specified"
        except:
            return "Salary not specified"

    def _format_salary_adzuna(self, job: Dict) -> str:
        """Format salary from Adzuna API response."""
        try:
            min_salary = job.get("salary_min")
            max_salary = job.get("salary_max")

            if min_salary and max_salary:
                return f"${int(min_salary):,} - ${int(max_salary):,} yearly"
            elif min_salary:
                return f"${int(min_salary):,}+ yearly"
            elif max_salary:
                return f"Up to ${int(max_salary):,} yearly"
            else:
                return "Salary not specified"
        except:
            return "Salary not specified"

    def _generate_sample_jobs(self, search_term: str, location: str, results_wanted: int, job_type: Optional[str]) -> List[Dict]:
        """Generate sample job data for demonstration."""
        companies = [
            "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Tesla",
            "Spotify", "Airbnb", "Uber", "LinkedIn", "Twitter", "Adobe", "Salesforce",
            "Oracle", "IBM", "Intel", "NVIDIA", "Cisco", "VMware"
        ]

        job_titles = [
            f"Senior {search_term}",
            f"Junior {search_term}",
            f"{search_term} Specialist",
            f"Lead {search_term}",
            f"{search_term} Manager",
            f"{search_term} Analyst",
            f"{search_term} Developer",
            f"{search_term} Engineer",
            f"Principal {search_term}",
            f"{search_term} Consultant"
        ]

        job_types = ["Full-time", "Part-time", "Contract", "Internship"]
        sources = ["LinkedIn", "Indeed", "ZipRecruiter", "Company Website"]

        sample_jobs = []

        for i in range(min(results_wanted, 20)):  # Limit to 20 for demo
            company = random.choice(companies)
            title = random.choice(job_titles)

            # Filter by job type if specified
            if job_type and job_type != "Any":
                selected_job_type = job_type
            else:
                selected_job_type = random.choice(job_types)

            # Generate salary range
            base_salary = random.randint(60000, 150000)
            salary_range = f"${base_salary:,} - ${base_salary + 20000:,} yearly"

            job = {
                "Job Title": title,
                "Company": company,
                "Location": location,
                "Job Type": selected_job_type,
                "Salary": salary_range,
                "Date Posted": f"{random.randint(1, 7)} days ago",
                "Apply Link": f"https://example.com/jobs/{company.lower()}-{i}",
                "Source": random.choice(sources)
            }

            sample_jobs.append(job)

        return sample_jobs
    
    def _clean_job_data(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Clean and format job data for display."""
        try:
            # Select and rename columns for better display
            display_columns = {
                'title': 'Job Title',
                'company': 'Company',
                'location': 'Location',
                'job_type': 'Job Type',
                'salary': 'Salary',
                'date_posted': 'Date Posted',
                'job_url': 'Apply Link',
                'site': 'Source'
            }
            
            # Create salary column from min/max amounts or use existing salary
            if 'Salary' not in jobs_df.columns:
                if 'min_amount' in jobs_df.columns and 'max_amount' in jobs_df.columns:
                    jobs_df['salary'] = jobs_df.apply(self._format_salary, axis=1)
                else:
                    jobs_df['salary'] = 'Not specified'
            
            # Handle location column
            if 'city' in jobs_df.columns and 'state' in jobs_df.columns:
                jobs_df['location'] = jobs_df.apply(
                    lambda row: f"{row.get('city', '')}, {row.get('state', '')}".strip(', '), 
                    axis=1
                )
            
            # Select available columns
            available_columns = {}
            for old_col, new_col in display_columns.items():
                if old_col in jobs_df.columns:
                    available_columns[old_col] = new_col
            
            # Rename columns
            jobs_df = jobs_df.rename(columns=available_columns)
            
            # Select only the renamed columns that exist
            final_columns = [col for col in display_columns.values() if col in jobs_df.columns]
            jobs_df = jobs_df[final_columns]
            
            # Remove duplicates based on job title and company
            if 'Job Title' in jobs_df.columns and 'Company' in jobs_df.columns:
                jobs_df = jobs_df.drop_duplicates(subset=['Job Title', 'Company'])
            
            # Sort by date if available
            if 'Date Posted' in jobs_df.columns:
                jobs_df = jobs_df.sort_values('Date Posted', ascending=False)
            
            return jobs_df.reset_index(drop=True)
            
        except Exception as e:
            safe_error(f"Error cleaning job data: {str(e)}")
            return jobs_df
    
    def _format_salary(self, row) -> str:
        """Format salary information from min/max amounts."""
        try:
            min_amount = row.get('min_amount')
            max_amount = row.get('max_amount')
            interval = row.get('interval', 'yearly')
            
            if pd.isna(min_amount) and pd.isna(max_amount):
                return 'Not specified'
            
            # Format amounts
            if not pd.isna(min_amount) and not pd.isna(max_amount):
                if min_amount == max_amount:
                    return f"${int(min_amount):,} {interval}"
                else:
                    return f"${int(min_amount):,} - ${int(max_amount):,} {interval}"
            elif not pd.isna(min_amount):
                return f"${int(min_amount):,}+ {interval}"
            elif not pd.isna(max_amount):
                return f"Up to ${int(max_amount):,} {interval}"
            
            return 'Not specified'
            
        except Exception:
            return 'Not specified'
    
    def get_job_recommendations(self, resume_text: str, target_role: Optional[str] = None) -> List[str]:
        """Get job search recommendations based on resume analysis."""
        prompt = f"""
        Based on the following resume, provide 5 specific job search recommendations.
        Focus on:
        1. Specific job titles to search for
        2. Companies or industries to target
        3. Skills to highlight in applications
        4. Keywords to use in job searches
        
        {f"The user is targeting: {target_role}" if target_role else ""}
        
        Resume content:
        {resume_text}
        
        Provide exactly 5 bullet points with actionable recommendations.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a career counselor providing job search advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            recommendations_text = response.choices[0].message.content
            if recommendations_text:
                recommendations_text = recommendations_text.strip()
                # Split into individual recommendations
                recommendations = [rec.strip() for rec in recommendations_text.split('\n') if rec.strip() and ('•' in rec or '-' in rec or rec.startswith(('1.', '2.', '3.', '4.', '5.')))]
                return recommendations[:5]
            return []
            
        except Exception as e:
            safe_error(f"Error generating recommendations: {str(e)}")
            return []

    def get_career_path_analysis(self, resume_text: str, target_role: Optional[str] = None) -> Dict:
        """Analyze potential career paths based on resume."""
        prompt = f"""
        Based on the following resume, analyze potential career paths.
        {f"The user is targeting: {target_role}" if target_role else ""}
        
        Resume content:
        {resume_text}
        
        Provide a JSON response with the following structure (no markdown, just pure JSON):
        {{
            "current_level": "Entry/Mid/Senior/Lead/Executive level assessment",
            "career_paths": [
                {{
                    "path_name": "Career Path Name",
                    "description": "Brief description",
                    "next_role": "Immediate next role",
                    "timeline": "Estimated timeline to reach",
                    "requirements": ["Key requirement 1", "Key requirement 2"]
                }}
            ],
            "strengths_for_growth": ["Strength 1", "Strength 2", "Strength 3"],
            "growth_areas": ["Area 1", "Area 2", "Area 3"]
        }}
        
        Provide 3 distinct career paths. Return ONLY valid JSON, no explanation text.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a career advisor. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            result = response.choices[0].message.content.strip()
            # Clean up potential markdown formatting
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            result = result.strip()
            
            return json.loads(result)
            
        except Exception as e:
            return {"error": str(e)}

    def get_skill_gap_analysis(self, resume_text: str, target_role: Optional[str] = None) -> Dict:
        """Analyze skill gaps for target role."""
        role_context = target_role if target_role else "a senior position in their field"
        
        prompt = f"""
        Analyze the skill gaps between the resume and requirements for {role_context}.
        
        Resume content:
        {resume_text}
        
        Provide a JSON response with the following structure (no markdown, just pure JSON):
        {{
            "current_skills": {{
                "technical": ["skill1", "skill2"],
                "soft": ["skill1", "skill2"],
                "domain": ["skill1", "skill2"]
            }},
            "required_skills": {{
                "technical": ["skill1", "skill2"],
                "soft": ["skill1", "skill2"],
                "domain": ["skill1", "skill2"]
            }},
            "skill_gaps": [
                {{
                    "skill": "Skill name",
                    "priority": "High/Medium/Low",
                    "importance": "Why this skill matters",
                    "how_to_acquire": "How to learn this skill"
                }}
            ],
            "match_percentage": 75
        }}
        
        Identify top 5 skill gaps. Return ONLY valid JSON, no explanation text.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a skills analyst. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            result = result.strip()
            
            return json.loads(result)
            
        except Exception as e:
            return {"error": str(e)}

    def get_salary_insights(self, resume_text: str, target_role: Optional[str] = None, location: str = "United States") -> Dict:
        """Get salary insights based on resume and target role."""
        role_context = target_role if target_role else "positions matching this resume"
        
        prompt = f"""
        Provide salary insights for {role_context} in {location} based on this resume.
        
        Resume content:
        {resume_text}
        
        Provide a JSON response with the following structure (no markdown, just pure JSON):
        {{
            "estimated_current_value": {{
                "low": 80000,
                "mid": 95000,
                "high": 115000,
                "currency": "USD"
            }},
            "market_rate": {{
                "entry_level": {{"low": 60000, "high": 80000}},
                "mid_level": {{"low": 80000, "high": 110000}},
                "senior_level": {{"low": 110000, "high": 150000}},
                "lead_level": {{"low": 140000, "high": 180000}}
            }},
            "factors_affecting_salary": [
                {{"factor": "Factor name", "impact": "Positive/Negative", "details": "Explanation"}}
            ],
            "negotiation_tips": ["Tip 1", "Tip 2", "Tip 3"],
            "additional_compensation": ["Bonus types", "Stock options", "Benefits to negotiate"]
        }}
        
        Return ONLY valid JSON, no explanation text.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a compensation analyst. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            result = result.strip()
            
            return json.loads(result)
            
        except Exception as e:
            return {"error": str(e)}

    def get_interview_preparation(self, resume_text: str, target_role: Optional[str] = None) -> Dict:
        """Get interview preparation tips based on resume."""
        role_context = target_role if target_role else "relevant positions"
        
        prompt = f"""
        Provide interview preparation guidance for {role_context} based on this resume.
        
        Resume content:
        {resume_text}
        
        Provide a JSON response with the following structure (no markdown, just pure JSON):
        {{
            "likely_questions": [
                {{
                    "question": "Interview question",
                    "category": "Behavioral/Technical/Situational",
                    "suggested_approach": "How to answer",
                    "resume_points_to_highlight": ["Point from resume to mention"]
                }}
            ],
            "stories_to_prepare": [
                {{
                    "situation": "STAR situation based on resume",
                    "applicable_questions": ["Questions this story answers"]
                }}
            ],
            "technical_topics_to_review": ["Topic 1", "Topic 2", "Topic 3"],
            "questions_to_ask_interviewer": ["Question 1", "Question 2", "Question 3"],
            "red_flags_to_address": [
                {{
                    "concern": "Potential concern from resume",
                    "how_to_address": "How to proactively address this"
                }}
            ]
        }}
        
        Provide 5 likely questions and 3 STAR stories. Return ONLY valid JSON, no explanation text.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an interview coach. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            result = result.strip()
            
            return json.loads(result)
            
        except Exception as e:
            return {"error": str(e)}

    def get_learning_recommendations(self, resume_text: str, target_role: Optional[str] = None) -> Dict:
        """Get personalized learning recommendations."""
        role_context = target_role if target_role else "career advancement"
        
        prompt = f"""
        Provide learning recommendations to help achieve {role_context} based on this resume.
        
        Resume content:
        {resume_text}
        
        Provide a JSON response with the following structure (no markdown, just pure JSON):
        {{
            "courses": [
                {{
                    "title": "Course name",
                    "platform": "Coursera/Udemy/LinkedIn Learning/etc",
                    "skill_covered": "What skill this develops",
                    "priority": "High/Medium/Low",
                    "estimated_duration": "X hours/weeks"
                }}
            ],
            "certifications": [
                {{
                    "name": "Certification name",
                    "provider": "Certification provider",
                    "value": "Why this certification matters",
                    "difficulty": "Beginner/Intermediate/Advanced",
                    "estimated_prep_time": "X months"
                }}
            ],
            "books": [
                {{
                    "title": "Book title",
                    "author": "Author name",
                    "why_recommended": "Reason for recommendation"
                }}
            ],
            "projects_to_build": [
                {{
                    "project": "Project description",
                    "skills_demonstrated": ["Skill 1", "Skill 2"],
                    "portfolio_value": "How this helps your portfolio"
                }}
            ],
            "communities_to_join": ["Community 1", "Community 2"]
        }}
        
        Provide 4 courses, 3 certifications, 3 books, and 3 projects. Return ONLY valid JSON, no explanation text.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a learning advisor. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            result = result.strip()
            
            return json.loads(result)
            
        except Exception as e:
            return {"error": str(e)}

    def match_resume_to_job(self, resume_text: str, job_description: str) -> Dict:
        """Match resume against a job description and provide detailed analysis."""
        prompt = f"""
        Analyze how well this resume matches the job description. Provide a detailed compatibility analysis.
        
        RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        Provide a JSON response with the following structure (no markdown, just pure JSON):
        {{
            "match_score": 75,
            "match_level": "Good Match/Strong Match/Excellent Match/Weak Match/Poor Match",
            "summary": "Brief 2-3 sentence summary of the match",
            "matching_keywords": [
                {{
                    "keyword": "keyword from job description",
                    "found_in_resume": true,
                    "context": "Where/how it appears in resume"
                }}
            ],
            "missing_keywords": [
                {{
                    "keyword": "Missing keyword",
                    "importance": "Critical/Important/Nice to have",
                    "suggestion": "How to add or address this"
                }}
            ],
            "strengths": [
                {{
                    "area": "Area of strength",
                    "details": "Why this is a strong match"
                }}
            ],
            "weaknesses": [
                {{
                    "area": "Area of weakness",
                    "details": "Why this is a gap",
                    "how_to_improve": "Specific improvement suggestion"
                }}
            ],
            "experience_match": {{
                "required_years": "X years",
                "candidate_years": "Y years",
                "assessment": "Meets/Exceeds/Below requirements"
            }},
            "education_match": {{
                "required": "Required education",
                "candidate_has": "Candidate's education",
                "assessment": "Meets/Exceeds/Below requirements"
            }},
            "skills_breakdown": {{
                "technical_skills": {{
                    "matched": ["skill1", "skill2"],
                    "missing": ["skill3", "skill4"],
                    "match_percentage": 70
                }},
                "soft_skills": {{
                    "matched": ["skill1", "skill2"],
                    "missing": ["skill3"],
                    "match_percentage": 80
                }}
            }},
            "ats_optimization_tips": [
                "Tip 1 for better ATS compatibility",
                "Tip 2 for better ATS compatibility",
                "Tip 3 for better ATS compatibility"
            ],
            "resume_improvements": [
                {{
                    "section": "Section to improve",
                    "current": "Current state",
                    "suggested": "Suggested improvement",
                    "priority": "High/Medium/Low"
                }}
            ],
            "cover_letter_points": [
                "Key point to mention in cover letter",
                "Another key point to address"
            ]
        }}
        
        Be thorough in identifying ALL keywords from the job description. Return ONLY valid JSON, no explanation text.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert ATS (Applicant Tracking System) analyst and resume optimization specialist. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content.strip()
            # Clean up potential markdown formatting
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            result = result.strip()
            
            return json.loads(result)
            
        except Exception as e:
            return {"error": str(e)}

    def get_industry_insights(self, resume_text: str, target_role: Optional[str] = None) -> Dict:
        """Get industry insights and trends based on resume analysis."""
        prompt = f"""
        Based on this resume, provide industry insights and trends.
        {f"The user is targeting: {target_role}" if target_role else ""}
        
        Resume content:
        {resume_text}
        
        Provide a JSON response with the following structure (no markdown, just pure JSON):
        {{
            "relevant_industries": ["Industry 1", "Industry 2", "Industry 3"],
            "industry_trends": [
                {{
                    "trend": "Trend name",
                    "impact": "How this affects job seekers",
                    "opportunity": "How to leverage this trend"
                }}
            ],
            "emerging_roles": [
                {{
                    "role": "Role title",
                    "description": "What this role does",
                    "fit_score": "High/Medium/Low based on resume"
                }}
            ],
            "companies_to_target": [
                {{
                    "company_type": "Type of company",
                    "examples": ["Company 1", "Company 2"],
                    "why_good_fit": "Reason"
                }}
            ],
            "market_outlook": {{
                "demand": "High/Medium/Low",
                "competition": "High/Medium/Low",
                "summary": "Brief market outlook summary"
            }}
        }}
        
        Return ONLY valid JSON, no explanation text.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an industry analyst. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            result = result.strip()
            
            return json.loads(result)
            
        except Exception as e:
            return {"error": str(e)}
