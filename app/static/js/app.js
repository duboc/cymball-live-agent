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
    connectionStatus.textContent = window.bankConfig?.ui_text?.chat_status_connected || "Conectado";
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
  startAudioButton.textContent = "🎤 Ativar Voz";
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
      document.getElementById('ctx-nombre').textContent = c.nome || c.nombre || 'N/A';
      document.getElementById('ctx-tempo').textContent = c.tempo_cliente || c.tiempo_cliente || 'N/A';

      // Update CPF
      const cpfEl = document.getElementById('ctx-dni');
      if (cpfEl) {
        cpfEl.textContent = c.cpf || c.dni || 'N/A';
      }

      // Update profile tags
      const perfilTag = document.getElementById('ctx-perfil-tag');
      if (perfilTag) perfilTag.textContent = c.vinculo || c.perfil || 'Cliente';
      const deviceTag = document.getElementById('ctx-device');
      if (deviceTag) deviceTag.textContent = c.tipo_tarjeta || 'N/A';

      // Calculate available limit / total pre-approved value
      const limiteEl = document.getElementById('ctx-limite');
      const limiteLabelEl = document.getElementById('ctx-limite-label');
      const limiteDisponivel = c.valor_total_pre_aprovado || ((c.limite_credito || 0) - (c.limite_usado || 0));
      if (limiteDisponivel > 0) {
        if (limiteLabelEl) limiteLabelEl.textContent = 'Valor Pre-Aprovado';
        limiteEl.textContent = `R$ ${limiteDisponivel.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
        limiteEl.style.color = 'var(--bank-success)';
      } else if (c.margem_disponivel) {
        if (limiteLabelEl) limiteLabelEl.textContent = 'Margem Consignavel';
        limiteEl.textContent = `R$ ${c.margem_disponivel.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
        limiteEl.style.color = 'var(--bank-warning)';
      } else {
        if (limiteLabelEl) limiteLabelEl.textContent = 'Valor Pre-Aprovado';
        limiteEl.textContent = 'R$ 0,00';
        limiteEl.style.color = 'var(--bank-success)';
      }

      // Update proposals count
      const propostas = c.propostas_pre_aprovadas ? Object.keys(c.propostas_pre_aprovadas).length : 0;
      const faturaEl = document.getElementById('ctx-pago-minimo');
      const faturaStatusEl = document.getElementById('ctx-pago-minimo-status');
      if (faturaEl) {
        if (propostas > 0) {
          faturaEl.textContent = `${propostas} proposta${propostas !== 1 ? 's' : ''}`;
          faturaEl.style.color = 'var(--bank-primary)';
        } else {
          faturaEl.textContent = 'Simulacao disponivel';
          faturaEl.style.color = 'var(--bank-warning)';
        }
      }
      if (faturaStatusEl) {
        if (propostas > 0) {
          faturaStatusEl.textContent = 'Pre-aprovada' + (propostas !== 1 ? 's' : '');
        } else {
          faturaStatusEl.textContent = c.simulacao ? 'Margem: R$ ' + c.margem_disponivel?.toLocaleString('pt-BR', {minimumFractionDigits: 2}) : 'Sem propostas';
        }
      }

      // Update card status with color
      const statusEl = document.getElementById('ctx-tarjeta-status');
      statusEl.textContent = c.tarjeta_status === 'ativo' ? 'Ativo ✅' :
                              c.tarjeta_status === 'bloqueado' ? 'Bloqueado 🔐' : c.tarjeta_status;
      statusEl.style.color = c.tarjeta_status === 'ativo' ? 'var(--bank-success)' : 'var(--bank-error)';
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
    
    if (data.estado_cuenta && data.estado_cuenta.pago_minimo) {
      faturaEl.textContent = `R$ ${data.estado_cuenta.pago_minimo.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
      faturaEl.style.color = data.estado_cuenta.status === 'en_mora' ? 'var(--bank-error)' : 'var(--bank-primary)';
      statusEl.textContent = data.estado_cuenta.status === 'en_mora' ?
        `⚠️ ${data.estado_cuenta.dias_mora} dias de atraso` : 'Em dia';
    } else {
      // For proposal-based scenarios, show proposal count
      faturaEl.textContent = '4 propostas';
      faturaEl.style.color = 'var(--bank-primary)';
      statusEl.textContent = 'Pre-aprovadas';
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
      
      sorted.forEach((txn) => {
        const item = document.createElement('div');
        item.className = 'txn-item';

        // Proposal-specific rendering
        const isProposal = txn.categoria === 'proposta_pre_aprovada';
        const typeIcons = {
          'emprestimo_consignado': '💰',
          'credito_pessoal': '💳',
          'portabilidade': '🔄',
          'refinanciamento': '📊'
        };
        const icon = isProposal ? (typeIcons[txn.tipo] || '📄') : (txn.icone || '');

        // Status styling
        let statusStyle = '';
        let statusBadge = '';
        let amountColor = 'color: var(--bank-success); font-weight: 700;';

        if (txn.status === 'pre_aprovada') {
          statusStyle = 'border-left: 3px solid var(--bank-success); padding-left: 10px; background: #f0faf4;';
          statusBadge = '<span style="font-size: 0.65rem; background: var(--bank-success); color: white; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">PRE-APROVADA</span>';
        } else if (txn.status === 'contratada') {
          statusStyle = 'border-left: 3px solid var(--bank-primary); padding-left: 10px; background: #e8f5e9;';
          statusBadge = '<span style="font-size: 0.65rem; background: var(--bank-primary); color: white; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">CONTRATADA</span>';
        } else if (txn.status === 'rechazada' || txn.status === 'bloqueada') {
          statusStyle = 'border-left: 3px solid var(--bank-error); padding-left: 10px; background: #fff5f5;';
          amountColor = 'color: var(--bank-error);';
        }

        // Format value display
        const valorDisplay = txn.valor > 0
          ? `R$ ${txn.valor.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`
          : 'Sem valor liberado';
        const valorColor = txn.valor > 0 ? amountColor : 'color: #999; font-size: 0.8rem;';

        // Proposal name (clean up "Proposta XXXXX - " prefix for cleaner display)
        const displayName = txn.nombre_comercio.replace(/^Proposta \d+ - /, '');

        item.style.cssText = statusStyle;
        item.innerHTML = `
          <div class="txn-info" style="flex: 1;">
            <h4 style="display: flex; align-items: center; flex-wrap: wrap;">${icon} ${displayName}${statusBadge}</h4>
            <div style="font-size: 0.75rem; color: #888; margin-top: 2px;">N. ${txn.nombre_comercio.match(/\d{9}/)?.[0] || ''}</div>
          </div>
          <div style="text-align: right; ${valorColor}">
            ${valorDisplay}
          </div>
        `;

        container.appendChild(item);
      });
    } else {
      // Check if this client has simulation data
      try {
        const clientResp = await fetch(`/api/cliente/${clienteId}`);
        const clientData = await clientResp.json();
        if (clientData.success && clientData.cliente && clientData.cliente.simulacao) {
          const sim = clientData.cliente.simulacao;
          container.innerHTML = `
            <div style="padding: 16px;">
              <div style="text-align: center; margin-bottom: 16px;">
                <span style="font-size: 2rem;">🧮</span>
                <h4 style="color: var(--bank-primary); margin-top: 8px;">Simulacao de Financiamento</h4>
                <p style="font-size: 0.85rem; color: #666;">Este cliente nao possui propostas pre-aprovadas, mas pode simular um novo emprestimo.</p>
              </div>
              <div style="background: #f8f8f8; border-radius: 12px; padding: 14px; margin-bottom: 12px;">
                <div style="font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px;">Margem Consignavel (35%)</div>
                <div style="font-weight: 700; font-size: 1.1rem; color: var(--bank-success);">R$ ${sim.margem_consignavel_35.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <div style="background: #f8f8f8; border-radius: 8px; padding: 10px;">
                  <div style="font-size: 0.7rem; color: #666;">Taxa Mensal</div>
                  <div style="font-weight: 600;">${sim.taxa_mensal}% a.m.</div>
                </div>
                <div style="background: #f8f8f8; border-radius: 8px; padding: 10px;">
                  <div style="font-size: 0.7rem; color: #666;">Taxa Anual</div>
                  <div style="font-weight: 600;">${sim.taxa_anual}% a.a.</div>
                </div>
                <div style="background: #f8f8f8; border-radius: 8px; padding: 10px;">
                  <div style="font-size: 0.7rem; color: #666;">CET Mensal</div>
                  <div style="font-weight: 600;">${sim.cet_mensal}% a.m.</div>
                </div>
                <div style="background: #f8f8f8; border-radius: 8px; padding: 10px;">
                  <div style="font-size: 0.7rem; color: #666;">CET Anual</div>
                  <div style="font-weight: 600;">${sim.cet_anual}% a.a.</div>
                </div>
                <div style="background: #f8f8f8; border-radius: 8px; padding: 10px;">
                  <div style="font-size: 0.7rem; color: #666;">Prazo Maximo</div>
                  <div style="font-weight: 600;">${sim.prazo_maximo_meses} meses</div>
                </div>
                <div style="background: #f8f8f8; border-radius: 8px; padding: 10px;">
                  <div style="font-size: 0.7rem; color: #666;">Sistema</div>
                  <div style="font-weight: 600;">${sim.sistema_amortizacao}</div>
                </div>
              </div>
              <div style="margin-top: 14px; background: #e8f5e9; border-radius: 8px; padding: 12px; font-size: 0.85rem; color: #2e7d32;">
                💡 Peca a Sara para simular um valor e prazo!
              </div>
            </div>
          `;
        } else {
          container.innerHTML = `
            <div style="color: #888; text-align: center; padding: 20px;">
              📄 Nenhuma movimentacao encontrada
            </div>
          `;
        }
      } catch {
        container.innerHTML = `
          <div style="color: #888; text-align: center; padding: 20px;">
            📄 Nenhuma movimentacao encontrada
          </div>
        `;
      }
    }
  } catch (error) {
    console.error('Error loading transactions:', error);
    container.innerHTML = `
      <div style="color: var(--bank-error); text-align: center; padding: 20px;">
        ❌ Erro ao carregar movimentacoes
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
        'maria_santos_001': 'maria',
        'jose_carlos_002': 'jose',
        'ana_beatriz_003': 'ana',
        'roberto_lima_004': 'roberto',
        'francisca_oliveira_005': 'francisca'
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
          🔧 As chamadas de ferramentas aparecerao aqui...
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
