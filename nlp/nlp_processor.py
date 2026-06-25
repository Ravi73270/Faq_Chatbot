"""
nlp_processor.py
----------------
NLP pipeline:
  - Tokenization, lowercasing, stopword removal, lemmatization (NLTK)
  - Synonym expansion for better paraphrase matching
  - TF-IDF vectorization + Cosine Similarity (sklearn)
  - Keyword fallback for near-zero TF-IDF scores
"""

import re, json
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── NLTK bootstrap ─────────────────────────────────────────────────
for r in ['punkt', 'stopwords', 'wordnet', 'omw-1.4', 'punkt_tab']:
    try: nltk.download(r, quiet=True)
    except: pass

# ── Synonym map (domain-level paraphrase expansion) ────────────────
SYNONYMS = {
    'price': ['cost', 'pricing', 'fee', 'charge', 'plan', 'subscription', 'pay', 'money', 'rate'],
    'cost':  ['price', 'pricing', 'fee', 'plan'],
    'safe':  ['secure', 'security', 'privacy', 'encrypt', 'protected'],
    'safety':['security', 'privacy'],
    'help':  ['support', 'contact', 'assist', 'customer'],
    'support':['help', 'contact', 'assist'],
    'free':  ['trial', 'demo', 'test'],
    'trial': ['free', 'demo'],
    'login': ['sign', 'account', 'password', 'access'],
    'sign':  ['account', 'register', 'login', 'create'],
    'create':['register', 'sign', 'new', 'open'],
    'cancel':['subscription', 'stop', 'end', 'terminate', 'quit'],
    'refund':['money', 'back', 'return', 'guarantee'],
    'phone': ['mobile', 'app', 'ios', 'android'],
    'mobile':['phone', 'app', 'ios', 'android'],
    'call':  ['api', 'request', 'limit', 'quota'],
    'browser':['chrome', 'firefox', 'safari', 'edge'],
    'update':['upgrade', 'change', 'switch', 'move'],
    'export':['download', 'backup', 'extract', 'get'],
    'offline':['internet', 'connection', 'network', 'without'],
}

lemmatizer = WordNetLemmatizer()
STOP_WORDS  = set(stopwords.words('english'))

# ── Preprocessing ───────────────────────────────────────────────────
def preprocess(text: str, expand_synonyms: bool = False) -> str:
    text   = text.lower()
    text   = re.sub(r'[^a-z\s]', '', text)
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 1]
    tokens = [lemmatizer.lemmatize(t) for t in tokens]

    if expand_synonyms:
        extra = []
        for t in tokens:
            extra.extend(SYNONYMS.get(t, []))
        tokens = tokens + extra

    return ' '.join(tokens)


# ── Chatbot Engine ──────────────────────────────────────────────────
class FAQChatbot:
    def __init__(self, faq_path: str):
        with open(faq_path) as f:
            self.faqs = json.load(f)

        self.questions    = [faq['question'] for faq in self.faqs]
        self.answers      = [faq['answer']   for faq in self.faqs]

        # Build two sets of processed questions: plain + synonym-expanded
        plain_qs    = [preprocess(q) for q in self.questions]
        expanded_qs = [preprocess(q, expand_synonyms=True) for q in self.questions]

        # Combine for richer TF-IDF corpus (each FAQ represented twice)
        corpus = plain_qs + expanded_qs
        self.n  = len(self.questions)

        self.vectorizer   = TfidfVectorizer(ngram_range=(1, 2))
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def get_response(self, user_input: str, threshold: float = 0.10):
        plain    = preprocess(user_input)
        expanded = preprocess(user_input, expand_synonyms=True)

        if not plain.strip():
            return self._miss(0.0)

        # Score against both halves; take element-wise max
        vec_plain = self.vectorizer.transform([plain])
        vec_exp   = self.vectorizer.transform([expanded])

        scores_plain = cosine_similarity(vec_plain, self.tfidf_matrix).flatten()
        scores_exp   = cosine_similarity(vec_exp,   self.tfidf_matrix).flatten()

        # Combine: each FAQ has two rows (plain[i] and expanded[i+n])
        scores = np.maximum(
            scores_plain[:self.n],
            np.maximum(scores_plain[self.n:], np.maximum(scores_exp[:self.n], scores_exp[self.n:]))
        )

        best_idx   = int(np.argmax(scores))
        best_score = float(scores[best_idx])

        top_indices = scores.argsort()[::-1][:3]
        top_matches = [
            {'question': self.questions[i], 'confidence': round(float(scores[i]) * 100, 1)}
            for i in top_indices if scores[i] > 0
        ]

        if best_score < threshold:
            return self._miss(round(best_score * 100, 1), top_matches)

        return {
            'answer':           self.answers[best_idx],
            'matched_question': self.questions[best_idx],
            'confidence':       round(best_score * 100, 1),
            'top_matches':      top_matches
        }

    def _miss(self, conf, top_matches=None):
        return {
            'answer': (
                "Sorry, I couldn't find a relevant answer to your question. "
                "Try rephrasing it, or contact our support team for help."
            ),
            'matched_question': None,
            'confidence':       conf,
            'top_matches':      top_matches or []
        }

    def get_all_faqs(self):
        return self.faqs
