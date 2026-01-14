# Agragrati - AI Resume & Job Search 🎯

An AI-powered resume analysis and job search platform built with Streamlit and Groq AI that provides comprehensive resume feedback and helps you find real job opportunities from multiple job boards and APIs.

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all prerequisites are met
3. Verify your API key is valid and active
4. Try restarting the application

---

## 🌟 Features Overview

### What Makes This Tool Special:

- **🎯 Targeted Analysis**: Provides job-specific recommendations
- **📊 Structured Output**: Organized feedback in 6 clear sections
- **🔍 Smart Job Search**: AI-powered job matching based on your resume
- **💼 Multi-Platform Search**: Search across LinkedIn, Indeed, ZipRecruiter, and more
- **⚡ Fast Processing**: Quick AI-powered analysis and job search
- **🔒 Privacy Focused**: Your resume data is processed securely
- **💰 Cost Effective**: Uses free Groq API with generous limits
- **🚀 Easy Deployment**: Multiple setup options for all skill levels

### Sample Analysis Output:

The tool provides feedback in these structured sections:
1. **Overall Impression** - Quick quality assessment
2. **Strengths** - What's working well
3. **Areas for Improvement** - Specific issues identified
4. **Recommendations** - Concrete improvement suggestions
5. **Action Items** - Prioritized tasks (High/Medium/Low)
6. **Final Score** - Numerical rating (1-10) with justification

Perfect for job seekers, career counselors, and HR professionals! 🎉

---

## ✨ New Features

### 🔍 Real Job Search Integration
- **Smart Resume-Based Search**: Automatically extracts skills from your resume and finds matching real jobs
- **Manual Job Search**: Search for specific job titles, keywords, or companies
- **Real API Integration**: Uses JSearch API (RapidAPI) and Adzuna API for live job data
- **Multi-Platform Coverage**: Searches across LinkedIn, Indeed, ZipRecruiter, Google Jobs, and more
- **Advanced Filtering**: Filter results by company, job type, location, and source
- **Export Results**: Download job search results as CSV for offline review
- **Fallback Mode**: Shows sample data if API keys are not configured

### 💡 Career Insights
- **Skill Extraction**: AI identifies key skills from your resume
- **Job Recommendations**: Personalized suggestions for job titles and companies to target
- **Career Guidance**: Strategic advice for improving your job search

---

## 📄 License

This project is open source and available under the MIT License.

## 🚀 Features

- **📁 Multi-Format Support**: Upload resumes in PDF or TXT format
- **🤖 AI-Powered Analysis**: Uses advanced Groq Llama models for intelligent feedback
- **📊 Structured Feedback**: Get organized analysis with scores and prioritized action items
- **🎯 Job-Specific Advice**: Tailored recommendations based on target job role
- **🔍 ATS Compatibility**: Checks for Applicant Tracking System optimization
- **⚡ Real-time Processing**: Fast analysis with detailed improvement suggestions
- **💼 Real Job Search**: Find live job opportunities from real APIs based on your resume or manual search
- **📈 Career Insights**: Get personalized career recommendations and skill analysis
- **🔗 API Integration**: Connects to JSearch API and Adzuna API for real-time job data

## 📋 Prerequisites

Before you can run this application, you need:

1. **Groq API Key** (Required)
   - Sign up at [console.groq.com](https://console.groq.com/keys)
   - Generate a free API key
   - Note: Free tier includes generous usage limits

2. **Choose Your Setup Method**:
   - **Option A**: Docker (Recommended - No Python setup needed)
   - **Option B**: Local Python Environment

---

## 🐳 Method A: Docker Deployment (Recommended)

### What You Need:
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop/))
- Your Groq API key

### Step-by-Step Setup:

1. **Download/Clone this project** to your computer

2. **Create the API key file**:
   - Open the `.env` file in the project folder
   - Replace `your_groq_api_key_here` with your actual API key:
   ```env
   GROQ_API_KEY=gsk_your_actual_api_key_here
   ```

3. **Open Terminal/Command Prompt** in the project folder

4. **Run the application**:
   ```bash
   docker-compose up --build
   ```
   
   *This will download dependencies, build the app, and start it automatically*

5. **Access the app**: Open your browser and go to http://localhost:8501

6. **To stop the app**: Press `Ctrl+C` in the terminal

6. **To stop the app**: Press `Ctrl+C` in the terminal

### Alternative Docker Commands (Advanced Users):

**Build the image manually**:
```bash
docker build -t resume-critiquer .
```

**Run container directly**:
```bash
docker run -p 8501:8501 --env-file .env resume-critiquer
```

---

## 🐍 Method B: Local Python Setup

### What You Need:
- Python 3.8 or higher ([Download here](https://www.python.org/downloads/))
- Your Groq API key

### Step-by-Step Setup:

1. **Download/Clone this project** to your computer

2. **Open Terminal/Command Prompt** in the project folder

3. **Create a virtual environment** (Recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up your API keys**:

   **Required - Groq API Key**:
   - Open the `.env` file
   - Replace `your_groq_api_key_here` with your actual API key:
   ```env
   GROQ_API_KEY=gsk_your_actual_api_key_here
   ```

   **Optional - Job Search API Keys** (for real job data):

   **JSearch API (via RapidAPI)** - 200 free requests/month:
   - Visit: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
   - Subscribe to the free plan
   - Copy your RapidAPI key to `.env`: `RAPIDAPI_KEY=your_key_here`

   **Adzuna API** - 25 free requests/hour:
   - Visit: https://developer.adzuna.com/
   - Create a free account and get your App ID and App Key
   - Add to `.env`:
     ```env
     ADZUNA_APP_ID=your_app_id_here
     ADZUNA_APP_KEY=your_app_key_here
     ```

   **Note**: If job search API keys are not provided, the app will show sample job data with a warning.

6. **Run the application**:
   ```bash
   streamlit run app.py
   ```

7. **Access the app**: Open your browser and go to http://localhost:8501

---

## 🎯 How to Use the Application

### 📄 Resume Analysis
1. **Upload Your Resume**:
   - Go to the **"📄 Resume Analysis"** tab
   - Click the file uploader and select your resume (PDF or TXT)
   - Wait for upload to complete

2. **Set Your Target (Optional but Recommended)**:
   - In the **Target Role / Job Offer** area you can:
     - Enter a **Target Job Title** (e.g., "Software Engineer")
     - Paste a **Job Description / Offer** (full posting text)
     - Or use **both** for the most precise guidance

3. **Run Analysis**:
   - Click **"Analyze Resume & (Optional) Project Fit"**
   - The app will:
     - Run a full resume review
     - Extract skills and generate job recommendations
     - Optionally analyze your projects vs. the pasted job offer (if provided)

4. **Review Results**:
   - **Overall Impression**: Quick summary of resume quality
   - **Strengths**: What's working well in your resume
   - **Areas for Improvement**: Specific issues to address
   - **Recommendations**: Concrete suggestions for enhancement
   - **Action Items**: Prioritized tasks (High/Medium/Low priority)
   - **Final Score**: Numerical rating with justification

### 🔍 Job Search
1. **Choose Search Method**:
   - **Smart Search**: Upload and analyze your resume first, then use AI to find matching jobs
   - **Manual Search**: Enter specific job titles, keywords, or company names

2. **Configure Search Parameters**:
   - **Location**: Enter city, state, or country (e.g., "San Francisco, CA")
   - **Job Type**: Filter by Full-time, Part-time, Contract, or Internship
   - **Results Count**: Choose how many results to retrieve (10-50)

3. **Search and Filter**:
   - Click "Search Jobs" to find opportunities
   - Use company and source filters to narrow results
   - Review job details including salary, location, and application links

4. **Export Results**:
   - Download search results as CSV for offline review
   - Save job listings for future reference

### 💡 Career Insights
1. **Automatic Generation**: After analyzing your resume, visit the "Career Insights" tab
2. **Review Recommendations**: Get personalized job search strategies
3. **Skill Analysis**: See key skills identified from your resume
4. **Career Guidance**: Follow strategic advice for improving your job search

### 🎤 Interview Training (Voice-Only, Hands-Free)
1. Go to the **"🎤 Interview Training"** tab.
2. In **Interview Setup**:
   - Choose an **Interview Type** (Technical, Behavioral, General, Custom).
   - Optionally set a **Target Position**.
   - Optionally enable **Use my resume for context** (if you already analyzed your resume).
3. Click **"🚀 Start Interview"**:
   - The AI interviewer will **ask the first question and speak it aloud**.
4. After each question:
   - Simply *start speaking* your answer.
   - The app records, transcribes, sends it to the interviewer, speaks the reply, and then **immediately listens again** for the next answer.
5. Use **"🛑 End Interview"** to stop:
   - The app generates and shows **interview feedback / summary**.
6. **Sidebar chat history**:
   - Left sidebar shows **Previous Interviews**.
   - Click any interview to open it.
   - Use **"🗑️ Clear Current Chat"** to reset the current interview while keeping the slot.
   - Use the small **🗑️ button** next to a chat to delete it entirely.
   - Use **"➕ New Chat"** to start a fresh interview thread.

### ✉️ Cover Letter Generator
1. Go to the **"Cover Letter Generator"** tab.
2. Make sure you have already run **Resume Analysis** so the app has your `resume_content`.
3. Fill the fields:
   - **Job Title (optional)**
   - **Company Name (optional)**
   - **Your Name / Email / Phone (optional)** – otherwise they’re extracted from the resume when possible.
   - Paste the **Job Description / Offer** in the text area.
4. Click **"Generate Cover Letter"**:
   - The app creates a **tailored, structured cover letter** that aligns your resume with the job offer.
5. Review and optionally tweak the text, then:
   - Use the **Download Cover Letter** button to save it as a `.txt` file.

---

## 🔧 Troubleshooting

### Common Issues:

**"API key not found" Error**:
- Ensure your `.env` file has the correct API key
- Check that there are no extra spaces or quotes around the key
- Restart the application after updating the API key

**"File has no content" Error**:
- Try a different PDF file
- Ensure your PDF contains selectable text (not just images)
- Try converting to TXT format if PDF doesn't work

**Job Search Issues**:
- If no jobs are found, try different keywords or broader location
- Some job sites may temporarily block requests - try again later
- Ensure you have a stable internet connection for job scraping

**Docker Issues**:
- Ensure Docker Desktop is running
- Try `docker-compose down` then `docker-compose up --build`
- Check if port 8501 is already in use

**Slow Analysis/Job Search**:
- Resume analysis: Wait up to 60 seconds for complex resumes
- Job search: May take 30-60 seconds depending on number of results
- Check your internet connection

---

## ⚙️ Technical Details

- **Framework**: Streamlit for web interface
- **AI Model**: Groq Llama-3.3-70b-versatile for resume analysis and skill extraction
- **Job Search APIs**:
  - JSearch API (via RapidAPI) - 200 free requests/month
  - Adzuna API - 25 free requests/hour
  - Fallback to sample data if APIs not configured
- **File Processing**: PyPDF2 for PDF extraction
- **Data Processing**: Pandas for job data manipulation and filtering
- **HTTP Requests**: Requests library for API calls
- **Environment**: Python 3.8+ with virtual environment support
- **Deployment**: Docker containerized for easy deployment
- **Job Platforms**: LinkedIn, Indeed, ZipRecruiter, Google Jobs, and more (via APIs)

## 🤖 Supported AI Models

The application uses Groq's powerful language models:
- **Primary**: `llama-3.3-70b-versatile` (best quality)
- **Alternative**: `llama3-70b-8192`, `llama-3.1-8b-instant`

---

## � Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all prerequisites are met
3. Verify your API key is valid and active
4. Try restarting the application

---
