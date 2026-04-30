/**
 * MuseAI Chat Frontend
 * Handles chat flow, playlist generation UI, and real-time updates
 */

const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const resultPanel = document.getElementById('resultPanel');
const resultContent = document.getElementById('resultContent');
const closeResult = document.getElementById('closeResult');

let isProcessing = false;

// ─── Helpers ────────────────────────────────────────────

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function getTimestamp() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ─── Message Builders ───────────────────────────────────

function addUserMessage(text) {
    const html = `
        <div class="message user-message">
            <div class="message-avatar">👤</div>
            <div class="message-bubble">
                <div class="message-text">${escapeHtml(text)}</div>
                <div class="message-time">${getTimestamp()}</div>
            </div>
        </div>
    `;
    chatMessages.insertAdjacentHTML('beforeend', html);
    scrollToBottom();
}

function addBotMessage(htmlContent) {
    const html = `
        <div class="message bot-message">
            <div class="message-avatar">🎵</div>
            <div class="message-bubble">
                <div class="message-text">${htmlContent}</div>
                <div class="message-time">${getTimestamp()}</div>
            </div>
        </div>
    `;
    chatMessages.insertAdjacentHTML('beforeend', html);
    scrollToBottom();
}

function addTypingIndicator() {
    const id = 'typing-' + Date.now();
    const html = `
        <div id="${id}" class="message bot-message">
            <div class="message-avatar">🎵</div>
            <div class="message-bubble">
                <div class="typing">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    `;
    chatMessages.insertAdjacentHTML('beforeend', html);
    scrollToBottom();
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function addErrorMessage(text) {
    const html = `
        <div class="message bot-message">
            <div class="message-avatar">⚠️</div>
            <div class="message-bubble error-bubble">
                <div class="message-text">${escapeHtml(text)}</div>
                <div class="message-time">${getTimestamp()}</div>
            </div>
        </div>
    `;
    chatMessages.insertAdjacentHTML('beforeend', html);
    scrollToBottom();
}

// ─── Result Panel Renderer ──────────────────────────────

function renderResult(data) {
    const analysis = data.llm_analysis;
    const playlist = data.playlist;
    const tracks = data.tracks;

    const analysisHtml = `
        <div class="analysis-card">
            <h4>🧠 AI Analysis</h4>
            <div class="analysis-row">
                <span class="analysis-label">Mood</span>
                <span class="analysis-value">${escapeHtml(analysis.mood)}</span>
            </div>
            <div class="analysis-row">
                <span class="analysis-label">Energy</span>
                <span class="analysis-value">${(analysis.energy * 100).toFixed(0)}%</span>
            </div>
            <div class="analysis-row">
                <span class="analysis-label">Valence</span>
                <span class="analysis-value">${(analysis.valence * 100).toFixed(0)}%</span>
            </div>
            <div class="analysis-row">
                <span class="analysis-label">Genres</span>
                <span class="analysis-value">${analysis.genres.join(', ')}</span>
            </div>
        </div>
    `;

    const playlistHtml = `
        <div class="playlist-card">
            <h4>${escapeHtml(playlist.name)}</h4>
            <p>${tracks.length} tracks generated</p>
            <a href="${playlist.url}" target="_blank" class="playlist-link">
                <i class="fab fa-spotify"></i> Open in Spotify
            </a>
        </div>
    `;

    const tracksHtml = `
        <div class="tracks-section">
            <h4>Tracks</h4>
            ${tracks.map(t => `
                <div class="track-card">
                    <img src="${t.image || 'https://via.placeholder.com/44'}" alt="${escapeHtml(t.name)}" class="track-img">
                    <div class="track-meta">
                        <div class="track-title">${escapeHtml(t.name)}</div>
                        <div class="track-artist">${escapeHtml(t.artists)}</div>
                    </div>
                    <a href="${t.spotify_url}" target="_blank" class="track-play" title="Open in Spotify">
                        <i class="fas fa-play"></i>
                    </a>
                </div>
            `).join('')}
        </div>
    `;

    resultContent.innerHTML = analysisHtml + playlistHtml + tracksHtml;
    resultPanel.classList.remove('hidden');
}

// ─── Form Handler ───────────────────────────────────────

async function handleSubmit(e) {
    e.preventDefault();
    if (isProcessing) return;

    const message = messageInput.value.trim();
    if (!message) return;

    // UI State
    isProcessing = true;
    messageInput.value = '';
    messageInput.disabled = true;
    sendBtn.disabled = true;

    addUserMessage(message);
    const typingId = addTypingIndicator();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });

        removeTypingIndicator(typingId);

        const data = await response.json();

        if (!response.ok || data.error) {
            addErrorMessage(data.error || 'Something went wrong. Please try again.');
            return;
        }

        // Success — show summary in chat, details in sidebar
        const mood = data.llm_analysis?.mood || 'Custom';
        const reasoning = data.llm_analysis?.reasoning || '';
        addBotMessage(`
            <strong>Playlist generated!</strong> 🎉<br>
            Detected mood: <strong>${escapeHtml(mood)}</strong><br>
            ${escapeHtml(reasoning.substring(0, 120))}${reasoning.length > 120 ? '...' : ''}<br><br>
            Check the sidebar for details and the playlist link!
        `);

        renderResult(data);
        scrollToBottom();

    } catch (err) {
        removeTypingIndicator(typingId);
        addErrorMessage('Network error. Please check your connection and try again.');
        console.error(err);
    } finally {
        isProcessing = false;
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

// ─── Event Listeners ────────────────────────────────────

if (chatForm) {
    chatForm.addEventListener('submit', handleSubmit);
}

if (closeResult) {
    closeResult.addEventListener('click', () => {
        resultPanel.classList.add('hidden');
    });
}

// Clickable examples in welcome message
document.addEventListener('click', (e) => {
    const li = e.target.closest('.examples li');
    if (li && messageInput) {
        messageInput.value = li.textContent.replace(/^"|"$/g, '');
        messageInput.focus();
    }
});

// Auto-focus input on load
if (messageInput) {
    messageInput.focus();
}
