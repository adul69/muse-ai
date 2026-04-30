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
let currentAudio = null;
let currentPlayingId = null;

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

// ─── Audio Preview ──────────────────────────────────────

function stopPreview() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
    }
    if (currentPlayingId) {
        const btn = document.querySelector(`[data-track-id="${currentPlayingId}"] .track-preview-btn`);
        const card = document.querySelector(`[data-track-id="${currentPlayingId}"]`);
        if (btn) {
            btn.innerHTML = '<i class="fas fa-play"></i>';
            btn.classList.remove('playing');
        }
        if (card) card.classList.remove('playing');
        currentPlayingId = null;
    }
}

function playPreview(url, trackId) {
    // If clicking same track, toggle pause
    if (currentPlayingId === trackId && currentAudio) {
        if (!currentAudio.paused) {
            currentAudio.pause();
            const btn = document.querySelector(`[data-track-id="${trackId}"] .track-preview-btn`);
            const card = document.querySelector(`[data-track-id="${trackId}"]`);
            if (btn) {
                btn.innerHTML = '<i class="fas fa-play"></i>';
                btn.classList.remove('playing');
            }
            if (card) card.classList.remove('playing');
            return;
        }
    }

    // Stop any currently playing track
    stopPreview();

    // Start new preview
    currentAudio = new Audio(url);
    currentAudio.volume = 0.7;
    currentPlayingId = trackId;

    const btn = document.querySelector(`[data-track-id="${trackId}"] .track-preview-btn`);
    const card = document.querySelector(`[data-track-id="${trackId}"]`);
    const progressBar = document.querySelector(`[data-track-id="${trackId}"] .preview-progress-bar`);

    if (btn) {
        btn.innerHTML = '<i class="fas fa-pause"></i>';
        btn.classList.add('playing');
    }
    if (card) card.classList.add('playing');

    // Update progress bar
    currentAudio.addEventListener('timeupdate', () => {
        if (progressBar && currentAudio.duration) {
            const pct = (currentAudio.currentTime / currentAudio.duration) * 100;
            progressBar.style.width = `${pct}%`;
        }
    });

    // When finished, reset
    currentAudio.addEventListener('ended', () => {
        stopPreview();
    });

    currentAudio.play().catch(err => {
        console.warn('Preview playback failed:', err);
        stopPreview();
    });
}

// ─── Result Panel Renderer ──────────────────────────────

function renderResult(data) {
    // Always get fresh element references (for demo mode compatibility)
    const rp = document.getElementById('resultPanel');
    const rc = document.getElementById('resultContent');
    if (!rp || !rc) return; // Silently skip if elements don't exist

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
            <h4>Tracks <span class="preview-hint">▶ Click play to preview (30s)</span></h4>
            ${tracks.map((t, idx) => `
                <div class="track-card" data-track-id="track-${idx}">
                    <div class="track-img-wrapper">
                        <img src="${t.image || 'https://via.placeholder.com/44'}" alt="${escapeHtml(t.name)}" class="track-img">
                        ${t.preview_url ? `
                            <button class="track-preview-overlay" onclick="playPreview('${t.preview_url}', 'track-${idx}')">
                                <i class="fas fa-play"></i>
                            </button>
                        ` : ''}
                    </div>
                    <div class="track-meta">
                        <div class="track-title">${escapeHtml(t.name)}</div>
                        <div class="track-artist">${escapeHtml(t.artists)}</div>
                        ${t.preview_url ? `
                            <div class="preview-progress">
                                <div class="preview-progress-bar"></div>
                            </div>
                        ` : '<span class="no-preview">No preview available</span>'}
                    </div>
                    <a href="${t.spotify_url}" target="_blank" class="track-play" title="Open in Spotify">
                        <i class="fab fa-spotify"></i>
                    </a>
                </div>
            `).join('')}
        </div>
    `;

    rc.innerHTML = analysisHtml + playlistHtml + tracksHtml;
    rp.classList.remove('hidden');
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

// ─── Demo Mode Entry ────────────────────────────────────

function enterDemoMode() {
    // Hide landing, show chat UI
    const landing = document.querySelector('.landing');
    if (landing) {
        landing.style.display = 'none';
    }
    
    // Create and show chat container
    const main = document.querySelector('.main');
    const chatHtml = `
        <div class="chat-container">
            <div class="chat-header">
                <div>
                    <h2><i class="fas fa-robot"></i> MuseAI Chat</h2>
                    <span class="provider-badge demo">DEMO</span>
                </div>
            </div>
            <div id="chatMessages" class="chat-messages">
                <div class="message bot-message">
                    <div class="message-avatar">🎵</div>
                    <div class="message-bubble">
                        <div class="message-text">
                            <strong>Welcome to MuseAI Demo! 👋</strong><br><br>
                            This is a demo version — no Spotify login required.<br><br>
                            <strong>Examples:</strong>
                            <ul class="examples">
                                <li>"I just broke up, want something like Coldplay but more depressing"</li>
                                <li>"Coding session, need deep focus with no vocals"</li>
                                <li>"Friday night party vibes, something to dance to"</li>
                                <li>"Rainy day, cozy lo-fi for reading"</li>
                            </ul>
                        </div>
                        <div class="message-time">Now</div>
                    </div>
                </div>
            </div>
            <div class="chat-input-area">
                <form id="chatForm" class="chat-form">
                    <div class="input-wrapper">
                        <input type="text" id="messageInput" placeholder="Describe your mood or vibe..." autocomplete="off" required>
                        <button type="submit" class="send-btn" id="sendBtn">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </form>
            </div>
        </div>
        <div id="resultPanel" class="result-panel hidden">
            <div class="result-header">
                <h3><i class="fas fa-sparkles"></i> AI Analysis</h3>
                <button id="closeResult" class="btn btn-icon"><i class="fas fa-times"></i></button>
            </div>
            <div id="resultContent" class="result-content"></div>
        </div>
    `;
    main.innerHTML = chatHtml;
    
    // Re-bind events to new elements
    const newChatForm = document.getElementById('chatForm');
    const newMessageInput = document.getElementById('messageInput');
    const newSendBtn = document.getElementById('sendBtn');
    const newCloseResult = document.getElementById('closeResult');
    
    if (newChatForm) {
        newChatForm.addEventListener('submit', handleDemoSubmit);
    }
    if (newCloseResult) {
        newCloseResult.addEventListener('click', () => {
            document.getElementById('resultPanel').classList.add('hidden');
        });
    }
    if (newMessageInput) {
        newMessageInput.focus();
    }
}

// ─── Demo Submit Handler ────────────────────────────────

async function handleDemoSubmit(e) {
    e.preventDefault();
    if (isProcessing) return;

    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    
    const message = messageInput.value.trim();
    if (!message) return;

    isProcessing = true;
    messageInput.value = '';
    messageInput.disabled = true;
    sendBtn.disabled = true;

    // Add user message
    const userHtml = `
        <div class="message user-message">
            <div class="message-avatar">👤</div>
            <div class="message-bubble">
                <div class="message-text">${escapeHtml(message)}</div>
                <div class="message-time">${getTimestamp()}</div>
            </div>
        </div>
    `;
    chatMessages.insertAdjacentHTML('beforeend', userHtml);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Add typing
    const typingId = 'typing-' + Date.now();
    const typingHtml = `
        <div id="${typingId}" class="message bot-message">
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
    chatMessages.insertAdjacentHTML('beforeend', typingHtml);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });

        const el = document.getElementById(typingId);
        if (el) el.remove();

        const data = await response.json();

        if (!response.ok || data.error) {
            const errHtml = `
                <div class="message bot-message">
                    <div class="message-avatar">⚠️</div>
                    <div class="message-bubble error-bubble">
                        <div class="message-text">${escapeHtml(data.error || 'Something went wrong')}</div>
                        <div class="message-time">${getTimestamp()}</div>
                    </div>
                </div>
            `;
            chatMessages.insertAdjacentHTML('beforeend', errHtml);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            return;
        }

        // Success
        const mood = data.llm_analysis?.mood || 'Custom';
        const reasoning = data.llm_analysis?.reasoning || '';
        const botHtml = `
            <div class="message bot-message">
                <div class="message-avatar">🎵</div>
                <div class="message-bubble">
                    <div class="message-text">
                        <strong>Playlist generated!</strong> 🎉<br>
                        Detected mood: <strong>${escapeHtml(mood)}</strong><br>
                        ${escapeHtml(reasoning.substring(0, 120))}${reasoning.length > 120 ? '...' : ''}<br><br>
                        ${data.demo ? '<span style="color: var(--accent);">🚀 Demo Mode — Check the sidebar for track samples!</span>' : 'Check the sidebar for details and the playlist link!'}
                    </div>
                    <div class="message-time">${getTimestamp()}</div>
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', botHtml);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Render result
        renderResult(data);

    } catch (err) {
        const el = document.getElementById(typingId);
        if (el) el.remove();
        
        const errHtml = `
            <div class="message bot-message">
                <div class="message-avatar">⚠️</div>
                <div class="message-bubble error-bubble">
                    <div class="message-text">Network error. Please try again.</div>
                    <div class="message-time">${getTimestamp()}</div>
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', errHtml);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } finally {
        isProcessing = false;
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}
