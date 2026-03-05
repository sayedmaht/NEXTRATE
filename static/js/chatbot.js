/**
 * NextRate AI — Chatbot Module
 * Floating chatbot window with AI-powered financial assistant
 */

// ═══════════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════════

let chatHistory = [];
let isChatOpen = false;
let isTyping = false;

// ═══════════════════════════════════════════════════════════════════════════════
// Toggle Chat
// ═══════════════════════════════════════════════════════════════════════════════

function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    const badge = document.getElementById('chatBadge');
    isChatOpen = !isChatOpen;

    if (isChatOpen) {
        chatWindow.classList.add('active');
        badge.style.display = 'none';
        document.getElementById('chatInput').focus();
    } else {
        chatWindow.classList.remove('active');
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Send Message
// ═══════════════════════════════════════════════════════════════════════════════

function sendQuickMessage(text) {
    document.getElementById('chatInput').value = text;
    sendChatMessage();
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message || isTyping) return;

    input.value = '';

    // Add user message
    addChatMessage('user', message);
    chatHistory.push({ role: 'user', content: message });

    // Show typing indicator
    showTypingIndicator();
    isTyping = true;

    try {
        const resp = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                history: chatHistory.slice(-10)
            })
        });

        if (!resp.ok) throw new Error('Chat API error');
        const data = await resp.json();

        hideTypingIndicator();
        isTyping = false;

        const response = data.response || "I'm sorry, I couldn't process that request.";
        addChatMessage('bot', response);
        chatHistory.push({ role: 'assistant', content: response });
    } catch (err) {
        hideTypingIndicator();
        isTyping = false;
        addChatMessage('bot', "⚠️ Sorry, I encountered an error. Please try again in a moment.");
        console.error('Chat error:', err);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Chat UI
// ═══════════════════════════════════════════════════════════════════════════════

function addChatMessage(role, content) {
    const container = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${role === 'user' ? 'user' : ''}`;

    const avatar = role === 'user' ? '👤' : '🤖';
    const formattedContent = formatChatContent(content);

    msgDiv.innerHTML = `
        <div class="chat-msg-avatar">${avatar}</div>
        <div class="chat-msg-bubble">${formattedContent}</div>
    `;

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function formatChatContent(text) {
    // Basic markdown-like formatting
    return text
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Italic
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Code
        .replace(/`(.*?)`/g, '<code>$1</code>')
        // Line breaks
        .replace(/\n/g, '<br>')
        // Bullet points
        .replace(/^- (.+)/gm, '• $1');
}

function showTypingIndicator() {
    const container = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="chat-msg-avatar">🤖</div>
        <div class="chat-msg-bubble">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
}

function hideTypingIndicator() {
    const el = document.getElementById('typingIndicator');
    if (el) el.remove();
}
