"""
app.py  –  Flask backend for FAQ Chatbot
Routes:
  GET  /            →  Chat UI
  POST /chat        →  Returns JSON response for user query
  GET  /faqs        →  Returns all FAQs as JSON
  GET  /health      →  Health check
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, render_template
from nlp.nlp_processor import FAQChatbot

app = Flask(__name__)

# ── Initialise chatbot once at startup ────────────────────────────────────────
FAQ_PATH = os.path.join(os.path.dirname(__file__), 'data', 'faqs.json')
chatbot  = FAQChatbot(FAQ_PATH)
print("✅ FAQ Chatbot loaded successfully!")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    data       = request.get_json()
    user_input = data.get('message', '').strip()

    if not user_input:
        return jsonify({'error': 'Empty message'}), 400

    result = chatbot.get_response(user_input)
    return jsonify({
        'user_message':     user_input,
        'answer':           result['answer'],
        'matched_question': result['matched_question'],
        'confidence':       result['confidence'],
        'top_matches':      result['top_matches']
    })


@app.route('/faqs', methods=['GET'])
def faqs():
    return jsonify(chatbot.get_all_faqs())


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'faq_count': len(chatbot.faqs)})


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
