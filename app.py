import streamlit as st
import groq
import PyPDF2
import io
import os
import pandas as pd
from dotenv import load_dotenv
from job_search import JobSearcher
from interview_training import render_interview_training

load_dotenv()

st.set_page_config(page_title='Agragrati - AI Resume & Job Search', layout='wide')

st.title('🎯 Agragrati - AI Resume & Job Search')
st.markdown('Upload your resume to receive feedback and find real job opportunities!')


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize job searcher
if GROQ_API_KEY:
    job_searcher = JobSearcher(GROQ_API_KEY)
else:
    st.error("GROQ_API_KEY not found. Please check your .env file.")
    st.stop()

# Initialize session state variables
if 'resume_content' not in st.session_state:
    st.session_state.resume_content = None
if 'resume_analyzed' not in st.session_state:
    st.session_state.resume_analyzed = False
if 'project_analysis' not in st.session_state:
    st.session_state.project_analysis = None
if 'career_insights' not in st.session_state:
    st.session_state.career_insights = None
if 'extracted_skills' not in st.session_state:
    st.session_state.extracted_skills = []

# Create tabs for different functionalities
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 Resume Analysis", 
    "🔍 Job Search", 
    "💡 Career Insights", 
    "📊 Project Review",
    "🎤 Interview Training"
])

def extract_text_pdf(file):
    """Extract text from PDF file."""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file (PDF or TXT)."""
    if uploaded_file.type == "application/pdf":
        return extract_text_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

def analyze_projects_against_job_offer(resume_content: str, job_offer: str, groq_client) -> str:
    """Analyze resume projects against a specific job offer."""
    prompt = f"""
You are a senior technical recruiter and project analyst with 10+ years of experience. 
Analyze the projects mentioned in the resume against the specific job offer provided.

**ANALYSIS FRAMEWORK:**
Please structure your response with the following sections:

1. **JOB REQUIREMENTS SUMMARY**
- Key technical requirements from the job offer
- Required skills and technologies
- Experience level expected

2. **PROJECT ALIGNMENT ANALYSIS**
- Which projects from the resume align with job requirements
- Specific technologies/skills that match
- Relevance score for each project (1-10)

3. **STRENGTHS & MATCHES**
- Projects that strongly demonstrate required skills
- Specific examples that would impress this employer
- Transferable skills from projects

4. **GAPS & MISSING ELEMENTS**
- Required skills not demonstrated in current projects
- Technologies mentioned in job offer but missing from projects
- Areas where projects could be enhanced

5. **PROJECT ENHANCEMENT RECOMMENDATIONS**
- How to modify existing projects to better match job requirements
- Additional features/technologies to add
- Ways to better showcase relevant skills

6. **INTERVIEW PREPARATION**
- Which projects to highlight in interviews
- Key talking points for each relevant project
- How to position projects to address job requirements

7. **ACTION ITEMS**
- Priority improvements for existing projects
- New project ideas that would strengthen candidacy
- Skills to develop based on job requirements

**JOB OFFER:**
{job_offer}

**RESUME CONTENT:**
{resume_content}

**INSTRUCTIONS:**
- Focus specifically on technical projects and their relevance
- Be specific about technology matches and mismatches
- Provide actionable recommendations for project improvement
- Consider both current projects and suggestions for new ones
- Rate each project's relevance to this specific job offer
- Suggest concrete ways to make projects more compelling for this role
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert technical recruiter and project analyst specializing in matching candidate projects to job requirements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing projects: {str(e)}"

def analyze_resume(file_content: str, job_role: str, groq_client):
    """Perform comprehensive resume analysis."""
    prompt = f"""
You are an expert resume reviewer and career consultant with 15+ years of experience in talent acquisition and HR. 
Analyze the following resume and provide comprehensive, actionable feedback for {job_role if job_role else 'general job applications'}.

**ANALYSIS FRAMEWORK:**
Please structure your response with the following sections:

1. **OVERALL IMPRESSION** (1-2 sentences)
- First impression and general quality assessment

2. **STRENGTHS** 
- What works well in this resume
- Standout achievements or experiences

3. **AREAS FOR IMPROVEMENT**
- Content gaps or weaknesses
- Formatting and presentation issues
- Missing key information

4. **SPECIFIC RECOMMENDATIONS**
- Concrete suggestions for improvement
- Industry-specific advice for {job_role if job_role else 'General Job Applications'}
- Keywords and skills to consider adding

5. **ACTION ITEMS** 
- Priority fixes (High/Medium/Low)
- Quick wins that can be implemented immediately

6. **FINAL SCORE** 
- Rate the resume from 1-10 with brief justification

**RESUME CONTENT:**
{file_content}

**INSTRUCTIONS:**
- Be honest but constructive in your feedback
- Provide specific examples from the resume when pointing out issues
- Consider ATS (Applicant Tracking System) compatibility
- Focus on relevance to {job_role if job_role else 'modern job market standards'}
- Suggest specific metrics, action verbs, and formatting improvements
- Keep feedback actionable and prioritized
"""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing resume: {str(e)}"

# TAB 1: Resume Analysis
with tab1:
    st.header("Resume Analysis")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF or TXT)", type=["pdf", "txt"])
    job_role = st.text_input("Enter the job role you are targeting (optional)")
    
    # Optional Project Review Section
    st.markdown("---")
    st.subheader("🎯 Optional: Project vs Job Offer Review")
    st.markdown("*Compare your projects against a specific job posting for targeted insights*")
    
    enable_project_review = st.checkbox("Enable Project Review Against Job Offer")
    job_offer_text = None
    
    if enable_project_review:
        st.info("📋 Paste the job description/offer below to get project-specific feedback")
        job_offer_text = st.text_area(
            "Job Description/Offer",
            placeholder="Paste the complete job description here...",
            height=200,
            help="Include job requirements, responsibilities, skills needed, etc."
        )
    
    analyze_button = st.button("Analyze Resume", type="primary")
    
    # Resume Analysis Logic
    if analyze_button and uploaded_file:
        with st.spinner("Analyzing your resume..."):
            file_content = extract_text_from_file(uploaded_file)

            if not file_content.strip():
                st.error("File does not have any content!")
            else:
                # Store resume content in session state
                st.session_state.resume_content = file_content
                st.session_state.resume_analyzed = True

                # Initialize Groq client
                client = groq.Client(api_key=GROQ_API_KEY)

                # Perform resume analysis
                resume_analysis = analyze_resume(file_content, job_role, client)
                
                # Extract skills and get recommendations
                skills = job_searcher.extract_skills_from_resume(file_content)
                st.session_state.extracted_skills = skills
                
                # Get job recommendations
                recommendations = job_searcher.get_job_recommendations(file_content, job_role)
                st.session_state.career_insights = {
                    'recommendations': recommendations,
                    'skills': skills,
                    'analysis': resume_analysis
                }

                # Display results
                st.balloons()
                st.markdown('### 📋 Resume Analysis Results:')
                st.markdown(resume_analysis)

                # Project Review Analysis (if enabled)
                if enable_project_review and job_offer_text and job_offer_text.strip():
                    st.markdown("---")
                    st.markdown('### 🎯 Project vs Job Offer Analysis:')
                    
                    with st.spinner("Analyzing your projects against the job offer..."):
                        project_analysis = analyze_projects_against_job_offer(file_content, job_offer_text, client)
                        st.session_state.project_analysis = project_analysis
                        st.markdown(project_analysis)

                st.success("✅ Analysis complete! Check the Career Insights and Project Review tabs for additional information.")

def display_job_result(jobs_df, search_type):
    """Display job search results with filters and download options."""
    st.markdown("### 💼 Job Search Results:")

    # Add filters for the results
    col1, col2 = st.columns(2)
    with col1:
        if 'Company' in jobs_df.columns:
            companies = ['All'] + sorted(jobs_df['Company'].dropna().unique().tolist())
            selected_company = st.selectbox("Filter by Company", companies, key=f"{search_type}_company")

    with col2:
        if 'Source' in jobs_df.columns:
            sources = ['All'] + sorted(jobs_df['Source'].dropna().unique().tolist())
            selected_source = st.selectbox("Filter by Source", sources, key=f"{search_type}_source")

    # Apply filters
    filtered_df = jobs_df.copy()
    if 'Company' in jobs_df.columns and selected_company != 'All':
        filtered_df = filtered_df[filtered_df['Company'] == selected_company]
    if 'Source' in jobs_df.columns and selected_source != 'All':
        filtered_df = filtered_df[filtered_df['Source'] == selected_source]

    # Display filtered results
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Apply Link": st.column_config.LinkColumn("Apply Link")
        }
    )

    # Download option
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name="job_search_results.csv",
        mime="text/csv",
        key=f"{search_type}_download"
    )


# TAB 2: Job Search
with tab2:
    st.header("Job Search")

    # Show API status
    api_status = []
    if hasattr(job_searcher, 'rapidapi_key') and job_searcher.rapidapi_key and job_searcher.rapidapi_key != "your_rapidapi_key_here":
        api_status.append("✅ JSearch API")
    else:
        api_status.append("❌ JSearch API (not configured)")

    if (hasattr(job_searcher, 'adzuna_app_id') and job_searcher.adzuna_app_id and job_searcher.adzuna_app_id != "your_adzuna_app_id_here" and
        hasattr(job_searcher, 'adzuna_app_key') and job_searcher.adzuna_app_key and job_searcher.adzuna_app_key != "your_adzuna_app_key_here"):
        api_status.append("✅ Adzuna API")
    else:
        api_status.append("❌ Adzuna API (not configured)")

    st.info(f"**API Status**: {' | '.join(api_status)}")

    if not any("✅" in status for status in api_status):
        st.warning("⚠️ No job search APIs configured. Will show sample data. See README for API setup instructions.")

    # Job search options
    search_option = st.radio(
        "Choose search method:",
        ["🤖 Smart Search (Based on Resume)", "✏️ Manual Search"]
    )

    col1, col2 = st.columns(2)

    with col1:
        if search_option == "✏️ Manual Search":
            search_term = st.text_input("Job title or keywords", placeholder="e.g., Software Engineer, Data Analyst")
        else:
            search_term = None
            if not st.session_state.resume_analyzed:
                st.info("Upload your resume in the Resume Analysis tab first, then return here for smart job search.")

        location = st.text_input("Location", value="United States", placeholder="e.g., San Francisco, CA")

    with col2:
        job_type_filter = st.selectbox(
            "Job Type",
            ["Any", "Full-time", "Part-time", "Contract", "Internship"]
        )

        results_count = st.slider("Number of results", min_value=10, max_value=50, value=20)

    search_jobs_button = st.button("🔍 Search Jobs", type="primary")

    # Job Search Logic
    if search_jobs_button:
        if search_option == "🤖 Smart Search (Based on Resume)":
            if not st.session_state.resume_content:
                st.error("Please upload and analyze your resume first in the Resume Analysis tab.")
            else:
                with st.spinner("Searching for jobs based on your resume..."):
                    job_type_param = None if job_type_filter == "Any" else job_type_filter
                    jobs_df = job_searcher.search_jobs_by_resume(
                        st.session_state.resume_content,
                        location,
                        results_count,
                        job_type_param
                    )

                    if not jobs_df.empty:
                        st.success(f"Found {len(jobs_df)} job opportunities!")
                        display_job_result(jobs_df, "smart")
                    else:
                        st.warning("No jobs found. Try adjusting your search criteria.")

        else:  # Manual search
            if not search_term:
                st.error("Please enter a job title or keywords to search.")
            else:
                with st.spinner(f"Searching for '{search_term}' jobs..."):
                    job_type_param = None if job_type_filter == "Any" else job_type_filter
                    jobs_df = job_searcher.search_jobs(
                        search_term,
                        location,
                        results_count,
                        job_type_param
                    )

                    if not jobs_df.empty:
                        st.success(f"Found {len(jobs_df)} job opportunities!")
                        display_job_result(jobs_df, "manual")
                    else:
                        st.warning("No jobs found. Try adjusting your search criteria.")


# TAB 3: Career Insights
with tab3:
    st.header("Career Insights")
    
    if st.session_state.career_insights:
        st.success("✅ Resume analyzed! Here are your personalized career insights:")
        
        insights = st.session_state.career_insights
        
        # Job Search Recommendations
        if insights.get('recommendations'):
            st.markdown("### 🎯 Job Search Recommendations:")
            for i, rec in enumerate(insights['recommendations'], 1):
                st.markdown(f"{i}. {rec}")
        
        # Skills Section
        if insights.get('skills'):
            st.markdown("### 🔧 Key Skills Identified:")
            skills_html = " ".join([
                f'<span style="background-color: #e1f5fe; padding: 4px 8px; margin: 2px; border-radius: 12px; font-size: 12px; display: inline-block;">{skill}</span>' 
                for skill in insights['skills']
            ])
            st.markdown(skills_html, unsafe_allow_html=True)
            
        # Download insights
        if insights.get('analysis'):
            st.download_button(
                label="📥 Download Career Analysis",
                data=insights['analysis'],
                file_name="career_analysis.txt",
                mime="text/plain"
            )
    else:
        st.info("Upload your resume and analyze it to get personalized career recommendations!")

# TAB 4: Project Review
with tab4:
    st.header("Project Review")
    
    if st.session_state.project_analysis:
        st.success("✅ Project analysis completed! Review the detailed insights below:")
        st.markdown("### 🎯 Project vs Job Offer Analysis")
        st.markdown(st.session_state.project_analysis)
        
        # Download option for project analysis
        st.download_button(
            label="📥 Download Project Analysis",
            data=st.session_state.project_analysis,
            file_name="project_analysis.txt",
            mime="text/plain"
        )
    else:
        st.info("Upload your resume and enable 'Project Review Against Job Offer' in the Resume Analysis tab to see project-specific insights here!")

# TAB 5: Interview Training
with tab5:
    render_interview_training(GROQ_API_KEY, st.session_state.resume_content)