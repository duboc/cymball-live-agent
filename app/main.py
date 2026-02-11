"""
Banking Agent Server
====================

FastAPI server that serves the banking agent UI and handles WebSocket
communication with Google's Gemini Live API.

Configuration is loaded from config.py.
"""

import asyncio
import base64
import json
import logging
import os
from pathlib import Path
from typing import AsyncIterable

from dotenv import load_dotenv
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.events.event import Event
from google.adk.runners import InMemoryRunner
from google.genai import types

# Import configuration and agent
# Support both relative imports (when run as module) and absolute imports (when run directly)
try:
    from .config import (
        BANK_NAME,
        BANK_COUNTRY,
        BANK_CURRENCY,
        BANK_CURRENCY_SYMBOL,
        AGENT_NAME,
        AGENT_VOICE,
        BRAND_COLORS,
        UI_TEXT,
        SCENARIOS,
    )
    from .agent.agent import root_agent
except ImportError:
    from config import (
        BANK_NAME,
        BANK_COUNTRY,
        BANK_CURRENCY,
        BANK_CURRENCY_SYMBOL,
        AGENT_NAME,
        AGENT_VOICE,
        BRAND_COLORS,
        UI_TEXT,
        SCENARIOS,
    )
    from agent.agent import root_agent

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

#
# ADK Streaming
#

# Load Gemini API Key
load_dotenv()

# App name from config
APP_NAME = UI_TEXT["app_title"]


async def start_agent_session(session_id, is_audio=False):
    """Starts an agent session"""

    # Create a Runner
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=root_agent,
    )

    # Create a Session
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
    )

    # Detect if using native audio model
    model_name = root_agent.model
    is_native_audio = "native-audio" in model_name.lower()

    # Native audio models ONLY support AUDIO output modality
    # Half-cascade models (like gemini-live-2.5-flash-preview) support both TEXT and AUDIO
    if is_native_audio:
        modality = "AUDIO"
        logger.info(f"Native audio model detected: {model_name}, forcing AUDIO modality")
    else:
        modality = "AUDIO" if is_audio else "TEXT"

    # Create speech config with voice settings from config
    speech_config = types.SpeechConfig(
        voice_config=types.VoiceConfig(
            # Available voices: Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=AGENT_VOICE)
        )
    )

    # Create run config with basic settings
    config = {"response_modalities": [modality]}

    # Add audio transcription when using audio mode or native audio model
    if is_audio or is_native_audio:
        config["speech_config"] = speech_config
        # Enable input transcription for speech-to-text
        config["input_audio_transcription"] = types.AudioTranscriptionConfig()
        # Enable output transcription to get text version of audio response
        config["output_audio_transcription"] = types.AudioTranscriptionConfig()
        logger.debug("Audio transcription enabled (input and output)")
    else:
        # Disable VAD for text-only sessions to avoid "Cannot extract voices" error
        config["realtime_input_config"] = {
            "automatic_activity_detection": {"disabled": True}
        }

    run_config = RunConfig(**config)
    logger.debug(f"RunConfig created with modality: {modality}, is_audio: {is_audio}, is_native_audio: {is_native_audio}")

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue


async def agent_to_client_messaging(
    websocket: WebSocket, live_events: AsyncIterable[Event | None]
):
    """Agent to client communication"""
    async for event in live_events:
        if event is None:
            continue

        # If the turn complete or interrupted, send it
        if event.turn_complete or event.interrupted:
            message = {
                "turn_complete": event.turn_complete,
                "interrupted": event.interrupted,
            }
            await websocket.send_text(json.dumps(message))
            logger.debug(f"[AGENT TO CLIENT]: {message}")
            continue

        # Handle transcription events (input and output)
        # Transcription attributes are directly on the event object
        transcription_sent = False

        # Input transcription (user's speech -> text)
        if hasattr(event, 'input_transcription') and event.input_transcription:
            transcription = event.input_transcription
            text = getattr(transcription, 'text', None)
            finished = getattr(transcription, 'finished', False)
            logger.debug(f"[TRANSCRIPTION DEBUG] input: text={text}, finished={finished}")
            # Send ALL transcriptions (not just finished) - frontend handles replacement
            if text and text.strip():
                message = {
                    "type": "input_transcription",
                    "data": text,
                    "role": "user",
                    "finished": finished,
                }
                await websocket.send_text(json.dumps(message))
                logger.info(f"[TRANSCRIPTION] input: {text} (finished={finished})")
                transcription_sent = True

        # Output transcription (model's speech -> text)
        if hasattr(event, 'output_transcription') and event.output_transcription:
            transcription = event.output_transcription
            text = getattr(transcription, 'text', None)
            finished = getattr(transcription, 'finished', False)
            logger.debug(f"[TRANSCRIPTION DEBUG] output: text={text}, finished={finished}")
            # Send ALL transcriptions (not just finished) - frontend handles replacement
            if text and text.strip():
                message = {
                    "type": "output_transcription",
                    "data": text,
                    "role": "model",
                    "finished": finished,
                }
                await websocket.send_text(json.dumps(message))
                logger.info(f"[TRANSCRIPTION] output: {text} (finished={finished})")
                transcription_sent = True

        # Read the Content and its first Part
        part = event.content and event.content.parts and event.content.parts[0]
        if not part:
            continue

        # Make sure we have a valid Part
        if not isinstance(part, types.Part):
            continue

        # Only send text if it's a partial response (streaming)
        # Skip text/plain if we already sent transcription for this event
        # to avoid duplication
        if part.text and event.partial and not transcription_sent:
            message = {
                "mime_type": "text/plain",
                "data": part.text,
                "role": "model",
            }
            await websocket.send_text(json.dumps(message))
            logger.debug(f"[AGENT TO CLIENT]: text/plain: {part.text}")

        # If it's audio, send Base64 encoded audio data
        is_audio = (
            part.inline_data
            and part.inline_data.mime_type
            and part.inline_data.mime_type.startswith("audio/pcm")
        )
        if is_audio:
            audio_data = part.inline_data and part.inline_data.data
            if audio_data:
                message = {
                    "mime_type": "audio/pcm",
                    "data": base64.b64encode(audio_data).decode("ascii"),
                    "role": "model",
                }
                await websocket.send_text(json.dumps(message))
                logger.debug(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")

        # Check for Tool Calls (Function Calls)
        if part.function_call:
            fc = part.function_call
            message = {
                "type": "tool_use",
                "tool_name": fc.name,
                "tool_args": fc.args,
                "role": "model"
            }
            await websocket.send_text(json.dumps(message))
            logger.info(f"[TOOL USE]: {fc.name} args={fc.args}")


async def client_to_agent_messaging(
    websocket: WebSocket, live_request_queue: LiveRequestQueue
):
    """Client to agent communication"""
    while True:
        # Decode JSON message
        message_json = await websocket.receive_text()
        message = json.loads(message_json)
        mime_type = message["mime_type"]
        data = message["data"]
        role = message.get("role", "user")  # Default to 'user' if role is not provided

        # Send the message to the agent
        if mime_type == "text/plain":
            # Send a text message
            content = types.Content(role=role, parts=[types.Part.from_text(text=data)])
            live_request_queue.send_content(content=content)
            logger.debug(f"[CLIENT TO AGENT]: {data}")
        elif mime_type == "audio/pcm":
            # Send audio data
            decoded_data = base64.b64decode(data)

            # Send the audio data - note that ActivityStart/End and transcription
            # handling is done automatically by the ADK when input_audio_transcription
            # is enabled in the config
            live_request_queue.send_realtime(
                types.Blob(data=decoded_data, mime_type=mime_type)
            )
            logger.debug(f"[CLIENT TO AGENT]: audio/pcm: {len(decoded_data)} bytes")

        else:
            raise ValueError(f"Mime type not supported: {mime_type}")


#
# FastAPI web app
#

app = FastAPI()

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """Serves the index.html"""
    return FileResponse(STATIC_DIR / "index.html")


#
# API Endpoints for Dynamic UI
#

@app.get("/api/config")
async def get_config():
    """Returns brand configuration for the frontend"""
    return {
        "bank_name": BANK_NAME,
        "bank_country": BANK_COUNTRY,
        "currency": BANK_CURRENCY,
        "currency_symbol": BANK_CURRENCY_SYMBOL,
        "agent_name": AGENT_NAME,
        "colors": BRAND_COLORS,
        "ui_text": UI_TEXT,
        "scenarios": SCENARIOS,
    }


@app.get("/api/clientes")
async def get_clientes():
    """Returns list of all mock clients for scenario selector"""
    try:
        from .agent.data.mock_data import CLIENTES
    except ImportError:
        from agent.data.mock_data import CLIENTES

    clientes_resumen = []
    for cid, data in CLIENTES.items():
        clientes_resumen.append({
            "id": cid,
            "nombre": data["nombre"],
            "perfil": data.get("perfil", "cliente"),
            "tarjeta_status": data.get("tarjeta_status", "activa"),
            "escenario": _get_escenario_for_client(cid)
        })
    return {"clientes": clientes_resumen}


def _get_escenario_for_client(cliente_id: str) -> str:
    """Returns the journey scenario for a client"""
    if cliente_id in SCENARIOS:
        return SCENARIOS[cliente_id]["name"]
    return "General"


@app.get("/api/cliente/{cliente_id}")
async def get_cliente(cliente_id: str):
    """Returns full client profile for context panel"""
    try:
        from .agent.data.mock_data import CLIENTES
    except ImportError:
        from agent.data.mock_data import CLIENTES

    if cliente_id in CLIENTES:
        cliente = CLIENTES[cliente_id].copy()
        cliente["id"] = cliente_id
        cliente["escenario"] = _get_escenario_for_client(cliente_id)
        return {"success": True, "cliente": cliente}
    return {"success": False, "error": "Cliente no encontrado"}


@app.get("/api/transacciones/{cliente_id}")
async def get_transacciones(cliente_id: str):
    """Returns transactions for a specific client"""
    try:
        from .agent.data.mock_data import TRANSACCIONES
    except ImportError:
        from agent.data.mock_data import TRANSACCIONES

    transacciones = []
    for tid, data in TRANSACCIONES.items():
        if data["cliente_id"] == cliente_id:
            txn = data.copy()
            txn["id"] = tid
            transacciones.append(txn)
    return {"success": True, "transacciones": transacciones}


@app.get("/api/estado-cuenta/{cliente_id}")
async def get_estado_cuenta(cliente_id: str):
    """Returns account statement for a specific client"""
    try:
        from .agent.data.mock_data import ESTADOS_CUENTA
    except ImportError:
        from agent.data.mock_data import ESTADOS_CUENTA

    for eid, data in ESTADOS_CUENTA.items():
        if data["cliente_id"] == cliente_id:
            estado = data.copy()
            estado["id"] = eid
            return {"success": True, "estado_cuenta": estado}
    return {"success": True, "estado_cuenta": None, "status": "al_dia"}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    is_audio: str = Query(...),
):
    """Client websocket endpoint"""

    # Wait for client connection
    await websocket.accept()
    logger.info(f"Client #{session_id} connected, audio mode: {is_audio}")

    # Start agent session
    live_events, live_request_queue = await start_agent_session(
        session_id, is_audio == "true"
    )

    # Start tasks
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )

    # Run both tasks concurrently with proper exception handling
    try:
        await asyncio.gather(agent_to_client_task, client_to_agent_task)
    except WebSocketDisconnect:
        logger.info(f"Client #{session_id} disconnected normally")
    except Exception as e:
        logger.error(f"Unexpected error in streaming tasks for session {session_id}: {e}", exc_info=True)
    finally:
        # Always close the queue, even if exceptions occurred
        logger.debug(f"Closing live_request_queue for session {session_id}")
        live_request_queue.close()
        logger.info(f"Client #{session_id} session ended")


# For Cloud Run deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
