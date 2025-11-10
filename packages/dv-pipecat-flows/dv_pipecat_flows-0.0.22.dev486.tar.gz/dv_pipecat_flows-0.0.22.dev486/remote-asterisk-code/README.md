The piepcat bridge server is a python script that runs on the same VM as Asterisk for easiest networking. It connects to the Asterisk and Pipecat and relays the media between them.
The thing is for the outbound, the extension.conf is not used as I think dial plan is set from the codebase here int he pipecat flows only(Check asterisk_ari_client.py and asterisk_service.py)

🎨 Visual Architecture
┌─────────────┐
│  Caller     │ (Phone/SIP Provider)
│ PB_Fintech  │
└──────┬──────┘
       │ SIP/RTP
       ▼
┌──────────────────────────────────────────┐
│           Asterisk Server                │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │   PJSIP Channel                  │   │
│  │   PJSIP/pb_fintech-00000042     │   │
│  └────────────┬─────────────────────┘   │
│               │                          │
│               ▼                          │
│  ┌──────────────────────────────────┐   │
│  │      Mixing Bridge               │   │
│  │      (Conference Room)           │   │
│  │                                  │   │
│  │   [Mix PJSIP + UnicastRTP]      │   │
│  └────────────┬─────────────────────┘   │
│               │                          │
│               ▼                          │
│  ┌──────────────────────────────────┐   │
│  │   UnicastRTP Channel             │   │
│  │   UnicastRTP/...-00000043       │   │
│  │   RTP → 127.0.0.1:45678         │   │
│  └────────────┬─────────────────────┘   │
└───────────────┼──────────────────────────┘
                │ RTP (UDP)
                ▼
┌───────────────────────────────────────────┐
│     pipecat-bridge.py (This Script)       │
│                                           │
│   ┌─────────────┐      ┌──────────────┐  │
│   │  RTPPort    │      │  WebSocket   │  │
│   │  UDP:45678  │◄────►│  Client      │  │
│   └─────────────┘      └──────┬───────┘  │
│         │                     │           │
│         └─────────┬───────────┘           │
│                   │                       │
│              ┌────▼─────┐                 │
│              │Audio     │                 │
│              │Relay     │                 │
│              │Loops     │                 │
│              └──────────┘                 │
└────────────────────┬──────────────────────┘
                     │ WebSocket
                     ▼
┌────────────────────────────────────────────┐
│        Pipecat Server (Your AI)            │
│                                            │
│   /ws/asterisk endpoint                    │
│                                            │
│   ┌──────────────────────────────────┐    │
│   │  WebSocket Handler               │    │
│   │  - Receives caller audio         │    │
│   │  - Processes with AI             │    │
│   │  - Sends AI response audio       │    │
│   └──────────────────────────────────┘    │
└────────────────────────────────────────────┘

-------

Question: Is asterisk and the bridge speaking via ws?
Answer:
Let me clarify this critical distinction - there are actually TWO different WebSocket connections in this system!
🔌 Two WebSocket Connections
WebSocket #1: ARI Events (Asterisk ↔ Bridge)
async def ws_events(self, app: str):
    # WebSocket for Asterisk EVENTS (control/monitoring)
    url = f"ws://{self.host}:{self.port}/ari/events?app={app}&api_key=..."
    return await websockets.connect(url)
What it does:
Asterisk sends events to the bridge about what's happening with calls
This is a control plane connection (not audio!)
One-way: Asterisk → Bridge (mostly)
Example events:
// New call entered Stasis app
{
  "type": "StasisStart",
  "channel": {
    "id": "PJSIP/pb_fintech-00000042",
    "state": "Up",
    "caller": {"number": "919876543210"}
  }
}

// Call ended
{
  "type": "ChannelDestroyed",
  "channel": {
    "id": "PJSIP/pb_fintech-00000042"
  }
}
Purpose: The bridge needs to know when calls start/end so it can create/destroy resources.
WebSocket #2: Pipecat Audio (Bridge ↔ Pipecat AI)
# Connect to Pipecat
ws_url = f"ws://127.0.0.1:8080/ws/asterisk?call_id={call_id}..."
ws = await websockets.connect(ws_url)

# Send audio to Pipecat
await ws.send(json.dumps({
    "event": "media",
    "payload": base64_audio
}))
What it does:
Bridge sends/receives audio to/from your AI
This is the data plane connection
Two-way: Bridge ↔ Pipecat
Example messages:
// Bridge → Pipecat (caller audio)
{
  "event": "media",
  "encoding": "pcmu",
  "sampleRate": 8000,
  "payload": "////+fn5+fkA..."  // base64 audio
}

// Pipecat → Bridge (AI audio response)
{
  "event": "media",
  "payload": "AQIDBAUG..."  // base64 audio
}
Purpose: This is where the actual audio flows for AI processing.
📊 Complete Connection Map
┌──────────────────────────────────────────────────────────────┐
│                     Asterisk Server                          │
│                                                              │
│  Port 5038: ARI HTTP API                                    │
│  Port 8088: ARI WebSocket Events ◄─┐                        │
│                                     │                        │
│  ┌──────────────────────────────┐  │                        │
│  │   PJSIP Channel              │  │                        │
│  │   (Caller's audio)           │  │                        │
│  └──────────┬───────────────────┘  │                        │
│             │                       │                        │
│             ▼                       │                        │
│  ┌──────────────────────────────┐  │                        │
│  │   Mixing Bridge              │  │                        │
│  └──────────┬───────────────────┘  │                        │
│             │                       │                        │
│             ▼                       │                        │
│  ┌──────────────────────────────┐  │                        │
│  │   UnicastRTP Channel         │  │                        │
│  │   RTP → 127.0.0.1:45678     │  │                        │
│  └──────────┬───────────────────┘  │                        │
└─────────────┼────────────────────────┼────────────────────────┘
              │ RTP                    │ WS Events
              │ (UDP Audio)            │ (Control)
              ▼                        ▼
┌───────────────────────────────────────────────────────────────┐
│              pipecat-bridge.py                                │
│                                                               │
│  ┌────────────────────┐        ┌──────────────────────┐     │
│  │  ARI WebSocket     │        │  RTPPort             │     │
│  │  (Events Only)     │        │  UDP:45678           │     │
│  │                    │        │  (Audio Only)        │     │
│  │  - StasisStart     │        │                      │     │
│  │  - ChannelDestroy  │        │  Receives/Sends      │     │
│  │  - Dial events     │        │  RTP packets         │     │
│  └────────────────────┘        └──────────┬───────────┘     │
│                                            │                 │
│                                            ▼                 │
│                         ┌──────────────────────────────┐     │
│                         │  Audio Relay Loops           │     │
│                         │  RTP ↔ WebSocket             │     │
│                         └──────────┬───────────────────┘     │
│                                    │                         │
└────────────────────────────────────┼─────────────────────────┘
                                     │ WS Audio
                                     │ (Data)
                                     ▼
┌───────────────────────────────────────────────────────────────┐
│              Pipecat Server (Your AI)                         │
│                                                               │
│  Port 8080: /ws/asterisk                                     │
│                                                               │
│  ┌──────────────────────────────────────┐                    │
│  │  WebSocket Handler                   │                    │
│  │  - Receives caller audio             │                    │
│  │  - Processes with LLM/TTS            │                    │
│  │  - Sends AI response audio           │                    │
│  └──────────────────────────────────────┘                    │
└───────────────────────────────────────────────────────────────┘
🔍 Detailed Breakdown
Connection 1: ARI Events WebSocket
URL:
ws://localhost:8088/ari/events?app=pipecat&api_key=asterisk:asterisk
Who connects: Bridge → Asterisk When: Once at startup, stays open for all calls What flows:
Asterisk → Bridge (Events):
  - "New call arrived!" (StasisStart)
  - "Call ended!" (ChannelDestroyed)
  - "Channel state changed!" (ChannelStateChange)
  - "Dial attempt!" (Dial)
Code:
# In run_events()
ws = await ari.ws_events(ASTERISK_ARI_APP)  # Connect to Asterisk

async for raw in ws:  # Listen for events
    ev = json.loads(raw)
    
    if ev["type"] == "StasisStart":
        ch_id = ev["channel"]["id"]
        # Create bridge, RTP, connect to Pipecat...
        asyncio.create_task(start_for_channel(ari, ch_id))
Important: This is NOT audio! It's just notifications about call lifecycle.
Connection 2: Pipecat Audio WebSocket
URL:
ws://localhost:8080/ws/asterisk?call_id=pbf_call_12345&sip_provider=pb_fintech&...
Who connects: Bridge → Pipecat When: Created for each call (one per call) What flows:
Bridge → Pipecat (Audio):
  {"event": "media", "payload": "<caller audio>"}

Pipecat → Bridge (Audio):
  {"event": "media", "payload": "<AI audio>"}

Bridge → Pipecat (Control):
  {"event": "start", "callId": "..."}
  {"event": "hangup"}
Code:
# In start_for_channel()
ws_url = f"{PIPECAT_WS_URL_LOCAL}?call_id={call_id}&..."
ws = await websockets.connect(ws_url)  # Connect to Pipecat

# Send start event
await ws.send(json.dumps({"event": "start", ...}))

# Audio relay loop
while True:
    # Receive RTP from Asterisk
    payload = await sess.rtp.recv_payload()
    
    # Send to Pipecat via WebSocket
    await ws.send(json.dumps({
        "event": "media",
        "payload": base64.b64encode(payload).decode()
    }))
🎭 Three Communication Protocols in Use
┌─────────────┬──────────────────┬─────────────────────────┐
│ Protocol    │ Connection       │ Purpose                 │
├─────────────┼──────────────────┼─────────────────────────┤
│ HTTP        │ Bridge → Asterisk│ Control commands        │
│ (ARI REST)  │ Port 8088        │ (create bridge, hangup) │
├─────────────┼──────────────────┼─────────────────────────┤
│ WebSocket   │ Asterisk → Bridge│ Call lifecycle events   │
│ (ARI Events)│ Port 8088        │ (start, end, state)     │
├─────────────┼──────────────────┼─────────────────────────┤
│ RTP         │ Asterisk ↔ Bridge│ Audio packets           │
│ (UDP)       │ Dynamic ports    │ (caller voice data)     │
├─────────────┼──────────────────┼─────────────────────────┤
│ WebSocket   │ Bridge ↔ Pipecat │ Audio + control         │
│ (Audio)     │ Port 8080        │ (AI processing)         │
└─────────────┴──────────────────┴─────────────────────────┘
🕐 Timeline: What Happens When
T=0: Bridge starts
  ├─> Opens HTTP connection to Asterisk ARI
  ├─> Opens WebSocket to Asterisk for events
  └─> Listens for StasisStart events

T=1: Call arrives at Asterisk
  ├─> Asterisk creates PJSIP channel
  ├─> Dialplan: Stasis(pipecat)
  └─> Asterisk sends StasisStart event via WS #1

T=2: Bridge receives StasisStart event
  ├─> Creates audio bridge (via HTTP)
  ├─> Creates RTP port (UDP socket)
  ├─> Creates external media channel (via HTTP)
  ├─> Opens WebSocket to Pipecat (WS #2)
  └─> Starts audio relay loops

T=3-300: Active call
  ├─> RTP packets: Asterisk ↔ Bridge (UDP)
  └─> Audio messages: Bridge ↔ Pipecat (WS #2)

T=301: Call ends
  ├─> Asterisk sends ChannelDestroyed via WS #1
  ├─> Bridge sends hangup to Pipecat via WS #2
  ├─> Closes WS #2
  ├─> Deletes bridge/channels via HTTP
  └─> Cleans up RTP socket
❓ Why Not RTP Directly Between Asterisk and Pipecat?
You might ask: Why use a bridge at all? Why not:
Asterisk (RTP) ──────────> Pipecat (RTP) ?
Answer:
Protocol mismatch - Pipecat speaks WebSocket, not RTP
Flexibility - WebSocket is easier to work with in Python/Node.js
NAT/Firewall - WebSocket (HTTP/HTTPS) is easier to tunnel
Features - WebSocket allows JSON metadata alongside audio
Portability - Can run Pipecat anywhere (cloud, localhost, etc.)
💡 Key Takeaway
The bridge has TWO jobs:
Monitor Asterisk (via ARI WebSocket) - "Tell me when calls start/end"
Relay Audio (via RTP ↔ Pipecat WebSocket) - "Move audio between phone and AI"
         ARI WebSocket (Control)
Asterisk ────────────────────────> Bridge
                                     │
                                     │ Audio WS
                                     │ (Data)
                                     ▼
                                  Pipecat
The ARI WebSocket is like a notification system - it tells the bridge "something happened!", and then the bridge takes action (like creating an audio connection to Pipecat). 