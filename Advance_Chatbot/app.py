import os
import json
import base64
from flask import Flask, render_template, request, jsonify, session, Response
from werkzeug.utils import secure_filename
import google.generativeai as genai
from dotenv import load_dotenv
import uuid
import markdown
from script_detector import script_detector

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# System instruction for Medicynth
SYSTEM_INSTRUCTION = """You are **Medicynth**, a professional, reliable, evidence-minded health assistant built to be embedded in a Flask/Python web app. Your responses power a Copilot-like chatbot UI (purple, modern, slightly glowing aesthetic). **Do NOT return code** — only natural language replies. Follow these instructions exactly:

**Identity & tone**
- Persona: Medicynth — professional, calm, empathetic, concise. Helpful but never casual or jokey.
- Style: Copilot-like: proactive, stepwise, actionable suggestions when appropriate, short summaries up front, then optional deeper explanation.
- UI hint (for developers): Assume a **purple, professional theme** with a subtle glow on CTA elements — keep responses formatted so they display cleanly in that UI (use short paragraphs, clear headings when needed, bullet lists for steps).

**CRITICAL SCRIPT PRESERVATION RULE**
- **MOST IMPORTANT**: You will receive a SCRIPT PRESERVATION INSTRUCTION before each user message
- **FOLLOW THE SCRIPT INSTRUCTION EXACTLY** - this is the #1 priority
- If told to use DEVANAGARI → use only देवनागरी characters (अ, आ, इ, ई, क, ख, etc.)
- If told to use ROMANIZED/LATIN → use only English letters (a, aa, i, ee, k, kh, g, gh, etc.)
- If told to use ARABIC → use only Arabic script (ا, ب, ت, etc.)
- **NEVER change the script type** - this breaks the user experience
- **RESPOND IN THE EXACT SAME LANGUAGE** as detected by the script preservation instruction

**MULTI-LANGUAGE SUPPORT**
- Always respond in the EXACT SAME LANGUAGE as the user input
- Automatically detect the language and respond naturally
- Use appropriate medical terminology for each language
- For Indian languages, use proper cultural context

**Scope & allowed content**
- **ONLY** answer health-related questions: medical conditions, symptoms, treatments, medication basics, diagnostics concepts, lifestyle, prevention, mental health guidance, interpretation of public health info. You can analyze images of rashes, pills, medical equipment, videos of symptoms or exercises, and documents containing health information, etc.
- If a user query is outside health, politely refuse in the user's language and script:
  - English: "I'm Medicynth — I can only help with health, medical, or wellness questions."
  - Hindi (Devanagari): "मैं मेडिसिंथ हूं — मैं केवल स्वास्थ्य, चिकित्सा या कल्याण संबंधी प्रश्नों में मदद कर सकता हूं।"
  - Hindi (Romanized): "Main Medicynth hoon — main sirf swasthya, chikitsa ya kalyan sambandhi prashnon mein madad kar sakta hoon."
  - Marathi (Devanagari): "मी मेडिसिंथ आहे — मी फक्त आरोग्य, वैद्यकीय किंवा कल्याण संबंधित प्रश्नांमध्ये मदत करू शकतो।"
  - Marathi (Romanized): "Mi Medicynth aahe — mi fakt aarogya, vaidyakiya kinva kalyan sambhandhit prashnaammadhye madatha karu shakato."
- Never invent credentials or claim to be a licensed physician.

**Medical safety rules**
- For emergencies, provide appropriate guidance in user's language and script:
  - English: "If someone is in immediate danger, call your local emergency number now or go to the nearest emergency department."
  - Hindi (Devanagari): "यदि कोई तत्काल खतरे में है, तो अभी अपना स्थानीय आपातकालीन नंबर डायल करें।"
  - Hindi (Romanized): "Yadi koi tatkal khatre mein hai, to abhi apna sthaniya apatkalin number dial karein."
  - Marathi (Devanagari): "जर कोणी तात्काळ धोक्यात असेल, तर आता तुमचा स्थानिक आपत्कालीन क्रमांक कॉल करा।"
  - Marathi (Romanized): "Jar koni tatkal dhokyat asel, tar aata tumcha sthanik apatkalin kramank call kara."
- Always include safety disclaimers in the user's language and script
- Encourage consulting healthcare professionals in appropriate language and script

**Final behavior rule**
- **CRITICAL**: Always follow the SCRIPT PRESERVATION INSTRUCTION provided before each user message
- This is the most important rule - failure to follow script instructions breaks the user experience
- Respond in the exact same language and script as the user input"""

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'tiff', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', '3gp', 'zip', 'rar', '7z', 'tar', 'gz', 'pdf', 'doc', 'docx', 'txt'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

def get_user_friendly_error(error_message):
    """Convert technical error messages to user-friendly ones"""
    error_str = str(error_message).lower()
    
    # API quota/billing errors
    if '429' in error_str and 'quota' in error_str:
        if 'free_tier' in error_str:
            return "Daily free usage limit reached. You can try again tomorrow or upgrade to a paid plan. 📊"
        return "I'm currently experiencing high usage. Please try again in a few minutes. 🔄"
    elif 'quota' in error_str or 'billing' in error_str:
        return "Service temporarily unavailable. Please try again later. ⏰"
    
    # Authentication errors
    elif 'authentication' in error_str or 'api key' in error_str or '401' in error_str:
        return "Service configuration issue. Please contact support. 🔧"
    
    # Network/connection errors
    elif 'network' in error_str or 'connection' in error_str or 'timeout' in error_str:
        return "Connection issue. Please check your internet and try again. 🌐"
    
    # Rate limit errors
    elif 'rate limit' in error_str or '429' in error_str:
        return "Too many requests. Please wait a moment before trying again. ⏳"
    
    # Server errors
    elif '500' in error_str or 'server error' in error_str:
        return "Service temporarily down. Please try again in a few minutes. 🛠️"
    
    # Generic fallback
    else:
        return "Something went wrong. Please try again or contact support if the issue persists. 💬"

def clean_ai_response(response_text):
    """Remove internal system instructions from AI response"""
    if not response_text:
        return response_text
    
    # Remove script preservation instructions that might leak into response
    lines = response_text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip lines that contain internal instructions
        if (
            line.startswith('SCRIPT PRESERVATION INSTRUCTION:') or
            line.startswith('CRITICAL SCRIPT PRESERVATION RULE:') or
            'ROMANIZED/LATIN' in line and 'script detected:' in line.lower() or
            'DEVANAGARI' in line and 'script detected:' in line.lower() or
            line.startswith('- User has written in') or
            line.startswith('- You MUST respond in') or
            line.startswith('- DO NOT use') or
            line.startswith('- Use English letters:') or
            line.startswith('- Example for') or
            'User input script detected:' in line
        ):
            continue
        
        # Keep all other lines
        if line:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_chat_session():
    """Get or create chat session for current user"""
    if 'chat_id' not in session:
        session['chat_id'] = str(uuid.uuid4())
        session['chat_history'] = []  # Store simplified history
    
    # Create new Gemini model instance
    model = genai.GenerativeModel(
        'gemini-2.0-flash-exp',
        system_instruction=SYSTEM_INSTRUCTION
    )
    
    # Start chat with history context
    chat = model.start_chat()
    
    # Rebuild context from stored history
    if session.get('chat_history'):
        context_parts = []
        context_parts.append({'text': 'Previous conversation context:'})
        
        for i, msg in enumerate(session['chat_history'][-10:]):  # Last 10 messages only
            if msg['role'] == 'user':
                context_parts.append({'text': f"User ({i+1}): {msg['content']}"})
            else:
                context_parts.append({'text': f"Assistant ({i+1}): {msg['content'][:200]}..."})
        
        context_parts.append({'text': 'Current conversation:'})
        
        # Send context as initial message (won't be visible to user)
        try:
            chat.send_message(context_parts)
        except:
            pass  # If context fails, continue without it
    
    return chat

def add_to_history(role, content, script_info=None):
    """Add message to chat history"""
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    # Keep only essential info to avoid session size issues
    history_entry = {
        'role': role,
        'content': content[:500],  # Truncate long messages
        'timestamp': str(uuid.uuid4())[:8],  # Short timestamp
    }
    
    if script_info:
        history_entry['script'] = script_info
    
    session['chat_history'].append(history_entry)
    
    # Keep only last 20 messages to prevent session overflow
    if len(session['chat_history']) > 20:
        session['chat_history'] = session['chat_history'][-20:]
    
    session.modified = True

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        image_data = data.get('image')
        
        if not message and not image_data:
            return jsonify({'error': 'Message or image required'}), 400
        
        # Prepare parts for the message
        parts = []
        detected_script = 'unknown'  # Initialize variable
        
        # Add script preservation instruction if there's text
        if message:
            detected_script = script_detector.detect_script(message)
            script_instruction = script_detector.create_script_instruction(detected_script, message)
            parts.append({'text': script_instruction})
            
            # Add user message to history before processing
            add_to_history('user', message, detected_script)
        
        if image_data:
            # Process base64 image
            try:
                image_bytes = base64.b64decode(image_data['data'])
                parts.append({
                    'inline_data': {
                        'mime_type': image_data['mimeType'],
                        'data': image_data['data']
                    }
                })
                # Add image info to history
                add_to_history('user', f"[Image uploaded: {image_data.get('filename', 'unknown')}]")
            except Exception as e:
                friendly_error = get_user_friendly_error(str(e))
                return jsonify({'error': friendly_error}), 400
        
        if message:
            parts.append({'text': f"User message: {message}"})
        
        # Get chat session and send message
        chat = get_chat_session()
        response = chat.send_message(parts)
        
        # Clean the response to remove internal instructions
        cleaned_response = clean_ai_response(response.text)
        
        # Add AI response to history
        add_to_history('assistant', cleaned_response, detected_script)
        
        return jsonify({
            'response': cleaned_response,
            'detected_script': detected_script,
            'chat_id': session.get('chat_id'),
            'history_length': len(session.get('chat_history', [])),
            'success': True
        })
        
    except Exception as e:
        # Use user-friendly error message
        friendly_error = get_user_friendly_error(str(e))
        return jsonify({'error': friendly_error}), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Handle streaming chat messages"""
    def generate():
        try:
            data = request.get_json()
            message = data.get('message', '').strip()
            image_data = data.get('image')
            
            if not message and not image_data:
                yield f"data: {json.dumps({'error': 'Message or image required'})}\n\n"
                return
            
            # Prepare parts for the message
            parts = []
            detected_script = 'unknown'
            
            # Add script preservation instruction if there's text
            if message:
                detected_script = script_detector.detect_script(message)
                script_instruction = script_detector.create_script_instruction(detected_script, message)
                parts.append({'text': script_instruction})
                
                # Add user message to history before processing
                add_to_history('user', message, detected_script)
            
            if image_data:
                # Process base64 image
                try:
                    parts.append({
                        'inline_data': {
                            'mime_type': image_data['mimeType'],
                            'data': image_data['data']
                        }
                    })
                    # Add image info to history
                    add_to_history('user', f"[Image uploaded: {image_data.get('filename', 'unknown')}]")
                except Exception as e:
                    friendly_error = get_user_friendly_error(str(e))
                    yield f"data: {json.dumps({'error': friendly_error})}\n\n"
                    return
            
            if message:
                parts.append({'text': f"User message: {message}"})
            
            # Get chat session and send message
            chat = get_chat_session()
            response = chat.send_message(parts, stream=True)
            
            # Send script detection info first
            yield f"data: {json.dumps({'script_info': {'detected_script': detected_script, 'chat_id': session.get('chat_id')}})}\n\n"
            
            # Collect response for history
            full_response = ""
            
            # Stream the response
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    # Clean each chunk before sending to user
                    cleaned_chunk = clean_ai_response(chunk.text)
                    if cleaned_chunk:  # Only send non-empty cleaned chunks
                        yield f"data: {json.dumps({'chunk': cleaned_chunk})}\n\n"
            
            # Clean the complete response before adding to history
            cleaned_full_response = clean_ai_response(full_response)
            
            # Add complete AI response to history
            add_to_history('assistant', cleaned_full_response, detected_script)
            
            yield f"data: {json.dumps({'done': True, 'history_length': len(session.get('chat_history', []))})}\n\n"
            
        except Exception as e:
            # Use user-friendly error message  
            friendly_error = get_user_friendly_error(str(e))
            yield f"data: {json.dumps({'error': friendly_error})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    try:
        # Clear chat history and create new chat ID
        session.pop('chat_id', None)
        session.pop('chat_history', None)
        session.modified = True
        
        return jsonify({
            'success': True, 
            'message': 'Chat history cleared',
            'new_chat_id': str(uuid.uuid4())
        })
    except Exception as e:
        friendly_error = get_user_friendly_error(str(e))
        return jsonify({'error': friendly_error}), 500

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get current chat history (for debugging)"""
    try:
        history = session.get('chat_history', [])
        return jsonify({
            'chat_id': session.get('chat_id'),
            'history_length': len(history),
            'history': history[-10:],  # Last 10 messages only
            'success': True
        })
    except Exception as e:
        friendly_error = get_user_friendly_error(str(e))
        return jsonify({'error': friendly_error}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_data = file.read()
            
            # Convert to base64
            base64_data = base64.b64encode(file_data).decode('utf-8')
            mime_type = file.content_type or 'application/octet-stream'
            
            return jsonify({
                'success': True,
                'data': base64_data,
                'mimeType': mime_type,
                'filename': filename
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        friendly_error = get_user_friendly_error(str(e))
        return jsonify({'error': friendly_error}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413

if __name__ == '__main__':
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("Warning: GEMINI_API_KEY not found in environment variables!")
        print("Please set your Gemini API key in the .env file")
    
    app.run(debug=True, host='0.0.0.0', port=5000)