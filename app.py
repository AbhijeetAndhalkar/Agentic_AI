import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from groq import Groq
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "chatbot")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_email(subject, body, to_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# Initialize Clients
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
except Exception as e:
    print(f"Error initializing Pinecone: {e}")
    index = None

try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Error initializing Groq: {e}")
    groq_client = None

# Load Embedding Model
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading embedding model: {e}")
    embedding_model = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/training')
def training():
    return render_template('training.html')

@app.route('/placements')
def placements():
    return render_template('placements.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/hire-from-us')
def hire():
    return render_template('hire.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    if not index or not groq_client or not embedding_model:
        return jsonify({"error": "Backend services not initialized"}), 500

    # 1. Embed user message
    query_embedding = embedding_model.encode(user_message).tolist()

    # 2. Query Pinecone
    try:
        search_results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
        context_text = "\n".join([match['metadata']['text'] for match in search_results['matches']])
    except Exception as e:
        print(f"Pinecone query error: {e}")
        context_text = ""

    # 3. Construct Prompt with Context
    system_prompt = f"""You are a helpful assistant for LinkCode Technologies.
    Use the following pieces of context to answer the user's question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    
    Context:
    {context_text}
    """

    # 4. Call Groq
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
        )
        bot_response = chat_completion.choices[0].message.content
        
        # Check if response indicates need for email (simple keyword check for demo)
        if "send email" in user_message.lower() and EMAIL_USER:
             # This is a placeholder logic. In production, use tool calling or structured output.
             pass

    except Exception as e:
        print(f"Groq API error: {e}")
        bot_response = "Sorry, I'm having trouble connecting to the AI service right now."

    return jsonify({"response": bot_response})

@app.route('/send_email', methods=['POST'])
def trigger_email():
    data = request.json
    subject = data.get('subject', 'ChatBot Notification')
    body = data.get('body', 'No content')
    to = data.get('to', EMAIL_USER) # Default to self
    
    if send_email(subject, body, to):
        return jsonify({"status": "success", "message": "Email sent"})
    else:
        return jsonify({"status": "error", "message": "Failed to send email"}), 500

if __name__ == '__main__':
    app.run(debug=True)
