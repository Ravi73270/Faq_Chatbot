// chat.js – handles all frontend chat interactions

const chatMessages = document.getElementById('chatMessages');
const userInput    = document.getElementById('userInput');
const sendBtn      = document.getElementById('sendBtn');
const typingStatus = document.getElementById('typingStatus');

// ── Load FAQs in sidebar ───────────────────────────────────────────
async function loadFAQs() {
  try {
    const res  = await fetch('/faqs');
    const faqs = await res.json();
    const list = document.getElementById('faqList');
    list.innerHTML = '';
    faqs.forEach(faq => {
      const div = document.createElement('div');
      div.className = 'faq-item';
      div.textContent = faq.question;
      div.onclick = () => sendQuick(faq.question);
      list.appendChild(div);
    });
  } catch (e) {
    document.getElementById('faqList').innerHTML =
      '<div class="faq-loading">Failed to load FAQs.</div>';
  }
}
loadFAQs();

// ── Helpers ────────────────────────────────────────────────────────

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setTyping(isTyping) {
  typingStatus.textContent = isTyping ? 'Typing…' : 'Ready to help you';
  sendBtn.disabled = isTyping;
}

function appendUserMessage(text) {
  const div = document.createElement('div');
  div.className = 'message user-message';
  div.innerHTML = `
    <div class="message-content">
      <p>${escapeHtml(text)}</p>
    </div>
    <div class="user-icon">👤</div>
  `;
  chatMessages.appendChild(div);
  scrollToBottom();
}

function appendTypingIndicator() {
  const div = document.createElement('div');
  div.className = 'message bot-message';
  div.id = 'typingIndicator';
  div.innerHTML = `
    <div class="bot-avatar small">🤖</div>
    <div class="message-content">
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>
  `;
  chatMessages.appendChild(div);
  scrollToBottom();
}

function removeTypingIndicator() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

function appendBotMessage(data) {
  const confColor = data.confidence >= 70 ? '#22c55e'
                  : data.confidence >= 40 ? '#f59e0b'
                  : '#ef4444';

  const matchedHtml = data.matched_question
    ? `<div class="matched-q">📌 Matched: "${escapeHtml(data.matched_question)}"</div>`
    : '';

  const confHtml = data.matched_question ? `
    <div class="confidence-bar">
      <div class="conf-label">Match confidence</div>
      <div class="conf-track">
        <div class="conf-fill" style="width:${data.confidence}%; background: linear-gradient(90deg, ${confColor}, ${confColor}aa)"></div>
      </div>
      <div class="conf-pct" style="color:${confColor}">${data.confidence}%</div>
    </div>` : '';

  const div = document.createElement('div');
  div.className = 'message bot-message';
  div.innerHTML = `
    <div class="bot-avatar small">🤖</div>
    <div class="message-content">
      <p>${escapeHtml(data.answer)}</p>
      ${matchedHtml}
      ${confHtml}
    </div>
  `;
  chatMessages.appendChild(div);
  scrollToBottom();
}

function escapeHtml(text) {
  const map = { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// ── Send message ───────────────────────────────────────────────────

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  userInput.value = '';
  appendUserMessage(text);
  appendTypingIndicator();
  setTyping(true);

  try {
    const res  = await fetch('/chat', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ message: text })
    });
    const data = await res.json();
    await new Promise(r => setTimeout(r, 600)); // realistic delay
    removeTypingIndicator();
    appendBotMessage(data);
  } catch (err) {
    removeTypingIndicator();
    appendBotMessage({
      answer: '⚠️ Connection error. Please check the server and try again.',
      matched_question: null,
      confidence: 0
    });
  } finally {
    setTyping(false);
    userInput.focus();
  }
}

function sendQuick(question) {
  userInput.value = question;
  sendMessage();
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function clearChat() {
  chatMessages.innerHTML = '';
  // Re-add welcome message
  const welcome = document.createElement('div');
  welcome.className = 'message bot-message';
  welcome.innerHTML = `
    <div class="bot-avatar small">🤖</div>
    <div class="message-content">
      <p>Chat cleared! How can I help you?</p>
      <div class="quick-chips">
        <button class="chip" onclick="sendQuick('How do I create an account?')">Create account</button>
        <button class="chip" onclick="sendQuick('Is there a free trial?')">Free trial</button>
        <button class="chip" onclick="sendQuick('How much does it cost?')">Pricing</button>
        <button class="chip" onclick="sendQuick('How do I contact support?')">Support</button>
      </div>
    </div>
  `;
  chatMessages.appendChild(welcome);
}
