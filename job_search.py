import re
import pandas as pd
import requests
import groq
import os
from typing import List, Dict, Optional
import streamlit as st
import time
import random
import json

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
        if not resume_text or not resume_text.strip():
            return []
            
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
        {resume_text[:3000]}  # Limit content to avoid token limits
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
                skills = [skill.strip().strip('"').strip("'") for skill in skills_text.split(',') if skill.strip()]
                # Filter out empty or too long skills
                skills = [skill for skill in skills if skill and len(skill) < 50]
                return skills[:15]  # Limit to 15 skills
            return []
            
        except Exception as e:
            self._log_error(f"Error extracting skills: {str(e)}")
            return []
    
    def search_jobs_by_resume(self, resume_text: str, location: str = "United States",
                             results_wanted: int = 20, job_type: Optional[str] = None) -> pd.DataFrame:
        """Search for jobs based on resume content."""
        # Extract skills from resume
        skills = self.extract_skills_from_resume(resume_text)
        
        if not skills:
            self._log_warning("Could not extract skills from resume. Please try manual search.")
            return pd.DataFrame()
        
        # Create search term from top skills
        search_term = " OR ".join(skills[:5])  # Use top 5 skills
        
        return self.search_jobs(search_term, location, results_wanted, job_type)
    
    def search_jobs(self, search_term: str, location: str = "United States",
                   results_wanted: int = 20, job_type: Optional[str] = None) -> pd.DataFrame:
        """Search for jobs using real APIs (JSearch and Adzuna)."""
        if not search_term or not search_term.strip():
            self._log_error("Search term cannot be empty")
            return pd.DataFrame()
            
        try:
            all_jobs = []

            # Try JSearch API first (via RapidAPI)
            if self.rapidapi_key and self.rapidapi_key != "your_rapidapi_key_here":
                jsearch_jobs = self._search_jsearch_api(search_term, location, min(results_wanted, 10), job_type)
                all_jobs.extend(jsearch_jobs)

            # Try Adzuna API as backup/additional source
            if (self.adzuna_app_id and self.adzuna_app_id != "your_adzuna_app_id_here" and 
                self.adzuna_app_key and self.adzuna_app_key != "your_adzuna_app_key_here" and 
                len(all_jobs) < results_wanted):
                remaining_results = results_wanted - len(all_jobs)
                adzuna_jobs = self._search_adzuna_api(search_term, location, min(remaining_results, 10), job_type)
                all_jobs.extend(adzuna_jobs)

            # If no API keys available or no results, fall back to sample data
            if not all_jobs:
                if (not self.rapidapi_key or self.rapidapi_key == "your_rapidapi_key_here") and \
                   (not self.adzuna_app_id or self.adzuna_app_id == "your_adzuna_app_id_here" or 
                    not self.adzuna_app_key or self.adzuna_app_key == "your_adzuna_app_key_here"):
                    self._log_warning("⚠️ No API keys configured. Showing sample data. Please add RAPIDAPI_KEY or ADZUNA_APP_ID/ADZUNA_APP_KEY to .env file for real job data.")
                sample_jobs = self._generate_sample_jobs(search_term, location, results_wanted, job_type)
                all_jobs.extend(sample_jobs)

            if not all_jobs:
                self._log_warning("No jobs found for the given criteria.")
                return pd.DataFrame()

            # Convert to DataFrame and clean
            jobs_df = pd.DataFrame(all_jobs)
            jobs_df = self._clean_job_data(jobs_df)

            return jobs_df

        except Exception as e:
            self._log_error(f"Error searching for jobs: {str(e)}")
            return pd.DataFrame()

    def _search_jsearch_api(self, search_term: str, location: str, results_wanted: int, job_type: Optional[str]) -> List[Dict]:
        """Search jobs using JSearch API via RapidAPI."""
        try:
            url = "https://jsearch.p.rapidapi.com/search"

            querystring = {
                "query": f"{search_term} {location}",
                "page": "1",
                "num_pages": "1",
                "date_posted": "week"
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
                self._log_warning(f"JSearch API returned status code: {response.status_code}")
                return []

        except requests.RequestException as e:
            self._log_warning(f"JSearch API request error: {str(e)}")
            return []
        except Exception as e:
            self._log_warning(f"JSearch API error: {str(e)}")
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
                            "Location": job.get("location", {}).get("display_name", "N/A"),
                            "Job Type": job.get("contract_type", "N/A"),
                            "Salary": self._format_salary_adzuna(job),
                            "Date Posted": job.get("created", "N/A"),
                            "Apply Link": job.get("redirect_url", "N/A"),
                            "Source": "Adzuna API"
                        }
                        jobs.append(job_data)

                return jobs
            else:
                self._log_warning(f"Adzuna API returned status code: {response.status_code}")
                return []

        except requests.RequestException as e:
            self._log_warning(f"Adzuna API request error: {str(e)}")
            return []
        except Exception as e:
            self._log_warning(f"Adzuna API error: {str(e)}")
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
        except (ValueError, TypeError):
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
        except (ValueError, TypeError):
            return "Salary not specified"

    def _generate_sample_jobs(self, search_term: str, location: str, results_wanted: int, job_type: Optional[str]) -> List[Dict]:
        """Generate sample job data for demonstration."""
        companies = [
            "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Tesla",
            "Spotify", "Airbnb", "Uber", "LinkedIn", "Twitter", "Adobe", "Salesforce",
            "Oracle", "IBM", "Intel", "NVIDIA", "Cisco", "VMware"
        ]

        # Generate job titles based on search term
        base_titles = [
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
            title = random.choice(base_titles)

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
                "Apply Link": f"https://example.com/jobs/{company.lower().replace(' ', '-')}-{i}",
                "Source": f"{random.choice(sources)} (Sample)"
            }

            sample_jobs.append(job)

        return sample_jobs
    
    def _clean_job_data(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Clean and format job data for display."""
        if jobs_df.empty:
            return jobs_df
            
        try:
            # Remove duplicates based on job title and company if both columns exist
            if 'Job Title' in jobs_df.columns and 'Company' in jobs_df.columns:
                jobs_df = jobs_df.drop_duplicates(subset=['Job Title', 'Company'])
            
            # Sort by date if available (handle different date formats)
            if 'Date Posted' in jobs_df.columns:
                # For now, just sort alphabetically since date formats may vary
                jobs_df = jobs_df.sort_values('Date Posted', ascending=False, na_last=True)
            
            # Clean up any NaN values
            jobs_df = jobs_df.fillna('N/A')
            
            # Ensure consistent column order
            desired_columns = ['Job Title', 'Company', 'Location', 'Job Type', 'Salary', 'Date Posted', 'Apply Link', 'Source']
            available_columns = [col for col in desired_columns if col in jobs_df.columns]
            jobs_df = jobs_df[available_columns]
            
            return jobs_df.reset_index(drop=True)
            
        except Exception as e:
            self._log_error(f"Error cleaning job data: {str(e)}")
            return jobs_df
    
    def get_job_recommendations(self, resume_text: str, target_role: Optional[str] = None) -> List[str]:
        """Get job search recommendations based on resume analysis."""
        if not resume_text or not resume_text.strip():
            return []
            
        prompt = f"""
        Based on the following resume, provide 5 specific job search recommendations.
        Focus on:
        1. Specific job titles to search for
        2. Companies or industries to target
        3. Skills to highlight in applications
        4. Keywords to use in job searches
        
        {f"The user is targeting: {target_role}" if target_role else ""}
        
        Resume content:
        {resume_text[:2000]}  # Limit content to avoid token limits
        
        Provide exactly 5 bullet points with actionable recommendations.
        Format each as: "• [recommendation]"
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
                # Split into individual recommendations and clean them
                lines = recommendations_text.split('\n')
                recommendations = []
                
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith('•') or line.startswith('-') or 
                               any(line.startswith(f'{i}.') for i in range(1, 6))):
                        # Clean up the bullet point
                        clean_rec = line.lstrip('•-123456789. ').strip()
                        if clean_rec:
                            recommendations.append(clean_rec)
                
                return recommendations[:5]  # Limit to 5 recommendations
            return []
            
        except Exception as e:
            self._log_error(f"Error generating recommendations: {str(e)}")
            return []

    def _log_error(self, message: str):
        """Log error message safely."""
        try:
            st.error(message)
        except:
            print(f"ERROR: {message}")

    def _log_warning(self, message: str):
        """Log warning message safely."""
        try:
            st.warning(message)
        except:
            print(f"WARNING: {message}")

    def _log_info(self, message: str):
        """Log info message safely."""
        try:
            st.info(message)
        except:
            print(f"INFO: {message}")