import groq
from typing import Optional
import streamlit as st
from datetime import datetime


class CoverLetterGenerator:
    def __init__(self, groq_api_key: str):
        """Initialize the CoverLetterGenerator with Groq API key."""
        self.groq_client = groq.Client(api_key=groq_api_key)
    
    def generate_cover_letter(
        self, 
        resume_content: str, 
        job_offer: str,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None,
        your_name: Optional[str] = None,
        your_email: Optional[str] = None,
        your_phone: Optional[str] = None
    ) -> str:
        """
        Generate a personalized cover letter based on resume and job offer.
        
        Args:
            resume_content: The full text content of the resume
            job_offer: The job description/offer text
            job_title: Optional job title (will be extracted from offer if not provided)
            company_name: Optional company name (will be extracted from offer if not provided)
            your_name: Optional name to use in the cover letter
            your_email: Optional email to include
            your_phone: Optional phone number to include
        
        Returns:
            Generated cover letter text
        """
        if not resume_content or not resume_content.strip():
            return "Error: Resume content is required to generate a cover letter."
        
        if not job_offer or not job_offer.strip():
            return "Error: Job offer/description is required to generate a cover letter."
        
        # Extract contact info from resume if not provided
        if not your_name:
            your_name = self._extract_name_from_resume(resume_content)
        if not your_email:
            your_email = self._extract_email_from_resume(resume_content)
        if not your_phone:
            your_phone = self._extract_phone_from_resume(resume_content)
        
        # Build the prompt for cover letter generation
        prompt = f"""You are an expert career counselor and professional cover letter writer with 15+ years of experience helping candidates craft compelling, personalized cover letters.

**TASK:** Generate a professional, compelling cover letter that:
1. Is tailored specifically to the job description provided
2. Highlights relevant experience and skills from the candidate's resume
3. Demonstrates clear alignment between the candidate's background and job requirements
4. Is professional, concise (3-4 paragraphs), and engaging
5. Uses specific examples from the resume to support claims
6. Shows enthusiasm for the role and company

**COVER LETTER STRUCTURE:**
- Professional header with candidate contact information (if provided)
- Date
- Hiring Manager/Company Address (use "Hiring Manager" if specific name not available)
- Subject line (if applicable)
- Opening paragraph: Strong hook that mentions the specific position and shows enthusiasm
- Body paragraph(s): 1-2 paragraphs connecting resume experience to job requirements with specific examples
- Closing paragraph: Reiterate interest, mention next steps, and professional closing

**RESUME CONTENT:**
{resume_content[:2000]}

**JOB DESCRIPTION/OFFER:**
{job_offer[:2000]}

**ADDITIONAL CONTEXT:**
- Job Title: {job_title if job_title else "Extract from job description"}
- Company Name: {company_name if company_name else "Extract from job description"}
- Candidate Name: {your_name if your_name else "[Your Name]"}
- Email: {your_email if your_email else "[Your Email]"}
- Phone: {your_phone if your_phone else "[Your Phone]"}

**INSTRUCTIONS:**
- Make the cover letter specific and personalized - avoid generic templates
- Use action verbs and quantifiable achievements from the resume
- Address key requirements from the job description
- Keep it professional but warm and engaging
- Ensure proper formatting with clear paragraphs
- Do NOT include placeholders like [Your Name] if actual information is provided
- If contact information is not provided, use appropriate placeholders
- The cover letter should be ready to use (just review and customize minor details)

Generate the complete cover letter now:"""

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert cover letter writer specializing in creating personalized, compelling cover letters that help candidates stand out to employers."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            cover_letter = response.choices[0].message.content.strip()
            return cover_letter
        
        except Exception as e:
            return f"Error generating cover letter: {str(e)}"
    
    def _extract_name_from_resume(self, resume_text: str) -> Optional[str]:
        """Extract candidate name from resume (usually first line or after 'Name:' label)."""
        lines = resume_text.split('\n')[:10]  # Check first 10 lines
        for line in lines:
            line = line.strip()
            if line and len(line.split()) <= 4 and len(line) > 3:
                # Likely a name if it's short and in first few lines
                if any(keyword in line.lower() for keyword in ['name:', 'candidate:', 'applicant:']):
                    return line.split(':', 1)[1].strip()
                # If no label, first substantial line might be name
                if not any(keyword in line.lower() for keyword in ['email', 'phone', 'address', 'objective', 'summary']):
                    return line
        return None
    
    def _extract_email_from_resume(self, resume_text: str) -> Optional[str]:
        """Extract email address from resume."""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, resume_text)
        return matches[0] if matches else None
    
    def _extract_phone_from_resume(self, resume_text: str) -> Optional[str]:
        """Extract phone number from resume."""
        import re
        # Common phone number patterns
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US format
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
        ]
        for pattern in phone_patterns:
            matches = re.findall(pattern, resume_text)
            if matches:
                return matches[0]
        return None
    
    def generate_cover_letter_batch(
        self,
        resume_content: str,
        job_offers: list,
        **kwargs
    ) -> dict:
        """
        Generate multiple cover letters for different job offers.
        
        Args:
            resume_content: The full text content of the resume
            job_offers: List of job offer dictionaries with 'offer' key and optionally 'title', 'company'
            **kwargs: Additional parameters (your_name, your_email, etc.)
        
        Returns:
            Dictionary mapping job titles to cover letters
        """
        results = {}
        for i, job_data in enumerate(job_offers):
            if isinstance(job_data, dict):
                offer = job_data.get('offer', '')
                title = job_data.get('title', f"Position {i+1}")
                company = job_data.get('company', '')
            else:
                offer = str(job_data)
                title = f"Position {i+1}"
                company = ''
            
            cover_letter = self.generate_cover_letter(
                resume_content=resume_content,
                job_offer=offer,
                job_title=title,
                company_name=company,
                **kwargs
            )
            results[title] = cover_letter
        
        return results


def render_cover_letter_generator(groq_api_key: str, resume_content: str):
    st.header("Cover Letter Generator")
    st.markdown("Generate a tailored cover letter from your resume and a job offer.")

    if not groq_api_key:
        st.error("GROQ_API_KEY not found. Please check your .env file.")
        return

    if not resume_content:
        st.info("Upload and analyze your resume in the Resume Analysis tab first.")
        return

    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Job Title (optional)")
        company_name = st.text_input("Company Name (optional)")
    with col2:
        your_name = st.text_input("Your Name (optional)")
        your_email = st.text_input("Your Email (optional)")
        your_phone = st.text_input("Your Phone (optional)")

    job_offer = st.text_area(
        "Job Description / Offer",
        placeholder="Paste the job description here...",
        height=220
    )

    if st.button("Generate Cover Letter", type="primary"):
        with st.spinner("Generating cover letter..."):
            generator = CoverLetterGenerator(groq_api_key)
            cover_letter = generator.generate_cover_letter(
                resume_content=resume_content,
                job_offer=job_offer,
                job_title=job_title or None,
                company_name=company_name or None,
                your_name=your_name or None,
                your_email=your_email or None,
                your_phone=your_phone or None,
            )

        st.markdown("### Generated Cover Letter")
        st.text_area("Cover Letter", value=cover_letter, height=350)

        st.download_button(
            label="📥 Download Cover Letter",
            data=cover_letter,
            file_name=f"cover_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
        )
