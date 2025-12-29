// AI Counsel Chat Interface

// Configure marked.js for markdown rendering
marked.setOptions({
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(code, { language: lang }).value;
            } catch (e) {}
        }
        return code;
    },
    breaks: true,
    gfm: true
});

// State
let ws = null;
let isConnected = false;
let isProcessing = false;

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
    setupAgentSelection();
    messageInput.focus();
});

// WebSocket Connection
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        isConnected = true;
        console.log('Connected to AI Counsel');
    };

    ws.onclose = () => {
        isConnected = false;
        console.log('Disconnected from AI Counsel');
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };
}

// Handle incoming messages
function handleMessage(data) {
    switch (data.type) {
        case 'status':
            showStatus(data.content, true);
            break;

        case 'analysis':
            removeStatus();
            showAnalysis(data.content, data.agents);
            break;

        case 'agent_response':
            showAgentResponse(data.agent, data.content);
            break;

        case 'synthesis':
            showSynthesis(data.content);
            break;

        case 'complete':
            removeStatus();
            isProcessing = false;
            updateSendButton();
            break;

        case 'error':
            removeStatus();
            showError(data.content);
            isProcessing = false;
            updateSendButton();
            break;
    }

    scrollToBottom();
}

// Send message
function sendMessage() {
    const task = messageInput.value.trim();

    if (!task || !isConnected || isProcessing) {
        return;
    }

    // Get selected agents
    const selectedAgents = getSelectedAgents();

    // Hide welcome message
    hideWelcome();

    // Show user message
    showUserMessage(task);

    // Send to server
    ws.send(JSON.stringify({
        task: task,
        agents: selectedAgents
    }));

    // Clear input and set processing state
    messageInput.value = '';
    autoResize(messageInput);
    isProcessing = true;
    updateSendButton();

    scrollToBottom();
}

// Show user message
function showUserMessage(content) {
    const div = document.createElement('div');
    div.className = 'message message-user';
    div.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
    chatMessages.appendChild(div);
}

// Show status message
function showStatus(content, loading = false) {
    removeStatus();
    const div = document.createElement('div');
    div.className = `message message-status${loading ? ' loading' : ''}`;
    div.id = 'statusMessage';
    div.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
    chatMessages.appendChild(div);
}

function removeStatus() {
    const status = document.getElementById('statusMessage');
    if (status) {
        status.remove();
    }
}

// Show analysis message
function showAnalysis(content, agents) {
    const div = document.createElement('div');
    div.className = 'message message-analysis';

    let agentBadges = '';
    if (agents && agents.length > 0) {
        agentBadges = `
            <div class="agents-consulting">
                <span style="color: var(--text-muted); font-size: 12px;">Consulting:</span>
                ${agents.map(agent => `
                    <span class="agent-badge">
                        <span class="agent-icon agent-${agent}"></span>
                        ${capitalizeFirst(agent)}
                    </span>
                `).join('')}
            </div>
        `;
    }

    div.innerHTML = `
        <div class="message-header">
            <span class="agent-name">Orchestrator Analysis</span>
        </div>
        <div class="message-content">
            ${content ? `<p>${escapeHtml(content)}</p>` : ''}
            ${agentBadges}
        </div>
    `;
    chatMessages.appendChild(div);
}

// Show agent response
function showAgentResponse(agent, content) {
    const div = document.createElement('div');
    div.className = 'message message-agent';
    div.innerHTML = `
        <div class="message-header">
            <span class="agent-icon agent-${agent}"></span>
            <span class="agent-name">${capitalizeFirst(agent)} Agent</span>
        </div>
        <div class="message-content">${marked.parse(content)}</div>
    `;
    chatMessages.appendChild(div);

    // Highlight code blocks
    div.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
}

// Show synthesis
function showSynthesis(content) {
    const div = document.createElement('div');
    div.className = 'message message-synthesis';
    div.innerHTML = `
        <div class="message-header">
            <span class="agent-name">Synthesized Recommendation</span>
        </div>
        <div class="message-content">${marked.parse(content)}</div>
    `;
    chatMessages.appendChild(div);

    // Highlight code blocks
    div.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
}

// Show error
function showError(content) {
    const div = document.createElement('div');
    div.className = 'message message-error';
    div.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
    chatMessages.appendChild(div);
}

// Agent selection
function setupAgentSelection() {
    document.querySelectorAll('.agent-checkbox').forEach(label => {
        label.addEventListener('click', (e) => {
            if (e.target.tagName !== 'INPUT') {
                const checkbox = label.querySelector('input');
                checkbox.checked = !checkbox.checked;
            }
            label.classList.toggle('selected', label.querySelector('input').checked);
        });
    });
}

function getSelectedAgents() {
    const selected = [];
    document.querySelectorAll('.agent-checkbox input:checked').forEach(checkbox => {
        selected.push(checkbox.value);
    });
    return selected;
}

function clearAgentSelection() {
    document.querySelectorAll('.agent-checkbox').forEach(label => {
        label.classList.remove('selected');
        label.querySelector('input').checked = false;
    });
}

// Clear chat
function clearChat() {
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <h2>Welcome to AI Counsel</h2>
            <p>I'm your council of specialized AI agents. Ask me anything about building applications, and I'll consult the relevant experts.</p>
            <div class="example-prompts">
                <p>Try asking:</p>
                <button class="example-btn" onclick="useExample(this)">Design a REST API for a task management app</button>
                <button class="example-btn" onclick="useExample(this)">Review this authentication flow for security issues</button>
                <button class="example-btn" onclick="useExample(this)">What's the best way to structure a Python microservice?</button>
                <button class="example-btn" onclick="useExample(this)">Create a testing strategy for a payment system</button>
            </div>
        </div>
    `;
    messageInput.focus();
}

function hideWelcome() {
    const welcome = document.querySelector('.welcome-message');
    if (welcome) {
        welcome.remove();
    }
}

// Use example prompt
function useExample(button) {
    messageInput.value = button.textContent;
    messageInput.focus();
    autoResize(messageInput);
}

// Input handling
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
}

function updateSendButton() {
    sendBtn.disabled = isProcessing || !messageInput.value.trim();
}

messageInput.addEventListener('input', updateSendButton);

// Utilities
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
