# 🤖 FAQ Chatbot — CodeAlpha Internship Task 2

An AI-powered FAQ chatbot using **NLP** (NLTK + TF-IDF + Cosine Similarity)
with a dark-theme chat UI built with Flask.

---

## 📁 Project Structure

```
faq_chatbot/
├── app.py                  # Flask backend (routes)
├── requirements.txt        # Python dependencies
├── README.md
│
├── data/
│   └── faqs.json           # FAQ dataset (20 Q&A pairs)
│
├── nlp/
│   ├── __init__.py
│   └── nlp_processor.py    # NLP pipeline + FAQChatbot class
│
├── templates/
│   └── index.html          # Chat UI (Jinja2 template)
│
└── static/
    ├── css/
    │   └── style.css       # Dark theme styles
    └── js/
        └── chat.js         # Frontend chat logic
```

---

## 🧠 How It Works (NLP Pipeline)

```
User Input
    │
    ▼
1. Lowercase + Remove special chars
    │
    ▼
2. NLTK Tokenization  (word_tokenize)
    │
    ▼
3. Stopword Removal   (nltk.corpus.stopwords)
    │
    ▼
4. Lemmatization      (WordNetLemmatizer)
    │
    ▼
5. Synonym Expansion  (domain-level synonym map)
    │
    ▼
6. TF-IDF Vectorization (sklearn, bigrams)
    │
    ▼
7. Cosine Similarity  → best matching FAQ question
    │
    ▼
8. Return Answer + Confidence Score
```

---

## 🚀 Setup & Run

### Step 1 — Clone / download the project
```bash
cd faq_chatbot
```

### Step 2 — Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the Flask server
```bash
python app.py
```

### Step 5 — Open in browser
```
http://localhost:5000
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/`      | Chat UI     |
| POST   | `/chat`  | Get answer for user query |
| GET    | `/faqs`  | List all FAQs |
| GET    | `/health`| Health check |

### POST `/chat` — Example
```json
// Request
{ "message": "how do I reset my password?" }

// Response
{
  "user_message":     "how do I reset my password?",
  "answer":           "Click 'Forgot Password' on the login page...",
  "matched_question": "How do I reset my password?",
  "confidence":       70.7,
  "top_matches": [
    { "question": "How do I reset my password?", "confidence": 70.7 },
    { "question": "How do I create an account?", "confidence": 12.3 }
  ]
}
```

---

## ✨ Features

- 20 realistic FAQ Q&A pairs (product support domain)
- Full NLP preprocessing: tokenize → clean → lemmatize → vectorize
- Synonym expansion for paraphrase handling
- TF-IDF + Cosine Similarity matching
- Confidence score with visual bar
- Dark-theme responsive chat UI
- Sidebar FAQ browser (click to ask)
- Quick-reply chips
- Typing indicator animation
- Clear chat button

---

## 🛠 Tech Stack

| Layer    | Technology |
|----------|-----------|
| Backend  | Python, Flask |
| NLP      | NLTK, scikit-learn |
| ML       | TF-IDF Vectorizer, Cosine Similarity |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Data     | JSON |

---

## 👨‍💻 Author
**Ravi Sahu** | CodeAlpha Internship — Task 2
