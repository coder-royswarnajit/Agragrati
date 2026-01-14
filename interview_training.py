import streamlit as st
import speech_recognition as sr
import pyttsx3
import groq
import os
from dotenv import load_dotenv
import threading
from datetime import datetime
import whisper


load_dotenv()

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

whisper_model = load_whisper()


def listen_audio():
    """Listen to audio input from microphone."""
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            # 🎤 Listening... Please speak now
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            
            # Processing your speech...
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

def render_interview_training(groq_api_key: str, resume_content: str):
    """Render the interview training interface."""
    
    # Initialize session state for multiple chats
    if 'all_chats' not in st.session_state:
        st.session_state.all_chats = {}  # {chat_id: {history, context, metadata}}
    if 'current_chat_id' not in st.session_state:
        st.session_state.current_chat_id = None
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    
    # Get current chat data
    current_chat = st.session_state.all_chats.get(st.session_state.current_chat_id) if st.session_state.current_chat_id else None
    interview_history = current_chat['history'] if current_chat else []
    interview_context = current_chat['context'] if current_chat else ""
    
    # Sidebar for chat history
    with st.sidebar:
        st.header("💬 Interview History")
        
        # New Chat button
        if st.button("➕ New Chat", type="primary", use_container_width=True):
            # Create new chat
            new_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.session_state.all_chats[new_chat_id] = {
                'history': [],
                'context': "",
                'metadata': {
                    'title': f"Interview {len(st.session_state.all_chats) + 1}",
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'interview_type': "",
                    'job_position': ""
                }
            }
            st.session_state.current_chat_id = new_chat_id
            st.session_state.interview_started = False
            st.rerun()
        
        st.markdown("---")
        
        # Clear current chat button
        if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.all_chats:
            if st.button("🗑️ Clear Current Chat", use_container_width=True, type="secondary"):
                # Clear the current chat's history but keep the chat
                current_chat = st.session_state.all_chats[st.session_state.current_chat_id]
                current_chat['history'] = []
                current_chat['context'] = ""
                current_chat['metadata']['interview_type'] = ""
                current_chat['metadata']['job_position'] = ""
                st.session_state.interview_started = False
                st.rerun()
        
        st.markdown("---")
        
        # Display all chats
        if st.session_state.all_chats:
            st.markdown("### Previous Interviews")
            for chat_id, chat_data in reversed(list(st.session_state.all_chats.items())):
                metadata = chat_data.get('metadata', {})
                title = metadata.get('title', f"Chat {chat_id}")
                created_at = metadata.get('created_at', '')
                message_count = len(chat_data.get('history', []))
                
                # Create columns for chat button and delete button
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Highlight current chat
                    is_active = chat_id == st.session_state.current_chat_id
                    button_label = f"{'▶️ ' if is_active else ''}{title}"
                    if created_at:
                        button_label += f"\n📅 {created_at.split()[0]}"
                    if message_count > 0:
                        button_label += f" | 💬 {message_count} messages"
                    
                    if st.button(button_label, key=f"chat_{chat_id}", use_container_width=True):
                        st.session_state.current_chat_id = chat_id
                        st.session_state.interview_started = False
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"delete_{chat_id}", help="Delete this chat"):
                        # If deleting current chat, switch to another or None
                        if chat_id == st.session_state.current_chat_id:
                            remaining_chats = [cid for cid in st.session_state.all_chats.keys() if cid != chat_id]
                            if remaining_chats:
                                st.session_state.current_chat_id = remaining_chats[-1]
                            else:
                                st.session_state.current_chat_id = None
                        del st.session_state.all_chats[chat_id]
                        st.session_state.interview_started = False
                        st.rerun()
        else:
            st.info("No interviews yet. Click 'New Chat' to start!")
    
    # Main content area
    st.header("🎤 AI Interview Training")
    st.markdown("""
    Practice your interview skills with our AI interviewer in **hands-free voice mode**.
    - 🎙️ Speak your answers using your microphone
    - The interviewer will reply, speak the response, and listening will resume automatically
    """)
    
    # Ensure we have a current chat
    if st.session_state.current_chat_id is None:
        # Create a default chat if none exists
        new_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.all_chats[new_chat_id] = {
            'history': [],
            'context': "",
            'metadata': {
                'title': f"Interview {len(st.session_state.all_chats) + 1}",
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'interview_type': "",
                'job_position': ""
            }
        }
        st.session_state.current_chat_id = new_chat_id
        st.rerun()
    
    # Update current chat reference
    current_chat = st.session_state.all_chats[st.session_state.current_chat_id]
    interview_history = current_chat['history']
    interview_context = current_chat['context']
    
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
        
        context_text = ""
        if use_resume and resume_content:
            context_text = f"Candidate's Resume:\n{resume_content[:1000]}..."
        
        if st.button("🚀 Start Interview", type="primary"):
            st.session_state.interview_started = True
            
            # Update chat metadata
            current_chat['context'] = context_text
            current_chat['metadata']['interview_type'] = interview_type
            current_chat['metadata']['job_position'] = job_position
            if job_position:
                current_chat['metadata']['title'] = f"{interview_type} - {job_position}"
            else:
                current_chat['metadata']['title'] = interview_type
            
            # Generate opening question based on interview type
            opening_prompt = f"Start a {interview_type.lower()}"
            if job_position:
                opening_prompt += f" for a {job_position} position"
            opening_prompt += ". Introduce yourself briefly and ask the first interview question."
            
            opening_response = get_interview_response(
                opening_prompt,
                groq_api_key,
                context_text
            )
            
            current_chat['history'].append({
                'role': 'interviewer',
                'content': opening_response,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            
            # Speak the opening interviewer message immediately
            if opening_response:
                with st.spinner("🔊 Interviewer is speaking..."):
                    speak_text(opening_response)
            st.rerun()
    
    else:
        # Active interview interface (voice only)
        st.markdown("### 💬 Interview in Progress (Voice Only)")
        
        # Display interview history
        st.markdown("#### Conversation History")
        chat_container = st.container()
        
        with chat_container:
            for msg in interview_history:
                if msg['role'] == 'interviewer':
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <strong>🤵 Interviewer ({msg['timestamp']}):</strong><br/>
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                elif msg['role'] == 'candidate':
                    st.markdown(f"""
                    <div style="background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <strong>👤 You ({msg['timestamp']}):</strong><br/>
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                elif msg['role'] == 'summary':
                    st.markdown(f"""
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <strong>📊 Summary ({msg['timestamp']}):</strong><br/>
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info("🎙️ Voice mode is active. After each interviewer question, speak your answer; the system will transcribe, respond, and keep listening automatically.")
        
        with col2:
            end_btn = st.button("🛑 End Interview", type="secondary")
        
        # End interview before starting a new listen cycle
        if end_btn:
            st.session_state.interview_started = False
            
            # Generate interview summary
            if len(interview_history) > 2:
                with st.spinner("Generating interview feedback..."):
                    summary_prompt = "Based on this interview conversation, provide a brief summary of the candidate's performance, strengths, and areas for improvement:\n\n"
                    summary_prompt += "\n\n".join([
                        f"{'Interviewer' if m['role'] == 'interviewer' else 'Candidate'}: {m['content']}"
                        for m in interview_history
                    ])
                    
                    summary = get_interview_response(summary_prompt, groq_api_key)
                    
                    current_chat['history'].append({
                        'role': 'summary',
                        'content': summary,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
            
            st.rerun()
        
        # Continuous hands-free loop: listen → transcribe → send → speak → listen again
        if st.session_state.interview_started:
            with st.spinner("Preparing microphone and listening..."):
                user_text, error = listen_audio()
            
            if error:
                st.error(error)
            elif user_text:
                st.success(f"✅ You said: {user_text}")
                
                # Add user response to history
                current_chat['history'].append({
                    'role': 'candidate',
                    'content': user_text,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                # Get interviewer response
                with st.spinner("Interviewer is thinking..."):
                    context_messages = "\n\n".join([
                        f"{'Interviewer' if m['role'] == 'interviewer' else 'Candidate'}: {m['content']}"
                        for m in current_chat['history'][-5:]
                    ])
                    
                    interviewer_response = get_interview_response(
                        f"Based on this conversation:\n{context_messages}\n\nProvide your next question or feedback.",
                        groq_api_key,
                        interview_context
                    )
                    
                    current_chat['history'].append({
                        'role': 'interviewer',
                        'content': interviewer_response,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # Speak the response
                    st.info("🔊 Interviewer is speaking...")
                    speak_text(interviewer_response)
            
            # Immediately rerun so the app listens again, creating a continuous hands-free flow
            st.rerun()
        
        # Download transcript
        if len(interview_history) > 0:
            st.markdown("---")
            transcript = "\n\n".join([
                f"[{msg['timestamp']}] {'Interviewer' if msg['role'] == 'interviewer' else 'Candidate' if msg['role'] == 'candidate' else 'Summary'}:\n{msg['content']}"
                for msg in interview_history
            ])
            
            st.download_button(
                label="📥 Download Interview Transcript",
                data=transcript,
                file_name=f"interview_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    # Show interview summary if interview ended
    if not st.session_state.interview_started and interview_history:
        summary_msg = next(
            (msg for msg in reversed(interview_history) if msg.get('role') == 'summary'),
            None
        )
        
        if summary_msg:
            st.markdown("### 📊 Interview Feedback")
            st.success(summary_msg['content'])
        
        if st.button("🔄 Start New Interview"):
            # Create a new chat for the new interview
            new_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.session_state.all_chats[new_chat_id] = {
                'history': [],
                'context': "",
                'metadata': {
                    'title': f"Interview {len(st.session_state.all_chats) + 1}",
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'interview_type': "",
                    'job_position': ""
                }
            }
            st.session_state.current_chat_id = new_chat_id
            st.session_state.interview_started = False
            st.rerun()