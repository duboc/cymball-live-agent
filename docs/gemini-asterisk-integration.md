# Gemini Live API - Asterisk/FreePBX Integration

This documentation describes how to connect Asterisk/FreePBX to Google's Gemini Live API via a Cloud Run WebSocket service, enabling voice conversations with AI through phone calls.

## Architecture

```
┌─────────────┐     ┌─────────────────────┐     ┌──────────────────────────────────┐
│  Softphone  │────▶│   FreePBX/Asterisk  │────▶│         Bridge Service           │
│  or Phone   │◀────│   (GCE)             │◀────│   (Python on FreePBX server)     │
└─────────────┘ SIP └─────────────────────┘     └──────────────────────────────────┘
                         AudioSocket                          │
                      (localhost:9092)                        │ WebSocket
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

## Audio Flow

### Input (User Speech → Gemini)
1. User speaks into phone/softphone
2. Asterisk receives audio via SIP (typically μ-law or signed linear PCM at 8kHz)
3. AudioSocket sends signed linear 16-bit PCM at 8kHz to bridge
4. Bridge upsamples 8kHz → 16kHz (Gemini Live API input requirement)
5. Bridge sends base64-encoded PCM to Cloud Run via WebSocket
6. Cloud Run forwards to Gemini Live API

### Output (Gemini Response → User)
1. Gemini Live API sends 24kHz 16-bit PCM audio
2. Cloud Run forwards to bridge via WebSocket
3. Bridge downsamples 24kHz → 8kHz
4. Bridge sends audio to Asterisk via AudioSocket
5. Asterisk plays audio to user via SIP

## Audio Format Specifications

| Stage | Format | Sample Rate | Bit Depth |
|-------|--------|-------------|-----------|
| Asterisk AudioSocket | Signed Linear PCM | 8 kHz | 16-bit |
| Gemini Live Input | Signed Linear PCM | 16 kHz | 16-bit |
| Gemini Live Output | Signed Linear PCM | 24 kHz | 16-bit |

## Prerequisites

- FreePBX/Asterisk server (tested with Asterisk 21.8.0)
- Python 3.x with venv support
- Cloud Run service running the ADK agent
- SIP softphone or phone for testing

---

## Installation

### Step 1: Create Bridge Directory and Virtual Environment

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

### Step 2: Create Bridge Script

Create the file `/opt/gemini-bridge/bridge.py` with the following content:

```python
#!/usr/bin/env python3
import asyncio
import audioop
import base64
import json
import logging
import struct
import uuid as uuid_lib
import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# UPDATE THIS URL to your Cloud Run service
CLOUD_RUN_WS_URL = "wss://your-service.run.app/ws"

ASTERISK_RATE = 8000
GEMINI_INPUT_RATE = 16000
GEMINI_OUTPUT_RATE = 24000

AUDIOSOCKET_KIND_HANGUP = 0x00
AUDIOSOCKET_KIND_UUID = 0x01
AUDIOSOCKET_KIND_SILENCE = 0x02
AUDIOSOCKET_KIND_AUDIO = 0x10
AUDIOSOCKET_KIND_ERROR = 0xFF


class AudioBridge:
    def __init__(self, reader, writer, session_id):
        self.reader = reader
        self.writer = writer
        self.session_id = session_id
        self.ws = None
        self.running = True
        self.upsample_state = None
        self.downsample_state = None

    async def connect_cloud_run(self):
        url = f"{CLOUD_RUN_WS_URL}/{self.session_id}?is_audio=true"
        logger.info(f"Connecting to Cloud Run: {url}")
        self.ws = await websockets.connect(url, ping_interval=20, ping_timeout=10)
        logger.info("Connected to Cloud Run")

    async def read_audiosocket_message(self):
        header = await self.reader.readexactly(3)
        kind, length = struct.unpack('!BH', header)
        data = b''
        if length > 0:
            data = await self.reader.readexactly(length)
        return kind, data

    def write_audiosocket_message(self, kind, data):
        header = struct.pack('!BH', kind, len(data))
        self.writer.write(header + data)

    async def asterisk_to_cloud_run(self):
        try:
            while self.running:
                kind, data = await self.read_audiosocket_message()
                
                if kind == AUDIOSOCKET_KIND_UUID:
                    logger.info("Call started")
                    
                elif kind == AUDIOSOCKET_KIND_AUDIO:
                    if len(data) == 0:
                        continue
                    
                    # Upsample 8kHz -> 16kHz with state preservation
                    audio_16k, self.upsample_state = audioop.ratecv(
                        data, 2, 1, ASTERISK_RATE, GEMINI_INPUT_RATE, self.upsample_state
                    )
                    
                    message = {
                        "mime_type": "audio/pcm",
                        "data": base64.b64encode(audio_16k).decode('ascii'),
                        "role": "user"
                    }
                    await self.ws.send(json.dumps(message))
                    
                elif kind == AUDIOSOCKET_KIND_HANGUP:
                    logger.info("Hangup")
                    self.running = False
                    break
                    
                elif kind == AUDIOSOCKET_KIND_ERROR:
                    self.running = False
                    break
                    
        except asyncio.IncompleteReadError:
            logger.info("Asterisk disconnected")
            self.running = False
        except Exception as e:
            logger.error(f"Error asterisk->cloud: {e}")
            self.running = False

    async def cloud_run_to_asterisk(self):
        try:
            while self.running:
                try:
                    message_json = await asyncio.wait_for(self.ws.recv(), timeout=30.0)
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

                    # Downsample 24kHz -> 8kHz with state preservation
                    audio_8k, self.downsample_state = audioop.ratecv(
                        audio_24k, 2, 1, GEMINI_OUTPUT_RATE, ASTERISK_RATE, self.downsample_state
                    )

                    # Send to Asterisk
                    self.write_audiosocket_message(AUDIOSOCKET_KIND_AUDIO, audio_8k)
                    await self.writer.drain()

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

        except Exception as e:
            logger.error(f"Error cloud->asterisk: {e}")
            self.running = False

    async def run(self):
        try:
            await self.connect_cloud_run()
            await asyncio.gather(
                self.asterisk_to_cloud_run(),
                self.cloud_run_to_asterisk(),
                return_exceptions=True
            )
        finally:
            if self.ws:
                await self.ws.close()
            self.writer.close()
            logger.info("Bridge closed")


async def handle_connection(reader, writer):
    logger.info("New connection")
    session_id = f"phone-{uuid_lib.uuid4().hex[:8]}"
    bridge = AudioBridge(reader, writer, session_id)
    await bridge.run()


async def main():
    server = await asyncio.start_server(handle_connection, '127.0.0.1', 9092)
    logger.info("Bridge listening on 127.0.0.1:9092")
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
```

### Step 3: Create Systemd Service

Create the file `/etc/systemd/system/gemini-bridge.service`:

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

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gemini-bridge
sudo systemctl start gemini-bridge
```

### Step 4: Configure Asterisk Dialplan

Edit `/etc/asterisk/extensions_custom.conf` and add:

```ini
[gemini-live]
; Route calls to Gemini AI via AudioSocket
exten => s,1,NoOp(Starting Gemini Live)
same => n,Answer()
same => n,Wait(0.5)
same => n,AudioSocket(00000000-0000-0000-0000-00000000000${RAND(0,9)},127.0.0.1:9092)
same => n,Hangup()

[from-internal-custom]
exten => 9999,1,NoOp(Dialing Gemini AI)
same => n,Goto(gemini-live,s,1)
```

Reload the dialplan:

```bash
sudo asterisk -rx "dialplan reload"
```

### Step 5: Verify AudioSocket Module is Loaded

```bash
sudo asterisk -rx "module show like audiosocket"
```

If not loaded:

```bash
sudo asterisk -rx "module load res_audiosocket.so"
sudo asterisk -rx "module load app_audiosocket.so"
```

Add to `/etc/asterisk/modules.conf` to load on startup:

```ini
load = res_audiosocket.so
load = app_audiosocket.so
```

---

## Testing

1. Register a SIP softphone to FreePBX (e.g., extension 205)
2. Dial `9999`
3. Speak and wait for Gemini's response
4. Watch the bridge logs: `sudo journalctl -u gemini-bridge -f`

---

## Monitoring & Debugging

### View Bridge Logs

```bash
sudo journalctl -u gemini-bridge -f
```

### Check Bridge Status

```bash
sudo systemctl status gemini-bridge
ss -tlnp | grep 9092
```

### Asterisk CLI Debugging

```bash
sudo asterisk -rvvvv
# Then dial 9999 and watch the output
```

### Verify Dialplan

```bash
sudo asterisk -rx "dialplan show gemini-live"
sudo asterisk -rx "dialplan show 9999@from-internal-custom"
```

---

## Troubleshooting

### Problem: No Audio Playback

**Symptoms:** Call connects but no audio from Gemini

**Solutions:**
1. Check bridge is running: `sudo systemctl status gemini-bridge`
2. Check bridge is listening: `ss -tlnp | grep 9092`
3. Check logs for errors: `sudo journalctl -u gemini-bridge -f`
4. Verify Cloud Run URL is correct in bridge.py
5. Test Cloud Run service directly with a browser client

### Problem: AudioSocket UUID Error

**Symptoms:** `Failed to parse UUID` in Asterisk logs

**Solution:** Ensure the dialplan uses a valid UUID format (8-4-4-4-12 hex characters):
```ini
AudioSocket(00000000-0000-0000-0000-00000000000${RAND(0,9)},127.0.0.1:9092)
```

### Problem: Call Disconnects Immediately

**Symptoms:** Call drops right after answering

**Solutions:**
1. Check AudioSocket modules are loaded:
   ```bash
   sudo asterisk -rx "module show like audiosocket"
   ```
2. Verify dialplan syntax:
   ```bash
   sudo asterisk -rx "dialplan show gemini-live"
   ```
3. Check for syntax errors in extensions_custom.conf

### Problem: 401 Unauthorized / 603 Decline

**Symptoms:** Softphone shows auth errors when calling

**Solutions:**
1. Verify softphone credentials match FreePBX extension
2. Check extension is registered:
   ```bash
   sudo asterisk -rx "pjsip show endpoints"
   ```

### Problem: Choppy/Poor Audio Quality

**Symptoms:** Audio is distorted, rushed, or choppy

**Possible Causes & Solutions:**
1. **Sample rate conversion artifacts** - The `audioop.ratecv` function is basic. Consider using scipy or soxr for better quality.
2. **Network latency** - Check network connectivity between FreePBX and Cloud Run
3. **Buffer issues** - Consider implementing jitter buffering (see Future Improvements)
4. **Upgrade Asterisk** - Version 21.11.0+ includes `chan_websocket` which handles timing automatically

---

## Cloud Run Service Requirements

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
{
  "turn_complete": true
}
```

```json
{
  "interrupted": true
}
```

---

## File Locations Summary

| File | Purpose |
|------|---------|
| `/opt/gemini-bridge/bridge.py` | Main bridge script |
| `/opt/gemini-bridge/venv/` | Python virtual environment |
| `/etc/systemd/system/gemini-bridge.service` | Systemd service file |
| `/etc/asterisk/extensions_custom.conf` | Asterisk dialplan |
| `/etc/asterisk/modules.conf` | Asterisk module loading |

---

## Future Improvements

1. **Upgrade to Asterisk 21.11.0+**
   - Use `chan_websocket` which handles audio timing/framing automatically
   - Eliminates need for AudioSocket and manual sample rate conversion

2. **Better Audio Resampling**
   ```bash
   sudo /opt/gemini-bridge/venv/bin/pip install scipy numpy
   # or
   sudo /opt/gemini-bridge/venv/bin/pip install soxr
   ```

3. **Jitter Buffer Implementation**
   - Buffer incoming audio to smooth out network jitter
   - Implement proper frame pacing for playback

4. **Production Scaling**
   - Run bridge as a separate service (not on PBX server)
   - Add load balancing for multiple concurrent calls
   - Implement call queuing

5. **Security Enhancements**
   - Add SRTP for encrypted SIP audio
   - Use WSS with client certificates
   - Implement rate limiting

---

## References

- [Asterisk AudioSocket Documentation](https://docs.asterisk.org/Configuration/Channel-Drivers/AudioSocket/)
- [Asterisk WebSocket Channel Driver](https://docs.asterisk.org/Configuration/Channel-Drivers/WebSocket/)
- [Gemini Live API Documentation](https://ai.google.dev/api/live)
- [Google ADK (Agent Development Kit)](https://github.com/google/adk-python)
- [FreePBX Documentation](https://wiki.freepbx.org/)

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-23 | 1.0 | Initial documentation |
