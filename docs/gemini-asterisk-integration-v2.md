# Gemini Live API - Asterisk/FreePBX Integration (v2)

## Using chan_websocket (Asterisk 21.11.0+)

This documentation describes how to connect Asterisk/FreePBX to Google's Gemini Live API via a Cloud Run WebSocket service, enabling voice conversations with AI through phone calls.

**Version 2** uses the new `chan_websocket` channel driver available in Asterisk 21.11.0+ which provides automatic audio timing and framing, resulting in better audio quality compared to the AudioSocket approach.

---

## Architecture

```
┌─────────────┐     ┌─────────────────────┐     ┌──────────────────────────────────┐
│  Softphone  │────▶│   FreePBX/Asterisk  │────▶│         Bridge Service           │
│  or Phone   │◀────│   (GCE)             │◀────│   (Python WebSocket Server)      │
└─────────────┘ SIP └─────────────────────┘     └──────────────────────────────────┘
                        chan_websocket                        │
                     ws://localhost:8765                      │ WebSocket (wss)
                                                              ▼
                                                 ┌──────────────────────────────────┐
                                                 │  Cloud Run (ADK Agent)           │
                                                 │  wss://your-service.run.app/ws   │
                                                 └──────────────────────────────────┘
                                                              │
                                                              ▼
                                                 ┌──────────────────────────────────┐
                                                 │  Gemini Live API                 │
                                                 │  (Google AI)                     │
                                                 └──────────────────────────────────┘
```

---

## Audio Flow

### Input (User Speech → Gemini)
1. User speaks into phone/softphone
2. Asterisk receives audio via SIP
3. chan_websocket sends **slin16** (16kHz 16-bit PCM) to bridge via WebSocket
4. Bridge forwards directly to Cloud Run (no conversion needed - Gemini expects 16kHz!)
5. Cloud Run forwards to Gemini Live API

### Output (Gemini Response → User)
1. Gemini Live API sends 24kHz 16-bit PCM audio
2. Cloud Run forwards to bridge via WebSocket
3. Bridge downsamples 24kHz → 16kHz
4. Bridge sends to Asterisk via WebSocket
5. **chan_websocket handles all timing/framing automatically**
6. Asterisk plays audio to user via SIP

---

## Audio Format Specifications

| Stage | Format | Sample Rate | Bit Depth |
|-------|--------|-------------|-----------|
| Asterisk chan_websocket | Signed Linear PCM (slin16) | 16 kHz | 16-bit |
| Gemini Live Input | Signed Linear PCM | 16 kHz | 16-bit |
| Gemini Live Output | Signed Linear PCM | 24 kHz | 16-bit |

**Key Advantage**: Using slin16 codec means no sample rate conversion is needed for input audio!

---

## Prerequisites

- **Asterisk 21.11.0 or higher** (for chan_websocket support)
- FreePBX 17.x
- Python 3.x with venv support
- Cloud Run service running the ADK agent
- SIP softphone or phone for testing

---

## Installation

### Step 1: Verify Asterisk Version

```bash
asterisk -V
```

If version is below 21.11.0, you need to upgrade (see Appendix A).

Verify chan_websocket is available:

```bash
sudo asterisk -rx "module show like websocket"
```

You should see `chan_websocket.so` in the output:
```
chan_websocket.so              Websocket Media Channel                  0          Running              core
res_http_websocket.so          HTTP WebSocket Support                   6          Running              core
res_pjsip_transport_websocket.so PJSIP WebSocket Transport Support        0          Running              core
res_websocket_client.so        WebSocket Client Support                 2          Running              core
```

### Step 2: Create Bridge Directory and Virtual Environment

```bash
sudo mkdir -p /opt/gemini-bridge
cd /opt/gemini-bridge

# Create virtual environment
sudo python3 -m venv venv

# Bootstrap pip if needed
curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
sudo /opt/gemini-bridge/venv/bin/python /tmp/get-pip.py

# Install dependencies
sudo /opt/gemini-bridge/venv/bin/pip install websockets
```

### Step 3: Create Bridge Script

Create the file `/opt/gemini-bridge/bridge.py`:

```python
#!/usr/bin/env python3
"""
Bridge between Asterisk chan_websocket and Gemini Live API.
Asterisk connects to us via WebSocket, we connect to Cloud Run.
"""
import asyncio
import audioop
import base64
import json
import logging
import uuid as uuid_lib
import websockets
from websockets.server import serve

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# UPDATE THIS URL to your Cloud Run service
CLOUD_RUN_WS_URL = "wss://your-service.run.app/ws"

# slin16 = 16kHz, same as Gemini input - no conversion needed for input!
ASTERISK_RATE = 16000
GEMINI_INPUT_RATE = 16000
GEMINI_OUTPUT_RATE = 24000


class GeminiBridge:
    def __init__(self, asterisk_ws, session_id):
        self.asterisk_ws = asterisk_ws
        self.session_id = session_id
        self.gemini_ws = None
        self.running = True
        self.downsample_state = None

    async def connect_gemini(self):
        url = f"{CLOUD_RUN_WS_URL}/{self.session_id}?is_audio=true"
        logger.info(f"Connecting to Gemini: {url}")
        self.gemini_ws = await websockets.connect(url, ping_interval=20, ping_timeout=10)
        logger.info("Connected to Gemini")

    async def handle_asterisk_message(self, message):
        if isinstance(message, bytes):
            # Binary = audio from Asterisk (slin16 = 16kHz)
            # Gemini expects 16kHz - no conversion needed!
            msg = {
                "mime_type": "audio/pcm",
                "data": base64.b64encode(message).decode('ascii'),
                "role": "user"
            }
            await self.gemini_ws.send(json.dumps(msg))
            
        elif isinstance(message, str):
            try:
                data = json.loads(message)
                event = data.get("event")
                
                if event == "MEDIA_START":
                    logger.info(f"MEDIA_START: channel={data.get('channel')}, format={data.get('format')}")
                elif event == "DTMF_END":
                    logger.info(f"DTMF: {data.get('digit')}")
                elif event == "MEDIA_XOFF":
                    logger.warning("Asterisk buffer full")
                elif event == "MEDIA_XON":
                    logger.info("Asterisk buffer ok")
                else:
                    logger.debug(f"Asterisk event: {event}")
                    
            except json.JSONDecodeError:
                logger.debug(f"Asterisk text: {message}")

    async def asterisk_to_gemini(self):
        try:
            async for message in self.asterisk_ws:
                if not self.running:
                    break
                await self.handle_asterisk_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Asterisk disconnected")
        except Exception as e:
            logger.error(f"Error asterisk->gemini: {e}")
        finally:
            self.running = False

    async def gemini_to_asterisk(self):
        try:
            while self.running:
                try:
                    message_json = await asyncio.wait_for(self.gemini_ws.recv(), timeout=30.0)
                except asyncio.TimeoutError:
                    continue

                message = json.loads(message_json)
                mime_type = message.get("mime_type")
                data = message.get("data")
                msg_type = message.get("type")

                if mime_type == "audio/pcm" and data:
                    audio_24k = base64.b64decode(data)
                    if len(audio_24k) == 0:
                        continue

                    # Downsample 24kHz -> 16kHz for Asterisk
                    audio_16k, self.downsample_state = audioop.ratecv(
                        audio_24k, 2, 1, GEMINI_OUTPUT_RATE, ASTERISK_RATE, self.downsample_state
                    )

                    # Send binary audio - Asterisk handles timing automatically!
                    await self.asterisk_ws.send(audio_16k)

                elif message.get("interrupted"):
                    logger.info("Interrupted")

                elif msg_type == "input_transcription":
                    text = message.get('data', '')
                    if text:
                        logger.info(f"[User]: {text}")
                        
                elif msg_type == "output_transcription":
                    text = message.get('data', '')
                    if text:
                        logger.info(f"[Agent]: {text}")

        except websockets.exceptions.ConnectionClosed:
            logger.info("Gemini disconnected")
        except Exception as e:
            logger.error(f"Error gemini->asterisk: {e}")
        finally:
            self.running = False

    async def run(self):
        try:
            await self.connect_gemini()
            await asyncio.gather(
                self.asterisk_to_gemini(),
                self.gemini_to_asterisk(),
                return_exceptions=True
            )
        finally:
            if self.gemini_ws:
                await self.gemini_ws.close()
            logger.info("Bridge closed")


async def handle_connection(websocket, path):
    logger.info(f"Asterisk connected: {path}")
    session_id = f"phone-{uuid_lib.uuid4().hex[:8]}"
    bridge = GeminiBridge(websocket, session_id)
    await bridge.run()


async def main():
    server = await serve(handle_connection, "0.0.0.0", 8765, ping_interval=20, ping_timeout=10)
    logger.info("WebSocket bridge listening on ws://0.0.0.0:8765")
    await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
```

### Step 4: Create Systemd Service

Create `/etc/systemd/system/gemini-bridge.service`:

```ini
[Unit]
Description=Gemini Live Audio Bridge
After=network.target asterisk.service

[Service]
Type=simple
User=asterisk
WorkingDirectory=/opt/gemini-bridge
ExecStart=/opt/gemini-bridge/venv/bin/python /opt/gemini-bridge/bridge.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gemini-bridge
sudo systemctl start gemini-bridge
```

### Step 5: Configure WebSocket Client

Create `/etc/asterisk/websocket_client.conf`:

```ini
[gemini_bridge]
type = websocket_client
connection_type = per_call_config
uri = ws://127.0.0.1:8765/media
protocols =
connection_timeout = 2000
reconnect_attempts = 2
```

### Step 6: Configure Asterisk Dialplan

Edit `/etc/asterisk/extensions_custom.conf`:

```ini
[gemini-live]
exten => s,1,NoOp(Starting Gemini Live WebSocket)
same => n,Answer()
same => n,Wait(0.5)
same => n,Dial(WebSocket/gemini_bridge/c(slin16),60)
same => n,Hangup()

[from-internal-custom]
exten => 9999,1,NoOp(Dialing Gemini AI)
same => n,Goto(gemini-live,s,1)
```

### Step 7: Reload Configuration

```bash
sudo fwconsole restart
```

Or reload individual components:

```bash
sudo asterisk -rx "module reload res_websocket_client.so"
sudo asterisk -rx "dialplan reload"
```

---

## Testing

1. Verify bridge is running:
   ```bash
   sudo systemctl status gemini-bridge
   ss -tlnp | grep 8765
   ```

2. Register a SIP softphone to FreePBX (e.g., extension 205)

3. Dial `9999`

4. Speak and wait for Gemini's response

5. Watch the bridge logs:
   ```bash
   sudo journalctl -u gemini-bridge -f
   ```

---

## Monitoring & Debugging

### View Bridge Logs

```bash
sudo journalctl -u gemini-bridge -f
```

### Check Bridge Status

```bash
sudo systemctl status gemini-bridge
ss -tlnp | grep 8765
```

### Asterisk CLI Debugging

```bash
sudo asterisk -rvv
# Then dial 9999 and watch the output
```

### Verify Modules Loaded

```bash
sudo asterisk -rx "module show like websocket"
```

### Verify Dialplan

```bash
sudo asterisk -rx "dialplan show gemini-live"
sudo asterisk -rx "dialplan show 9999@from-internal-custom"
```

---

## Troubleshooting

### Problem: "WebSocket client connection 'gemini_bridge' not found"

**Cause**: websocket_client.conf not loaded or incorrect format

**Solution**:
```bash
# Check config file
cat /etc/asterisk/websocket_client.conf

# Ensure type = websocket_client (not type = client)

# Reload module
sudo fwconsole restart
```

### Problem: "Unrecognized option: 'f'"

**Cause**: The `f(json)` option may not be supported

**Solution**: Remove the `f(json)` option from the dialplan:
```ini
same => n,Dial(WebSocket/gemini_bridge/c(slin16),60)
```

### Problem: No Audio Playback

1. Check bridge is running: `sudo systemctl status gemini-bridge`
2. Check bridge is listening: `ss -tlnp | grep 8765`
3. Check logs: `sudo journalctl -u gemini-bridge -f`
4. Verify Cloud Run URL is correct in bridge.py

### Problem: chan_websocket.so Not Found

**Cause**: Asterisk version is below 21.11.0

**Solution**: Upgrade Asterisk (see Appendix A)

---

## File Locations Summary

| File | Purpose |
|------|---------|
| `/opt/gemini-bridge/bridge.py` | Main bridge script |
| `/opt/gemini-bridge/venv/` | Python virtual environment |
| `/etc/systemd/system/gemini-bridge.service` | Systemd service file |
| `/etc/asterisk/extensions_custom.conf` | Asterisk dialplan |
| `/etc/asterisk/websocket_client.conf` | WebSocket client configuration |

---

## Comparison: chan_websocket vs AudioSocket

| Feature | chan_websocket (v2) | AudioSocket (v1) |
|---------|---------------------|------------------|
| Asterisk Version | 21.11.0+ | Any |
| Audio Timing | Automatic | Manual |
| Input Sample Rate | 16kHz (slin16) | 8kHz |
| Input Conversion | None needed | 8kHz → 16kHz |
| Output Conversion | 24kHz → 16kHz | 24kHz → 8kHz |
| Audio Quality | Better | May be choppy |
| Complexity | Lower | Higher |

---

## Appendix A: Upgrading Asterisk to 21.12.0

If your Asterisk version is below 21.11.0, follow these steps to upgrade:

### 1. Backup

```bash
sudo tar -czvf /root/asterisk-backup-$(date +%Y%m%d).tar.gz /etc/asterisk/
sudo cp -r /opt/gemini-bridge /root/gemini-bridge-backup
```

### 2. Install Build Dependencies

```bash
sudo apt update
sudo apt install -y build-essential wget libssl-dev libncurses5-dev libnewt-dev \
    libxml2-dev linux-headers-$(uname -r) libsqlite3-dev uuid-dev libjansson-dev \
    libsrtp2-dev libcurl4-openssl-dev libedit-dev pkg-config subversion
```

### 3. Download and Compile

```bash
cd /usr/src
sudo wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-21.12.0.tar.gz
sudo tar -xzvf asterisk-21.12.0.tar.gz
cd asterisk-21.12.0

# Install prerequisites
sudo contrib/scripts/install_prereq install

# Configure
sudo ./configure

# Enable chan_websocket
sudo make menuselect.makeopts
sudo menuselect/menuselect --enable chan_websocket menuselect.makeopts
sudo menuselect/menuselect --enable res_http_websocket menuselect.makeopts

# Compile (takes 5-10 minutes)
sudo make -j$(nproc)

# Install
sudo make install
```

### 4. Restart and Verify

```bash
sudo fwconsole restart
asterisk -V
sudo asterisk -rx "module show like websocket"
```

---

## Appendix B: Cloud Run Service Requirements

The Cloud Run service (ADK Agent) must implement:

### WebSocket Endpoint
- Accept connections at `/ws/{session_id}?is_audio=true`

### Input Message Format
```json
{
  "mime_type": "audio/pcm",
  "data": "<base64-encoded-16kHz-16bit-PCM>",
  "role": "user"
}
```

### Output Message Formats

**Audio Response:**
```json
{
  "mime_type": "audio/pcm",
  "data": "<base64-encoded-24kHz-16bit-PCM>",
  "role": "model"
}
```

**Transcription Events:**
```json
{
  "type": "input_transcription",
  "data": "user's speech text",
  "role": "user",
  "finished": true
}
```

```json
{
  "type": "output_transcription",
  "data": "agent's response text",
  "role": "model",
  "finished": true
}
```

**Control Events:**
```json
{"turn_complete": true}
{"interrupted": true}
```

---

## References

- [Asterisk WebSocket Channel Driver Documentation](https://docs.asterisk.org/Configuration/Channel-Drivers/WebSocket/)
- [Gemini Live API Documentation](https://ai.google.dev/api/live)
- [Google ADK (Agent Development Kit)](https://github.com/google/adk-python)
- [FreePBX Documentation](https://wiki.freepbx.org/)

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-23 | 2.0 | New version using chan_websocket (Asterisk 21.11.0+) |
| 2026-01-23 | 1.0 | Initial version using AudioSocket |
