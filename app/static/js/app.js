/**
 * app.js: JS code for the adk-streaming sample app.
 */

/**
 * WebSocket handling
 */

// Global variables
let sessionId = "session_" + Date.now(); // Dynamic session ID for fresh starts
// Use secure WebSocket (wss://) for HTTPS and insecure (ws://) for HTTP
const ws_protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
let websocket = null;
let is_audio = false;
let currentMessageId = null; // Track the current message ID during a conversation turn
let currentInputTranscriptionId = null; // Track input transcription message ID
let currentOutputTranscriptionId = null; // Track output transcription message ID

// Get DOM elements
const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("message");
const messagesDiv = document.getElementById("messages");
const statusDot = document.getElementById("status-dot");
const connectionStatus = document.getElementById("connection-status");
const typingIndicator = document.getElementById("typing-indicator");
const startAudioButton = document.getElementById("startAudioButton");
const stopAudioButton = document.getElementById("stopAudioButton");
const recordingContainer = document.getElementById("recording-container");

// WebSocket handlers
function connectWebsocket() {
  // Construct WebSocket URL with current sessionId
  const wsUrl = ws_protocol + window.location.host + "/ws/" + sessionId + "?is_audio=" + is_audio;
  console.log(`[WEBSOCKET] Connecting to session: ${sessionId}`);
  websocket = new WebSocket(wsUrl);

  // Handle connection open
  websocket.onopen = function () {
    // Connection opened messages
    console.log("WebSocket connection opened.");
    connectionStatus.textContent = "Conectado";
    statusDot.classList.add("connected");

    // Enable the Send button ONLY if audio mode is active
    if (is_audio) {
      document.getElementById("sendButton").disabled = false;
    }
    addSubmitHandler();

    // Call custom onOpen handler if defined
    if (typeof window.onWebSocketOpen === 'function') {
      window.onWebSocketOpen();
    }
  };

  // Handle incoming messages
  websocket.onmessage = function (event) {
    // Parse the incoming message
    const message_from_server = JSON.parse(event.data);
    console.log("[AGENT TO CLIENT] ", message_from_server);

    // Show typing indicator for first message in a response sequence,
    // but not for turn_complete messages
    if (
      !message_from_server.turn_complete &&
      (message_from_server.mime_type === "text/plain" ||
        message_from_server.mime_type === "audio/pcm")
    ) {
      typingIndicator.classList.add("visible");
    }

    // Check if the turn is complete or interrupted
    if (message_from_server.turn_complete || message_from_server.interrupted) {
      // Reset currentMessageId to ensure the next message gets a new element
      currentMessageId = null;
      currentInputTranscriptionId = null;
      currentOutputTranscriptionId = null;
      typingIndicator.classList.remove("visible");

      // Clear audio buffer if interrupted (for barge-in)
      if (message_from_server.interrupted && audioPlayerNode) {
        audioPlayerNode.port.postMessage({ command: "endOfAudio" });
        console.log("[BARGE-IN] Interrupted - clearing audio buffer");
      }

      return;
    }

    // Handle input transcription (what the user said via voice)
    if (message_from_server.type === "input_transcription") {
      typingIndicator.classList.remove("visible");
      displayTranscription(message_from_server.data, "user", "input");
      return;
    }

    // Handle output transcription (what the agent said via voice)
    if (message_from_server.type === "output_transcription") {
      typingIndicator.classList.remove("visible");
      displayTranscription(message_from_server.data, "model", "output");
      return;
    }

    // If it's audio, play it
    if (message_from_server.mime_type === "audio/pcm" && audioPlayerNode) {
      audioPlayerNode.port.postMessage(base64ToArray(message_from_server.data));

      // If we have an existing message element for this turn, add audio icon if needed
      if (currentMessageId) {
        const messageElem = document.getElementById(currentMessageId);
        if (
          messageElem &&
          !messageElem.querySelector(".audio-icon") &&
          is_audio
        ) {
          const audioIcon = document.createElement("span");
          audioIcon.className = "audio-icon";
          messageElem.prepend(audioIcon);
        }
      }
    }

    // Handle text messages
    if (message_from_server.mime_type === "text/plain") {
      // Hide typing indicator
      typingIndicator.classList.remove("visible");

      const role = message_from_server.role || "model";

      // In audio mode, filter messages to show only order-related content
      if (is_audio && role === "model") {
        const isOrderRelated = detectOrderMessage(message_from_server.data);
        if (!isOrderRelated) {
          // Skip displaying non-order messages in audio mode
          return;
        }
      }

      // If we already have a message element for this turn, append to it
      if (currentMessageId && role === "model") {
        const existingMessage = document.getElementById(currentMessageId);
        if (existingMessage) {
          // For model messages, get the content container (skip audio icon if present)
          const contentContainer = existingMessage.querySelector('.message-content') || existingMessage;

          // Append the text and re-render markdown
          const currentText = contentContainer.dataset.rawText || '';
          const newText = currentText + message_from_server.data;
          contentContainer.dataset.rawText = newText;

          // Render markdown
          contentContainer.innerHTML = marked.parse(newText);

          // Scroll to the bottom
          messagesDiv.scrollTop = messagesDiv.scrollHeight;
          return;
        }
      }

      // Create a new message element if it's a new turn or user message
      const messageId = Math.random().toString(36).substring(7);
      const messageElem = document.createElement("p");
      messageElem.id = messageId;

      // Set class based on role
      messageElem.className =
        role === "user" ? "user-message" : "agent-message";

      // Add audio icon for model messages if audio is enabled
      if (is_audio && role === "model") {
        const audioIcon = document.createElement("span");
        audioIcon.className = "audio-icon";
        messageElem.appendChild(audioIcon);
      }

      // Create content container for the message
      const contentContainer = document.createElement("div");
      contentContainer.className = "message-content";

      // Handle text content based on role
      if (role === "model") {
        // For model messages, render markdown
        contentContainer.dataset.rawText = message_from_server.data;
        contentContainer.innerHTML = marked.parse(message_from_server.data);
      } else {
        // For user messages, use plain text
        contentContainer.textContent = message_from_server.data;
      }

      messageElem.appendChild(contentContainer);

      // Add the message to the DOM
      messagesDiv.appendChild(messageElem);

      // Remember the ID of this message for subsequent responses in this turn
      if (role === "model") {
        currentMessageId = messageId;
      }

      // Scroll to the bottom
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // Call custom message handler if defined
    if (typeof window.handleWebSocketMessage === 'function') {
      window.handleWebSocketMessage(message_from_server);
    }
  };

  // Handle connection close
  websocket.onclose = function () {
    console.log("WebSocket connection closed.");
    document.getElementById("sendButton").disabled = true;
    connectionStatus.textContent = "Desconectado. Reconectando...";
    statusDot.classList.remove("connected");
    typingIndicator.classList.remove("visible");

    // Call custom onClose handler if defined
    if (typeof window.onWebSocketClose === 'function') {
      window.onWebSocketClose();
    }

    setTimeout(function () {
      console.log("Reconnecting...");
      connectWebsocket();
    }, 5000);
  };

  websocket.onerror = function (e) {
    console.log("WebSocket error: ", e);
    connectionStatus.textContent = "Error de conexión";
    statusDot.classList.remove("connected");
    typingIndicator.classList.remove("visible");
  };
}
connectWebsocket();

// Add submit handler to the form
function addSubmitHandler() {
  messageForm.onsubmit = function (e) {
    e.preventDefault();
    const message = messageInput.value;
    if (message) {
      const p = document.createElement("p");
      p.textContent = message;
      p.className = "user-message";
      messagesDiv.appendChild(p);
      messageInput.value = "";

      // Show typing indicator after sending message
      typingIndicator.classList.add("visible");

      sendMessage({
        mime_type: "text/plain",
        data: message,
        role: "user",
      });
      console.log("[CLIENT TO AGENT] " + message);
      // Scroll down to the bottom of the messagesDiv
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    return false;
  };
}

// Send a message to the server as a JSON string
function sendMessage(message) {
  if (websocket && websocket.readyState == WebSocket.OPEN) {
    const messageJson = JSON.stringify(message);
    websocket.send(messageJson);
  }
}

// Decode Base64 data to Array
function base64ToArray(base64) {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * Audio handling
 */

let audioPlayerNode;
let audioPlayerContext;
let audioRecorderNode;
let audioRecorderContext;
let micStream;
let isRecording = false;

// Import the audio worklets
import { startAudioPlayerWorklet } from "./audio-player.js";
import { startAudioRecorderWorklet } from "./audio-recorder.js";

// Start audio
function startAudio() {
  // Start audio output
  startAudioPlayerWorklet().then(([node, ctx]) => {
    audioPlayerNode = node;
    audioPlayerContext = ctx;
  });
  // Start audio input
  startAudioRecorderWorklet(audioRecorderHandler).then(
    ([node, ctx, stream]) => {
      audioRecorderNode = node;
      audioRecorderContext = ctx;
      micStream = stream;
      isRecording = true;
    }
  );
}

// Stop audio recording
function stopAudio() {
  if (audioRecorderNode) {
    audioRecorderNode.disconnect();
    audioRecorderNode = null;
  }

  if (audioRecorderContext) {
    audioRecorderContext
      .close()
      .catch((err) => console.error("Error closing audio context:", err));
    audioRecorderContext = null;
  }

  if (micStream) {
    micStream.getTracks().forEach((track) => track.stop());
    micStream = null;
  }

  isRecording = false;
}

// Start the audio only when the user clicked the button
// (due to the gesture requirement for the Web Audio API)
startAudioButton.addEventListener("click", () => {
  startAudioButton.disabled = true;
  startAudioButton.textContent = "🎤 Modo Voz";
  startAudioButton.style.display = "none";
  stopAudioButton.style.display = "inline-block";
  recordingContainer.style.display = "flex";
  startAudio();
  is_audio = true;

  // Add visual feedback for audio mode
  messagesDiv.classList.add("audio-enabled");

  // Add audio mode styling to chat section
  const chatSection = document.querySelector('.chat-section');
  if (chatSection) {
    chatSection.classList.add("audio-mode");
  }

  // Enhanced recording container styling
  recordingContainer.classList.add("active");

  connectWebsocket(); // reconnect with the audio mode
});

// Stop audio recording when stop button is clicked
stopAudioButton.addEventListener("click", () => {
  stopAudio();
  stopAudioButton.style.display = "none";
  startAudioButton.style.display = "inline-block";
  startAudioButton.disabled = false;
  startAudioButton.textContent = "🎤 Activar Voz";
  recordingContainer.style.display = "none";

  // Disable the Send button when voice is deactivated
  document.getElementById("sendButton").disabled = true;

  // Remove audio styling classes
  messagesDiv.classList.remove("audio-enabled");

  // Remove audio mode styling from chat section
  const chatSection = document.querySelector('.chat-section');
  if (chatSection) {
    chatSection.classList.remove("audio-mode");
  }

  // Remove enhanced recording container styling
  recordingContainer.classList.remove("active");

  // Reconnect without audio mode
  is_audio = false;

  // Only reconnect if the connection is still open
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.close();
    // The onclose handler will trigger reconnection
  }
});

// Audio recorder handler
function audioRecorderHandler(pcmData) {
  // Only send data if we're still recording
  if (!isRecording) return;

  // Send the pcm data as base64
  sendMessage({
    mime_type: "audio/pcm",
    data: arrayBufferToBase64(pcmData),
  });

  // Log every few samples to avoid flooding the console
  if (Math.random() < 0.01) {
    // Only log ~1% of audio chunks
    console.log("[CLIENT TO AGENT] sent audio data");
  }
}

// Detect if a message should be shown in audio mode
function detectOrderMessage(text) {
  // For Cymball Bank, we WANT to show text in audio mode (agent responses/transcription)
  // This allows users to see what the agent is saying while hearing it
  return true;
}

// Encode an array buffer with Base64
function arrayBufferToBase64(buffer) {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

/**
 * Transcription handling
 */

// Display transcription message in the chat
function displayTranscription(text, role, type) {
  // Get the appropriate tracking ID based on type
  let trackingId = type === "input" ? currentInputTranscriptionId : currentOutputTranscriptionId;

  // If we have an existing transcription element for this turn, REPLACE the text
  // (the API sends accumulated text, not just new characters)
  if (trackingId) {
    const existingMessage = document.getElementById(trackingId);
    if (existingMessage) {
      const contentContainer = existingMessage.querySelector('.message-content') || existingMessage;

      // Replace the text (not append - transcription API sends full text each time)
      contentContainer.dataset.rawText = text;

      // Update the display
      if (role === "model") {
        contentContainer.innerHTML = marked.parse(text);
      } else {
        contentContainer.textContent = text;
      }

      // Scroll to the bottom
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
      return;
    }
  }

  // Create a new message element
  const messageId = Math.random().toString(36).substring(7);
  const messageElem = document.createElement("p");
  messageElem.id = messageId;

  // Set class based on role, with transcription indicator
  messageElem.className = role === "user" ? "user-message" : "agent-message";

  // Add a small transcription indicator icon
  const transcriptionIcon = document.createElement("span");
  transcriptionIcon.className = "transcription-icon";
  transcriptionIcon.textContent = type === "input" ? "🎤 " : "🔊 ";
  transcriptionIcon.style.fontSize = "0.8em";
  transcriptionIcon.style.opacity = "0.8";
  messageElem.appendChild(transcriptionIcon);

  // Create content container for the message
  const contentContainer = document.createElement("div");
  contentContainer.className = "message-content";
  contentContainer.style.display = "inline";
  contentContainer.dataset.rawText = text;

  // Handle text content based on role
  if (role === "model") {
    contentContainer.innerHTML = marked.parse(text);
  } else {
    contentContainer.textContent = text;
  }

  messageElem.appendChild(contentContainer);

  // Add the message to the DOM
  messagesDiv.appendChild(messageElem);

  // Remember the ID for subsequent transcription chunks
  if (type === "input") {
    currentInputTranscriptionId = messageId;
  } else {
    currentOutputTranscriptionId = messageId;
  }

  // Scroll to the bottom
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  console.log(`[TRANSCRIPTION] ${type}: ${text}`);
}

/**
 * Tool Logs Handling
 */
function handleToolUse(toolName, toolArgs) {
  // Use the global addToolLog function defined in index.html
  if (typeof window.addToolLog === 'function') {
    window.addToolLog(toolName, toolArgs);
  }
  console.log(`[TOOL USE] ${toolName}`, toolArgs);
}

// Custom WebSocket message handler (called from main message handler)
window.handleWebSocketMessage = function(message) {
  if (message.type === 'tool_use') {
    handleToolUse(message.tool_name, message.tool_args);
  }
};

/**
 * Context Panel Update
 */
async function loadClientContext(clienteId) {
  try {
    const response = await fetch(`/api/cliente/${clienteId}`);
    const data = await response.json();
    
    if (data.success && data.cliente) {
      const c = data.cliente;
      
      // Update context panel
      document.getElementById('ctx-nombre').textContent = c.nombre || 'N/A';
      document.getElementById('ctx-tempo').textContent = c.tiempo_cliente || 'N/A';
      
      // Update CPF
      const cpfEl = document.getElementById('ctx-dui');
      if (cpfEl) {
        cpfEl.textContent = c.dui || 'N/A';
      }
      
      // Calculate available limit
      const limiteDisponivel = (c.limite_credito || 0) - (c.limite_usado || 0);
      document.getElementById('ctx-limite').textContent = `${limiteDisponivel.toLocaleString('es-SV', {minimumFractionDigits: 2})}`;
      
      // Update card status with color
      const statusEl = document.getElementById('ctx-tarjeta-status');
      statusEl.textContent = c.tarjeta_status === 'activa' ? 'Activa ✅' : 
                              c.tarjeta_status === 'bloqueada' ? 'Bloqueada 🔐' : c.tarjeta_status;
      statusEl.style.color = c.tarjeta_status === 'activa' ? 'var(--cymball-success)' : 'var(--cymball-error)';
      
      // Load invoice info
      loadFaturaContext(clienteId);
    }
  } catch (error) {
    console.error('Error loading client context:', error);
  }
}

async function loadFaturaContext(clienteId) {
  try {
    const response = await fetch(`/api/estado-cuenta/${clienteId}`);
    const data = await response.json();
    
    const faturaEl = document.getElementById('ctx-pago-minimo');
    const statusEl = document.getElementById('ctx-pago-minimo-status');
    
    if (data.estado_cuenta) {
      faturaEl.textContent = `$${data.estado_cuenta.pago_minimo.toLocaleString('es-SV', {minimumFractionDigits: 2})}`;
      faturaEl.style.color = data.estado_cuenta.status === 'en_mora' ? 'var(--cymball-error)' : 'var(--cymball-blue)';
      statusEl.textContent = data.estado_cuenta.status === 'en_mora' ? 
        `⚠️ ${data.estado_cuenta.dias_mora} días de atraso` : 'Al día';
    } else {
      faturaEl.textContent = '$0.00';
      faturaEl.style.color = 'var(--cymball-success)';
      statusEl.textContent = 'Sin estado de cuenta pendiente';
    }
  } catch (error) {
    console.error('Error loading invoice context:', error);
  }
}

/**
 * Transactions Panel - Dynamic Loading
 */
async function loadTransactions(clienteId) {
  const container = document.getElementById('transactions-container');
  
  try {
    const response = await fetch(`/api/transacciones/${clienteId}`);
    const data = await response.json();
    
    if (data.success && data.transacciones && data.transacciones.length > 0) {
      container.innerHTML = '';
      
      // Sort by date (newest first)
      const sorted = data.transacciones.sort((a, b) => 
        new Date(b.fecha) - new Date(a.fecha)
      );
      
      sorted.forEach((txn, index) => {
        const item = document.createElement('div');
        item.className = 'txn-item';
        
        // Determine styling based on status
        let statusStyle = '';
        let statusIcon = '';
        let amountColor = '';
        
        if (txn.status === 'rechazada' || txn.status === 'bloqueada') {
          statusStyle = 'border-left: 3px solid var(--cymball-error); padding-left: 10px; background: #fff5f5;';
          statusIcon = '🔐 ';
          amountColor = 'color: var(--cymball-error);';
        } else if (txn.status === 'en_disputa') {
          statusStyle = 'border-left: 3px solid var(--cymball-warning); padding-left: 10px; background: #fffbf0;';
          statusIcon = '⚠️ ';
          amountColor = 'color: var(--cymball-warning);';
        } else if (index > 0) {
          statusStyle = 'opacity: 0.7;';
        }
        
        // Add icon if transaction has one (e.g., pet transactions)
        const icon = txn.icone || '';
        
        // Format date
        const date = new Date(txn.fecha);
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        let dateStr;
        if (date.toDateString() === today.toDateString()) {
          dateStr = `Hoy, ${date.toLocaleTimeString('es-SV', {hour: '2-digit', minute: '2-digit'})}`;
        } else if (date.toDateString() === yesterday.toDateString()) {
          dateStr = `Ayer, ${date.toLocaleTimeString('es-SV', {hour: '2-digit', minute: '2-digit'})}`;
        } else {
          dateStr = date.toLocaleDateString('es-SV', {day: '2-digit', month: 'short'});
        }
        
        item.style.cssText = statusStyle;
        item.innerHTML = `
          <div class="txn-info">
            <h4>${statusIcon}${icon} ${txn.nombre_comercio}</h4>
            <div class="txn-date" style="font-size: 0.8rem; color: #888;">${dateStr}</div>
          </div>
          <div class="txn-amount" style="font-weight: 600; ${amountColor}">
            ${txn.valor.toLocaleString('es-SV', {minimumFractionDigits: 2})}
          </div>
        `;
        
        container.appendChild(item);
      });
    } else {
      container.innerHTML = `
        <div style="color: #888; text-align: center; padding: 20px;">
          📄 No se encontraron transacciones
        </div>
      `;
    }
  } catch (error) {
    console.error('Error loading transactions:', error);
    container.innerHTML = `
      <div style="color: var(--cymball-error); text-align: center; padding: 20px;">
        ❌ Error al cargar transacciones
      </div>
    `;
  }
}

// Scenario selector handler
document.addEventListener('DOMContentLoaded', () => {
  const scenarioSelector = document.getElementById('scenario-selector');
  
  if (scenarioSelector) {
    // Load initial context and transactions
    const initialClientId = scenarioSelector.value;
    loadClientContext(initialClientId);
    loadTransactions(initialClientId);
    
    // Handle scenario change
    scenarioSelector.addEventListener('change', (e) => {
      const clienteId = e.target.value;
      
      // Sync journey tabs with scenario selector
      const journeyMap = {
        'roberto_garcia_001': 'roberto',
        'carolina_martinez_002': 'carolina',
        'javier_fernandez_003': 'javier',
        'maria_elena_lopez_004': 'maria_elena'
      };
      if (typeof window.showJourney === 'function' && journeyMap[clienteId]) {
        window.showJourney(journeyMap[clienteId]);
      }
      
      // Load new client context and transactions
      loadClientContext(clienteId);
      loadTransactions(clienteId);
      
      // Clear chat messages when scenario changes
      const messagesDiv = document.getElementById('messages');
      messagesDiv.innerHTML = '';
      
      // Clear tool logs
      const toolLogs = document.getElementById('tool-logs');
      toolLogs.innerHTML = `
        <div style="color: #888; text-align: center; padding: 20px;">
          🔧 Las llamadas de herramientas aparecerán aquí...
        </div>
      `;
      
      // Reset WebSocket session to clear agent memory (fresh start)
      // Generate new session ID so agent forgets previous conversation
      sessionId = "session_" + Date.now();
      console.log(`[SCENARIO] Changed to: ${clienteId}, new session: ${sessionId}`);
      
      // Close existing WebSocket (will trigger reconnection with new session)
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.close();
        // Note: onclose handler will automatically reconnect with new sessionId
      }
    });
  }
});
