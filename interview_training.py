import streamlit as st
import speech_recognition as sr
import pyttsx3
import groq
import os
from dotenv import load_dotenv
import threading
from datetime import datetime

load_dotenv()

def listen_audio():
    """Listen to audio input from microphone."""
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Please speak now")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            
            st.info("🔄 Processing your speech...")
            text = recognizer.recognize_google(audio)
            return text, None
    
    except sr.WaitTimeoutError:
        return None, "⏱️ No speech detected (timeout). Please try again."
    except sr.UnknownValueError:
        return None, "❌ Sorry, I couldn't understand that. Please speak more clearly."
    except sr.RequestError:
        return None, "❌ Speech recognition service is unavailable."
    except Exception as e:
        return None, f"❌ An error occurred: {str(e)}"

def get_interview_response(user_input: str, groq_api_key: str, context: str = ""):
    """Get AI interviewer response using Groq."""
    if not user_input:
        return None
    
    try:
        client = groq.Client(api_key=groq_api_key)
        
        system_prompt = """You are an experienced technical interviewer conducting a professional interview. 
Your role is to:
- Ask thoughtful, relevant questions about the candidate's experience and skills
- Evaluate responses critically but fairly
- Provide constructive feedback when appropriate
- Probe deeper into technical concepts to assess understanding
- Maintain a professional yet friendly demeanor
- Ask follow-up questions based on the candidate's answers
Keep your responses concise and focused (2-4 sentences)."""

        if context:
            system_prompt += f"\n\nAdditional context about the candidate:\n{context}"
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def speak_text(text: str):
    """Convert text to speech."""
    if not text:
        return False
    
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 150)  # Speed of speech
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")
        return False

def render_interview_training(groq_api_key: str, resume_content: str = None):
    """Render the interview training interface."""
    
    st.header("🎤 AI Interview Training")
    st.markdown("""
    Practice your interview skills with our AI interviewer! You can either:
    - 🎙️ **Voice Mode**: Speak your answers using your microphone
    - ⌨️ **Text Mode**: Type your responses
    """)
    
    # Initialize session state for interview history
    if 'interview_history' not in st.session_state:
        st.session_state.interview_history = []
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    if 'interview_context' not in st.session_state:
        st.session_state.interview_context = ""
    
    # Interview setup
    if not st.session_state.interview_started:
        st.markdown("### 📋 Interview Setup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            interview_type = st.selectbox(
                "Interview Type",
                ["Technical Interview", "Behavioral Interview", "General Interview", "Custom"]
            )
        
        with col2:
            job_position = st.text_input(
                "Target Position (optional)",
                placeholder="e.g., Software Engineer, Data Scientist"
            )
        
        # Option to use resume context
        use_resume = st.checkbox(
            "Use my resume for context",
            value=bool(resume_content),
            disabled=not resume_content
        )
        
        if use_resume and resume_content:
            st.session_state.interview_context = f"Candidate's Resume:\n{resume_content[:1000]}..."
        
        if st.button("🚀 Start Interview", type="primary"):
            st.session_state.interview_started = True
            
            # Generate opening question based on interview type
            opening_prompt = f"Start a {interview_type.lower()}"
            if job_position:
                opening_prompt += f" for a {job_position} position"
            opening_prompt += ". Introduce yourself briefly and ask the first interview question."
            
            opening_response = get_interview_response(
                opening_prompt,
                groq_api_key,
                st.session_state.interview_context
            )
            
            st.session_state.interview_history.append({
                'role': 'interviewer',
                'content': opening_response,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            st.rerun()
    
    else:
        # Active interview interface
        st.markdown("### 💬 Interview in Progress")
        
        # Display interview history
        st.markdown("#### Conversation History")
        chat_container = st.container()
        
        with chat_container:
            for msg in st.session_state.interview_history:
                if msg['role'] == 'interviewer':
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <strong>🤵 Interviewer ({msg['timestamp']}):</strong><br/>
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <strong>👤 You ({msg['timestamp']}):</strong><br/>
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Input mode selection
        input_mode = st.radio(
            "Choose your input method:",
            ["⌨️ Text Input", "🎙️ Voice Input"],
            horizontal=True
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        if input_mode == "⌨️ Text Input":
            with col1:
                user_text = st.text_area(
                    "Your Response",
                    placeholder="Type your answer here...",
                    height=100,
                    key="user_response_input"
                )
            
            with col2:
                submit_btn = st.button("📤 Submit Response", type="primary")
                speak_btn = st.button("🔊 Read Aloud")
            
            with col3:
                end_btn = st.button("🛑 End Interview", type="secondary")
            
            if submit_btn and user_text:
                # Add user response to history
                st.session_state.interview_history.append({
                    'role': 'candidate',
                    'content': user_text,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                # Get interviewer response
                with st.spinner("Interviewer is thinking..."):
                    # Build conversation context
                    context_messages = "\n\n".join([
                        f"{'Interviewer' if m['role'] == 'interviewer' else 'Candidate'}: {m['content']}"
                        for m in st.session_state.interview_history[-5:]  # Last 5 messages
                    ])
                    
                    interviewer_response = get_interview_response(
                        f"Based on this conversation:\n{context_messages}\n\nProvide your next question or feedback.",
                        groq_api_key,
                        st.session_state.interview_context
                    )
                    
                    st.session_state.interview_history.append({
                        'role': 'interviewer',
                        'content': interviewer_response,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                
                st.rerun()
            
            if speak_btn and st.session_state.interview_history:
                last_interviewer_msg = next(
                    (msg for msg in reversed(st.session_state.interview_history) 
                     if msg['role'] == 'interviewer'),
                    None
                )
                if last_interviewer_msg:
                    with st.spinner("🔊 Speaking..."):
                        speak_text(last_interviewer_msg['content'])
        
        else:  # Voice Input
            with col1:
                st.info("Click the button below and speak your answer when prompted.")
            
            with col2:
                voice_btn = st.button("🎤 Start Recording", type="primary")
            
            with col3:
                end_btn = st.button("🛑 End Interview", type="secondary")
            
            if voice_btn:
                with st.spinner("Preparing microphone..."):
                    user_text, error = listen_audio()
                
                if error:
                    st.error(error)
                elif user_text:
                    st.success(f"✅ You said: {user_text}")
                    
                    # Add user response to history
                    st.session_state.interview_history.append({
                        'role': 'candidate',
                        'content': user_text,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # Get interviewer response
                    with st.spinner("Interviewer is thinking..."):
                        context_messages = "\n\n".join([
                            f"{'Interviewer' if m['role'] == 'interviewer' else 'Candidate'}: {m['content']}"
                            for m in st.session_state.interview_history[-5:]
                        ])
                        
                        interviewer_response = get_interview_response(
                            f"Based on this conversation:\n{context_messages}\n\nProvide your next question or feedback.",
                            groq_api_key,
                            st.session_state.interview_context
                        )
                        
                        st.session_state.interview_history.append({
                            'role': 'interviewer',
                            'content': interviewer_response,
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        })
                        
                        # Speak the response
                        st.info("🔊 Interviewer is speaking...")
                        speak_text(interviewer_response)
                    
                    st.rerun()
        
        # End interview button action
        if end_btn:
            st.session_state.interview_started = False
            
            # Generate interview summary
            if len(st.session_state.interview_history) > 2:
                with st.spinner("Generating interview feedback..."):
                    summary_prompt = "Based on this interview conversation, provide a brief summary of the candidate's performance, strengths, and areas for improvement:\n\n"
                    summary_prompt += "\n\n".join([
                        f"{'Interviewer' if m['role'] == 'interviewer' else 'Candidate'}: {m['content']}"
                        for m in st.session_state.interview_history
                    ])
                    
                    summary = get_interview_response(summary_prompt, groq_api_key)
                    
                    st.session_state.interview_history.append({
                        'role': 'summary',
                        'content': summary,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
            
            st.rerun()
        
        # Download transcript
        if len(st.session_state.interview_history) > 0:
            st.markdown("---")
            transcript = "\n\n".join([
                f"[{msg['timestamp']}] {'Interviewer' if msg['role'] == 'interviewer' else 'Candidate' if msg['role'] == 'candidate' else 'Summary'}:\n{msg['content']}"
                for msg in st.session_state.interview_history
            ])
            
            st.download_button(
                label="📥 Download Interview Transcript",
                data=transcript,
                file_name=f"interview_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    # Show interview summary if interview ended
    if not st.session_state.interview_started and st.session_state.interview_history:
        summary_msg = next(
            (msg for msg in reversed(st.session_state.interview_history) if msg.get('role') == 'summary'),
            None
        )
        
        if summary_msg:
            st.markdown("### 📊 Interview Feedback")
            st.success(summary_msg['content'])
        
        if st.button("🔄 Start New Interview"):
            st.session_state.interview_history = []
            st.session_state.interview_started = False
            st.session_state.interview_context = ""
            st.rerun()