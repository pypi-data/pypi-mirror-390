"""
Asterisk <-> Pipecat bridge compatible with your asterisk_ws_serializer.py and /ws/asterisk.

Flow:
- Connect to ARI events (WebSocket) for app ASTERISK_ARI_APP.
- When a channel for that app becomes 'Up':
  - Create a mixing bridge.
  - Create an externalMedia channel toward a local UDP RTP port (on this machine).
  - Add both channels to the mixing bridge.
  - Open a WebSocket to your Pipecat /ws/asterisk?call_id=...&encoding=...&tenant=...
  - Send {"event":"start"} as the first WS message.
  - Relay media both ways:
      RTP -> WS {"event":"media","encoding":pcmu|pcm16,"sampleRate":...,"payload":b64}
      WS  -> RTP (build RTP packets; μ-law payload type 0 or PCM16 dynamic PT 96)
- Hangup:
  - If WS sends {"event":"hangup"} or the WS closes: DELETE /ari/channels/{tel_channel}
  - If the tel channel is destroyed: close WS and cleanup.

Run on the same VM as Asterisk for easiest networking. If you Dockerize: use --network host.
"""

import os
import json
import time
import base64
import socket
import struct
import asyncio
from typing import Dict, Optional
from urllib.parse import quote

import aiohttp
import websockets
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()


# ------------------ Config reloading ------------------
class Config:
    """Configuration class that can be reloaded from environment variables."""

    def __init__(self):
        self.reload()

    def reload(self):
        """Reload all configuration from environment variables."""
        # Reload .env file
        load_dotenv(override=True)

        # Update configuration variables
        self.ASTERISK_HTTP = os.getenv("ASTERISK_HTTP", "http://127.0.0.1:8088")
        self.ASTERISK_ARI_USER = os.getenv("ASTERISK_ARI_USER", "pipecat")
        self.ASTERISK_ARI_PASS = os.getenv("ASTERISK_ARI_PASS", "asdf!@#$")
        self.ASTERISK_ARI_APP = os.getenv("ASTERISK_ARI_APP", "pipecat")

        # Pipecat WS endpoint. This is YOUR server's route:
        #   @router.websocket("/ws/asterisk")
        self.PIPECAT_WS_URL = os.getenv("PIPECAT_WS_URL", "ws://127.0.0.1:8080/ws/asterisk")
        # Alternative endpoint for Ubona calls
        self.PIPECAT_WS_URL_LOCAL = os.getenv(
            "PIPECAT_WS_URL_LOCAL", "ws://127.0.0.1:8080/ws/ubona"
        )

        # The IP Asterisk should send RTP to. On the same VM: 127.0.0.1 is fine.
        self.BRIDGE_HOST = os.getenv("BRIDGE_HOST", "127.0.0.1")

        # Defaults if channel variables are absent
        self.DEFAULT_ENCODING = os.getenv("DEFAULT_ENCODING", "pcmu")  # "pcmu", "pcma" or "pcm16"
        self.DEFAULT_SR = int(os.getenv("DEFAULT_SR", "8000"))  # 8000 or 16000

        # Performance and debug settings
        self.DEBUG_MODE = int(os.getenv("DEBUG_MODE", "0"))  # 0=production, 1=debug
        self.AUDIO_DUMP = int(os.getenv("AUDIO_DUMP", "0"))  # 0=disabled, 1=enabled
        self.METRICS_INTERVAL = int(os.getenv("METRICS_INTERVAL", "1"))  # seconds

        if self.DEBUG_MODE:
            print(f"[config] Configuration reloaded at {time.strftime('%Y-%m-%d %H:%M:%S')}")


# Global configuration instance
config = Config()

# For backward compatibility, keep global variables
ASTERISK_HTTP = config.ASTERISK_HTTP
ASTERISK_ARI_USER = config.ASTERISK_ARI_USER
ASTERISK_ARI_PASS = config.ASTERISK_ARI_PASS
ASTERISK_ARI_APP = config.ASTERISK_ARI_APP
PIPECAT_WS_URL = config.PIPECAT_WS_URL
PIPECAT_WS_URL_LOCAL = config.PIPECAT_WS_URL_LOCAL
BRIDGE_HOST = config.BRIDGE_HOST
DEFAULT_ENCODING = config.DEFAULT_ENCODING
DEFAULT_SR = config.DEFAULT_SR
DEBUG_MODE = config.DEBUG_MODE
AUDIO_DUMP = config.AUDIO_DUMP
METRICS_INTERVAL = config.METRICS_INTERVAL


async def config_reloader():
    """Background task to reload configuration every minute."""
    global ASTERISK_HTTP, ASTERISK_ARI_USER, ASTERISK_ARI_PASS, ASTERISK_ARI_APP
    global PIPECAT_WS_URL, PIPECAT_WS_URL_LOCAL, BRIDGE_HOST, DEFAULT_ENCODING, DEFAULT_SR
    global DEBUG_MODE, AUDIO_DUMP, METRICS_INTERVAL

    while True:
        try:
            await asyncio.sleep(60)  # Wait 1 minute
            config.reload()

            # Update global variables
            ASTERISK_HTTP = config.ASTERISK_HTTP
            ASTERISK_ARI_USER = config.ASTERISK_ARI_USER
            ASTERISK_ARI_PASS = config.ASTERISK_ARI_PASS
            ASTERISK_ARI_APP = config.ASTERISK_ARI_APP
            PIPECAT_WS_URL = config.PIPECAT_WS_URL
            PIPECAT_WS_URL_LOCAL = config.PIPECAT_WS_URL_LOCAL
            BRIDGE_HOST = config.BRIDGE_HOST
            DEFAULT_ENCODING = config.DEFAULT_ENCODING
            DEFAULT_SR = config.DEFAULT_SR
            DEBUG_MODE = config.DEBUG_MODE
            AUDIO_DUMP = config.AUDIO_DUMP
            METRICS_INTERVAL = config.METRICS_INTERVAL

        except Exception as e:
            print(f"[config] Error reloading configuration: {e}")


# ------------------ Tiny μ-law and A-law helpers ------------------
def mulaw_decode(ulaw_bytes: bytes) -> bytes:
    """μ-law -> PCM16LE (not used by this bridge; here for completeness)."""
    pcm = bytearray()
    for u in ulaw_bytes:
        u = ~u & 0xFF
        t = ((u & 0x0F) << 3) + 0x84
        t <<= (u & 0x70) >> 4
        t -= 0x84
        if u & 0x80:
            t = -t
        pcm += struct.pack("<h", t)
    return bytes(pcm)


def mulaw_encode(pcm16le: bytes) -> bytes:
    """PCM16LE -> μ-law (not used by this bridge; your Pipecat serializer already sends μ-law)."""
    out = bytearray()
    for i in range(0, len(pcm16le), 2):
        s = struct.unpack_from("<h", pcm16le, i)[0]
        sign = 0x80 if s < 0 else 0
        if s < 0:
            s = -s
        s += 0x84
        if s > 0x7FFF:
            s = 0x7FFF
        seg = 7
        for j in range(7):
            if s <= (0x1F << (j + 3)):
                seg = j
                break
        mant = (s >> (seg + 3)) & 0x0F
        u = ~(sign | (seg << 4) | mant) & 0xFF
        out.append(u)
    return bytes(out)


def alaw_decode(alaw_bytes: bytes) -> bytes:
    """A-law -> PCM16LE (not used by this bridge; here for completeness)."""
    pcm = bytearray()
    for a in alaw_bytes:
        a = a ^ 0x55  # Invert even bits
        sign = 1 if a & 0x80 else -1
        seg = (a & 0x70) >> 4
        mant = a & 0x0F
        if seg == 0:
            t = (mant << 4) + 8
        elif seg == 1:
            t = (mant << 5) + 0x108
        else:
            t = (mant + 16) << (seg + 3)
        pcm += struct.pack("<h", sign * t)
    return bytes(pcm)


def alaw_encode(pcm16le: bytes) -> bytes:
    """PCM16LE -> A-law (not used by this bridge; your Pipecat serializer already sends A-law)."""
    out = bytearray()
    for i in range(0, len(pcm16le), 2):
        s = struct.unpack_from("<h", pcm16le, i)[0]
        sign = 0x80 if s < 0 else 0
        if s < 0:
            s = -s
        if s >= 0x1000:
            seg = 7
            mant = 0x0F
        else:
            seg = 7
            for j in range(7):
                if s < (1 << (j + 8)):
                    seg = j
                    break
            if seg < 2:
                mant = (s >> 1) & 0x0F
            else:
                mant = (s >> (seg + 3)) & 0x0F
        a = sign | (seg << 4) | mant
        out.append(a ^ 0x55)  # Invert even bits
    return bytes(out)


# ------------------ RTP ------------------
class RTPPort:
    """
    Minimal RTP port that:
      - binds UDP on an ephemeral port
      - learns Asterisk's RTP target (ip,port) from the first incoming packet
      - can send RTP with a basic header (no extensions)
    """

    def __init__(self, payload_type: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 0))
        self.sock.setblocking(False)
        self.peer = None  # (ip, port) learned from incoming RTP
        self.pt = payload_type
        self.seq = 0
        self.ts = 0
        self.ssrc = int(time.time()) & 0xFFFFFFFF

    @property
    def local_port(self) -> int:
        return self.sock.getsockname()[1]

    async def recv_payload(self) -> Optional[bytes]:
        try:
            data, addr = await asyncio.get_event_loop().sock_recvfrom(self.sock, 4096)
        except BlockingIOError:
            return None
        # learn peer for outbound
        if self.peer is None:
            self.peer = addr
        if len(data) < 12:
            return None
        # ignore header parsing beyond fixed 12B for simplicity
        return data[12:]

    async def send_payload(self, payload: bytes, sample_count: int):
        if not self.peer:
            return
        self.seq = (self.seq + 1) & 0xFFFF
        self.ts = (self.ts + sample_count) & 0xFFFFFFFF
        # V=2,P=0,X=0,CC=0,M=0, PT=self.pt
        header = struct.pack("!BBHII", 0x80, self.pt, self.seq, self.ts, self.ssrc)
        packet = header + payload
        await asyncio.get_event_loop().sock_sendto(self.sock, packet, self.peer)


# ------------------ ARI Client ------------------
class ARI:
    def __init__(self, base: str, user: str, pw: str):
        self.base = base.rstrip("/")
        self.auth = aiohttp.BasicAuth(user, pw)
        self.http = aiohttp.ClientSession(auth=self.auth)

    async def get(self, path: str, **params):
        async with self.http.get(self.base + path, params=params) as r:
            r.raise_for_status()
            return await r.json()

    async def post(self, path: str, **params):
        async with self.http.post(self.base + path, params=params) as r:
            r.raise_for_status()
            if r.content_type == "application/json":
                return await r.json()
            return await r.text()

    async def delete(self, path: str, **params):
        async with self.http.delete(self.base + path, params=params) as r:
            r.raise_for_status()
            return await r.text()

    async def ws_events(self, app: str):
        encoded_user = quote(ASTERISK_ARI_USER, safe="")
        encoded_pass = quote(ASTERISK_ARI_PASS, safe="")
        url = f"{self.base.replace('http', 'ws')}/ari/events?app={app}&api_key={encoded_user}:{encoded_pass}"
        return await websockets.connect(url)


# ------------------ Session ------------------
class CallSession:
    def __init__(self, chan_id: str, call_id: str, tenant: str, encoding: str, sample_rate: int):
        self.chan_id = chan_id  # Asterisk channel (PJSIP/… or the Local uuid)
        self.call_id = call_id  # Your Pipecat call_id (X_CALL_ID if provided)
        self.tenant = tenant
        self.encoding = encoding  # "pcmu" or "pcm16"
        self.sr = sample_rate  # 8000 or 16000
        self.bridge_id: Optional[str] = None
        self.ext_chan_id: Optional[str] = None
        self.ws = None  # WebSocket to Pipecat
        self.rtp = None  # RTPPort
        self.callback_url: Optional[str] = None  # Callback URL for status updates


sessions: Dict[str, CallSession] = {}  # key: tel channel id
processing_channels = set()  # Track channels being processed to prevent duplicates
pending_ext: Dict[str, Dict[str, str]] = {}  # ext_id -> {"bridge_id":..., "tel_id":...}
dial_callback_urls: Dict[str, str] = {}  # ch_id -> callback_url


# ------------------ Performance Metrics ------------------
class Metrics:
    def __init__(self):
        self.rtp_packets_rx = 0
        self.rtp_packets_tx = 0
        self.rtp_bytes_rx = 0
        self.rtp_bytes_tx = 0
        self.ws_messages_rx = 0
        self.ws_messages_tx = 0
        self.last_report_time = time.time()

    def report_rtp_rx(self, bytes_count: int):
        self.rtp_packets_rx += 1
        self.rtp_bytes_rx += bytes_count

    def report_rtp_tx(self, bytes_count: int):
        self.rtp_packets_tx += 1
        self.rtp_bytes_tx += bytes_count

    def report_ws_rx(self):
        self.ws_messages_rx += 1

    def report_ws_tx(self):
        self.ws_messages_tx += 1

    def maybe_log_stats(self):
        if METRICS_INTERVAL <= 0:
            return

        now = time.time()
        if now - self.last_report_time >= METRICS_INTERVAL:
            elapsed = now - self.last_report_time
            rtp_rx_rate = self.rtp_packets_rx / elapsed
            rtp_tx_rate = self.rtp_packets_tx / elapsed
            ws_rx_rate = self.ws_messages_rx / elapsed
            ws_tx_rate = self.ws_messages_tx / elapsed

            print(
                f"[metrics] RTP: {rtp_rx_rate:.1f}rx/s ({self.rtp_bytes_rx / elapsed / 1024:.1f}KB/s), "
                f"{rtp_tx_rate:.1f}tx/s ({self.rtp_bytes_tx / elapsed / 1024:.1f}KB/s) | "
                f"WS: {ws_rx_rate:.1f}rx/s, {ws_tx_rate:.1f}tx/s | Sessions: {len(sessions)}"
            )

            # Reset counters
            self.rtp_packets_rx = 0
            self.rtp_packets_tx = 0
            self.rtp_bytes_rx = 0
            self.rtp_bytes_tx = 0
            self.ws_messages_rx = 0
            self.ws_messages_tx = 0
            self.last_report_time = now


metrics = Metrics()


# ------------------ Helpers ------------------
def ulaw_silence_frame(samples: int = 160) -> bytes:
    """Generate μ-law silence frame. 20ms @ 8kHz = 160 samples; μ-law silence byte is 0xFF"""
    return b"\xff" * samples


async def get_var(ari: ARI, channel_id: str, name: str) -> Optional[str]:
    try:
        v = await ari.get(f"/ari/channels/{channel_id}/variable", variable=name)
        return v.get("value")
    except Exception:
        return None


def pick_format(encoding: str, sr: int) -> str:
    """
    Asterisk externalMedia 'format' must be one of Asterisk formats:
      - "ulaw" for μ-law (8k)
      - "alaw" for A-law (8k)
      - "slin" for 8k PCM16
      - "slin16" for 16k PCM16
    """
    if encoding == "pcmu":
        return "ulaw"
    if encoding == "pcma":
        return "alaw"
    if sr == 16000:
        return "slin16"
    return "slin"


def rtp_pt_for(encoding: str) -> int:
    if encoding == "pcmu":
        return 0  # PCMU
    elif encoding == "pcma":
        return 8  # PCMA
    else:
        return 96  # PCM16 (dynamic)


def samples_in_payload(encoding: str, payload: bytes) -> int:
    if encoding in ("pcmu", "pcma"):
        return len(payload)  # 1 byte per sample for both μ-law and A-law
    else:
        return len(payload) // 2  # 2 bytes per sample (L16)


def get_call_status(cause_code: int) -> str:
    """Convert Q.931 cause code to call status for retry logic."""
    if cause_code == 16:
        return "completed"  # Normal clearing - call was successful
    elif cause_code in [17, 19]:
        return "no-answer"  # Busy/No answer - temporary conditions
    else:
        return "error"  # Unknown/other causes - conservative approach


# ------------------ Media relay ------------------
async def media_loop(sess: CallSession, ari: ARI):
    assert sess.ws and sess.rtp

    async def rtp_to_ws():
        # Receive RTP from Asterisk, forward to Pipecat as "media"
        if DEBUG_MODE:
            print("[bridge-debug] Starting rtp_to_ws loop...")

        # Audio file setup (only if enabled)
        f_in = None
        if AUDIO_DUMP:
            import time

            timestamp = int(time.time())
            incoming_file = f"/tmp/audio_incoming_{sess.call_id}_{timestamp}.raw"
            f_in = open(incoming_file, "wb")
            if DEBUG_MODE:
                print(f"[bridge-debug] Saving incoming audio to {incoming_file}")

        try:
            while True:
                payload = await sess.rtp.recv_payload()
                if payload is None:
                    await asyncio.sleep(0.001)
                    continue

                # Report metrics
                metrics.report_rtp_rx(len(payload))
                metrics.maybe_log_stats()

                if DEBUG_MODE:
                    print(f"[bridge-debug] >> Received {len(payload)} bytes of RTP from Asterisk")

                # Save raw audio data (only if enabled)
                if f_in:
                    f_in.write(payload)
                    f_in.flush()

                msg = {
                    "event": "media",
                    "encoding": sess.encoding,
                    "sampleRate": sess.sr,
                    "payload": base64.b64encode(payload).decode("utf-8"),
                }
                await sess.ws.send(json.dumps(msg))
                metrics.report_ws_tx()
        except Exception as e:
            if DEBUG_MODE:
                print(f"[bridge-debug] Error in rtp_to_ws: {e}")
        finally:
            if f_in:
                f_in.close()
            if DEBUG_MODE:
                print(f"[bridge-debug] Stopped RTP to WS loop")

    async def ws_to_rtp():
        # Receive "media" from Pipecat, forward as RTP to Asterisk
        if DEBUG_MODE:
            print("[bridge-debug] Starting ws_to_rtp loop...")

        # Audio file setup (only if enabled)
        f_out = None
        if AUDIO_DUMP:
            import time

            timestamp = int(time.time())
            outgoing_file = f"/tmp/audio_outgoing_{sess.call_id}_{timestamp}.raw"
            f_out = open(outgoing_file, "wb")
            if DEBUG_MODE:
                print(f"[bridge-debug] Saving outgoing audio to {outgoing_file}")

        try:
            async for text in sess.ws:
                try:
                    msg = json.loads(text)
                except Exception:
                    continue

                metrics.report_ws_rx()
                ev = msg.get("event")

                if ev == "media":
                    if DEBUG_MODE:
                        print(f"[bridge-debug] << Received media event from Pipecat")

                    enc = msg.get("encoding", sess.encoding)
                    sr = int(msg.get("sampleRate", sess.sr))
                    if enc != sess.encoding or sr != sess.sr:
                        # keep it simple: ignore renegotiations; you can add support if needed
                        pass
                    raw = base64.b64decode(msg.get("payload", ""))
                    if not raw:
                        continue

                    # Save raw audio data (only if enabled)
                    if f_out:
                        f_out.write(raw)
                        f_out.flush()

                    sc = samples_in_payload(sess.encoding, raw)
                    if DEBUG_MODE:
                        print(
                            f"[bridge-debug] >> Sending {len(raw)} bytes of RTP to Asterisk at {sess.rtp.peer}"
                        )

                    await sess.rtp.send_payload(raw, sc)
                    metrics.report_rtp_tx(len(raw))

                elif ev == "hangup":
                    # Pipecat requested to end the call
                    await ari.delete(f"/ari/channels/{sess.chan_id}")
                    break
        except Exception as e:
            if DEBUG_MODE:
                print(f"[bridge-debug] Error in ws_to_rtp: {e}")
        finally:
            if f_out:
                f_out.close()
            if DEBUG_MODE:
                print(f"[bridge-debug] Stopped WS to RTP loop")

            # you can support {"event":"clear"} from your serializer if you want

    await asyncio.gather(rtp_to_ws(), ws_to_rtp())


# ------------------ Start on Answer ------------------
async def start_for_channel(
    ari: ARI, ch_id: str, app_args: list = None, call_id_from_app_data: str = None
):
    """
    Build the bridge & extMedia, then WS to Pipecat, then relay.
    Reads X_TENANT, X_CODEC, X_SR, X_CALL_ID if set by your originate.
    """
    print(f"[bridge] start_for_channel: {ch_id}")

    # Wait for channel to be Up before proceeding
    for _ in range(30):  # Wait up to 3 seconds
        try:
            ch_info = await ari.get(f"/ari/channels/{ch_id}")
            if ch_info.get("state") == "Up":
                break
            await asyncio.sleep(0.1)
        except:
            await asyncio.sleep(0.1)
    else:
        print(f"[bridge] Channel {ch_id} never went Up, abandoning")
        return

    # Try to get each variable individually
    tenant = await get_var(ari, ch_id, "X_TENANT")
    encoding = await get_var(ari, ch_id, "X_CODEC")
    sr_str = await get_var(ari, ch_id, "X_SR")
    call_id = await get_var(ari, ch_id, "X_CALL_ID")

    # Check if we already have callback URL from dial event
    callback_url = dial_callback_urls.pop(ch_id, None)
    if not callback_url:
        callback_url = await get_var(ari, ch_id, "X_CALLBACK_URL")

    # Check for generic inbound call variables
    inbound_provider = await get_var(ari, ch_id, "INBOUND_PROVIDER")
    inbound_did = await get_var(ari, ch_id, "INBOUND_DID")
    inbound_from = await get_var(ari, ch_id, "INBOUND_FROM")
    sip_context = await get_var(ari, ch_id, "SIP_CONTEXT")
    agent_id = await get_var(ari, ch_id, "AGENT_ID")
    custom_call_id = await get_var(ari, ch_id, "CUSTOM_CALL_ID")
    custom_vars = await get_var(ari, ch_id, "CUSTOM_VARS")

    # Check for call transfer configuration
    transfer_type = await get_var(ari, ch_id, "TRANSFER_TYPE")
    transfer_sip_domain = await get_var(ari, ch_id, "TRANSFER_SIP_DOMAIN")

    # Native SIP Call-ID (helps correlate logs with SIP provider)
    sip_call_id = await get_var(ari, ch_id, "CHANNEL(callid)")
    if not sip_call_id:
        sip_call_id = await get_var(ari, ch_id, "PJSIP_HEADER(read,Call-ID)")

    # Try to get call_id from different sources with priority:
    # 1. Custom call_id from X-Call-ID header (PB_Fintech)
    # 2. X_CALL_ID variable (outbound calls)
    # 3. app_data
    # 4. app_args
    # 5. Generate UUID (fallback)
    if custom_call_id:
        call_id = custom_call_id
        print(f"[bridge] Using custom call_id from X-Call-ID header: {call_id}")
    elif not call_id and call_id_from_app_data:
        call_id = call_id_from_app_data
        print(f"[bridge] Using call_id from app_data: {call_id}")
    elif not call_id and app_args and len(app_args) > 0:
        call_id = app_args[0]  # First app_arg should be call_id
        print(f"[bridge] Using call_id from app_args: {call_id}")

    # Generate UUID if no call_id found
    if not call_id:
        import uuid

        call_id = str(uuid.uuid4())
        print(f"[bridge] Generated UUID for call_id: {call_id}")

    # Use defaults if not found
    tenant = tenant or "default"
    encoding = encoding or DEFAULT_ENCODING
    sr_str = sr_str or str(DEFAULT_SR)

    print(
        f"[bridge] Channel config for {ch_id}: "
        f"tenant:{tenant}, encoding:{encoding}, sr:{sr_str}, call_id:{call_id}, "
        f"callback_url:{callback_url}, "
        f"inbound_provider:{inbound_provider}, inbound_did:{inbound_did}, inbound_from:{inbound_from}, sip_context:{sip_context}, agent_id:{agent_id}, custom_vars:{custom_vars}"
    )

    try:
        sr = int(sr_str)
    except ValueError:
        sr = DEFAULT_SR

    # Create mixing bridge
    b = await ari.post("/ari/bridges", type="mixing")
    bridge_id = b["id"]

    # Put tel channel into the bridge
    await ari.post(f"/ari/bridges/{bridge_id}/addChannel", channel=ch_id)

    # Create local RTP port, tell Asterisk to send there
    rtp = RTPPort(payload_type=rtp_pt_for(encoding))
    external_host = f"{BRIDGE_HOST}:{rtp.local_port}"
    fmt = pick_format(encoding, sr)

    print(f"[bridge] Creating externalMedia with external_host={external_host}, format={fmt}")
    em = await ari.post(
        "/ari/channels/externalMedia",
        app=ASTERISK_ARI_APP,  # Use main app instead of non-existent media app
        appArgs=call_id,  # Pass call_id as appArgs (must be string, not array)
        originator=ch_id,  # Link to originating PJSIP channel
        external_host=external_host,
        format=fmt,
        direction="both",
    )
    ext_chan_id = (em.get("channel") or {}).get("id") or em.get("id")
    print(f"[bridge] Created externalMedia channel: {ext_chan_id}")

    # Create session early so both immediate and StasisStart paths can find it
    sess = CallSession(ch_id, call_id, tenant, encoding, sr)
    sess.bridge_id = bridge_id
    sess.ext_chan_id = ext_chan_id
    sess.rtp = rtp
    sess.callback_url = callback_url  # Store callback URL in session
    sessions[ch_id] = sess

    # Fix race condition: Try to add ext channel to bridge immediately with retry
    added = False
    for attempt in range(20):  # ~1s
        try:
            await ari.post(f"/ari/bridges/{bridge_id}/addChannel", channel=ext_chan_id)
            print(
                f"[bridge] Added external media {ext_chan_id} to bridge {bridge_id} (immediate, attempt {attempt + 1})"
            )
            added = True
            break
        except Exception as e:
            if DEBUG_MODE:
                print(f"[bridge-debug] Bridge add attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(0.05)

    if not added:
        # Fallback: store in pending dict for StasisStart event handling
        pending_ext[ext_chan_id] = {"bridge_id": bridge_id, "tel_id": ch_id}
        print(f"[bridge] External media {ext_chan_id} pending; will add on StasisStart")

    # Discover RTP peer immediately and prime symmetric RTP
    if DEBUG_MODE:
        print(f"[bridge-debug] Discovering RTP peer for ext channel {ext_chan_id}")
    for attempt in range(20):  # ~1s
        addr = (await get_var(ari, ext_chan_id, "UNICASTRTP_LOCAL_ADDRESS")) or (
            await get_var(ari, ext_chan_id, "UNICAST_RTP_LOCAL_ADDRESS")
        )
        port = (
            (await get_var(ari, ext_chan_id, "UNICASTRTP_LOCAL_PORT"))
            or (await get_var(ari, ext_chan_id, "UNICASTRTP_RTP_LOCAL_PORT"))
            or (await get_var(ari, ext_chan_id, "UNICAST_RTP_LOCAL_PORT"))
        )

        if DEBUG_MODE:
            print(f"[bridge-debug] RTP discovery attempt {attempt + 1}: addr={addr}, port={port}")

        if addr and port:
            try:
                sess.rtp.peer = (addr, int(port))
                print(
                    f"[bridge] RTP peer set to {sess.rtp.peer} for tel {ch_id} / ext {ext_chan_id}"
                )
                # Prime symmetric RTP with silence frames (20ms @ 8kHz = 160 samples)
                for _ in range(6):  # ~120ms
                    await sess.rtp.send_payload(ulaw_silence_frame(160), 160)
                    await asyncio.sleep(0.02)
                if DEBUG_MODE:
                    print(f"[bridge-debug] Sent 6 silence frames to prime RTP")
                break
            except Exception as e:
                if DEBUG_MODE:
                    print(f"[bridge-debug] Failed to set RTP peer: {e}")
        await asyncio.sleep(0.05)

    if not sess.rtp.peer:
        if DEBUG_MODE:
            print(f"[bridge-debug] WARNING: Could not discover RTP peer for {ext_chan_id}")

    # Connect to your Pipecat WS - use generic approach for all inbound calls
    qs = f"call_id={call_id}&encoding={encoding}&tenant={tenant}"

    # Check if this is an inbound call from SIP provider
    if inbound_provider:
        # Add generic inbound parameters to query string
        qs += f"&sip_provider={inbound_provider}"
        if inbound_did:
            qs += f"&to_number={inbound_did}"
        if inbound_from:
            qs += f"&from_number={inbound_from}"
        if sip_context:
            qs += f"&sip_context={sip_context}"
        if agent_id:
            qs += f"&agent_id={agent_id}"
        if transfer_type:
            qs += f"&transfer_type={transfer_type}"
        if transfer_sip_domain:
            qs += f"&transfer_sip_domain={transfer_sip_domain}"
        ws_url = f"{PIPECAT_WS_URL_LOCAL}?{qs}"
        print(f"[bridge] Connecting to inbound WebSocket for {inbound_provider}: {ws_url}")
    else:
        ws_url = f"{PIPECAT_WS_URL}?{qs}"
        print(f"[bridge] Connecting to WebSocket: {ws_url}")
    try:
        ws = await websockets.connect(
            ws_url,
            max_queue=1024,  # Increase from default 32 to reduce drops
            write_limit=2**20,  # 1MB write buffer
            compression=None,  # Audio won't compress well; saves CPU
        )
        print(f"[bridge] WebSocket connected successfully")
    except Exception as e:
        print(f"[bridge] WebSocket connection failed: {e}")
        print(f"[bridge] Hanging up call {ch_id} due to WebSocket failure")
        try:
            await ari.delete(f"/ari/channels/{ch_id}")
        except:
            pass
        return

    # Send the required initial 'start' message (your WS expects this)
    start_msg = {
        "event": "start",
        "callId": call_id,
        "call_id": call_id,
        "tenant": tenant,
        "encoding": encoding,
        "sampleRate": sr,
        "channel_id": ch_id,
        "sip_call_id": sip_call_id,
    }

    channel_vars = {
        "X_TENANT": tenant,
        "X_CODEC": encoding,
        "X_SR": sr_str,
        "X_CALL_ID": call_id,
        "INBOUND_PROVIDER": inbound_provider,
        "INBOUND_DID": inbound_did,
        "INBOUND_FROM": inbound_from,
        "SIP_CONTEXT": sip_context,
        "AGENT_ID": agent_id,
        "TRANSFER_TYPE": transfer_type,
        "TRANSFER_SIP_DOMAIN": transfer_sip_domain,
        "CHANNEL(callid)": sip_call_id,
    }
    filtered_vars = {k: v for k, v in channel_vars.items() if v is not None}
    if filtered_vars:
        start_msg["variables"] = filtered_vars

    if app_args:
        start_msg["app_args"] = app_args

    # Add custom_vars if present (for PB_Fintech)
    if custom_vars:
        # Parse custom_vars from format: key1=val1&key2=val2
        custom_vars_dict = {}
        for pair in custom_vars.split("&"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                custom_vars_dict[key] = value
        start_msg["custom_vars"] = custom_vars_dict
        print(f"[bridge] Added custom_vars to start message: {custom_vars_dict}")

    print(f"[bridge] Sending start message: {start_msg}")
    await ws.send(json.dumps(start_msg))

    # Set WebSocket on existing session
    sess.ws = ws

    try:
        await media_loop(sess, ari)
    except websockets.exceptions.ConnectionClosed:
        print(f"[bridge] WebSocket closed by pipecat for {ch_id}, hanging up call")
        try:
            await ari.delete(f"/ari/channels/{ch_id}")
        except:
            pass
    except Exception as e:
        print(f"[bridge] Media loop error for {ch_id}: {e}")
        try:
            await ari.delete(f"/ari/channels/{ch_id}")
        except:
            pass
    finally:
        # Cleanup
        try:
            await ws.close()
        except:
            pass
        if sess.ext_chan_id:
            try:
                await ari.delete(f"/ari/channels/{sess.ext_chan_id}")
            except:
                pass
        if sess.bridge_id:
            try:
                await ari.delete(f"/ari/bridges/{sess.bridge_id}")
            except:
                pass
        sessions.pop(ch_id, None)
        processing_channels.discard(ch_id)


# ------------------ Main ARI events loop ------------------
async def run_events():
    ari = ARI(ASTERISK_HTTP, ASTERISK_ARI_USER, ASTERISK_ARI_PASS)
    while True:
        try:
            ws = await ari.ws_events(ASTERISK_ARI_APP)
            print("[bridge] ARI connected")
            async for raw in ws:
                try:
                    ev = json.loads(raw)
                except Exception:
                    continue

                t = ev.get("type")

                print(f"[bridge] ARI event: {t}")

                if t == "StasisStart":
                    # channel enters our app
                    ch = ev.get("channel", {})
                    ch_name = ch.get("name", "")
                    ch_id = ch.get("id")
                    ch_type = ch.get("channeltype", "UNKNOWN")
                    print(f"[bridge] StasisStart: name={ch_name}, channeltype={ch_type}")

                    # Handle external media channels (UnicastRTP)
                    if ch_name.startswith("UnicastRTP/") and ch_id in pending_ext:
                        meta = pending_ext.pop(ch_id)
                        bridge_id = meta["bridge_id"]
                        tel_id = meta["tel_id"]
                        print(
                            f"[bridge] External media {ch_id} ready, adding to bridge {bridge_id}"
                        )
                        try:
                            await ari.post(f"/ari/bridges/{bridge_id}/addChannel", channel=ch_id)
                            print(
                                f"[bridge] Successfully added external media {ch_id} to bridge {bridge_id}"
                            )
                        except Exception as e:
                            print(f"[bridge] Failed to add external media to bridge: {e}")
                            continue

                        # Set RTP peer explicitly from ext channel vars
                        async def _get_var(cid, key):
                            try:
                                v = await ari.get(f"/ari/channels/{cid}/variable", variable=key)
                                result = v.get("value")
                                if DEBUG_MODE:
                                    print(f"[bridge-debug] Variable {key} = {result}")
                                return result
                            except Exception as e:
                                if DEBUG_MODE:
                                    print(f"[bridge-debug] Failed to get variable {key}: {e}")
                                return None

                        if DEBUG_MODE:
                            print(
                                f"[bridge-debug] Attempting to discover RTP peer for ext channel {ch_id}"
                            )
                        addr = (await _get_var(ch_id, "UNICASTRTP_LOCAL_ADDRESS")) or (
                            await _get_var(ch_id, "UNICAST_RTP_LOCAL_ADDRESS")
                        )
                        port = (
                            (await _get_var(ch_id, "UNICASTRTP_LOCAL_PORT"))
                            or (await _get_var(ch_id, "UNICASTRTP_RTP_LOCAL_PORT"))
                            or (await _get_var(ch_id, "UNICAST_RTP_LOCAL_PORT"))
                        )

                        if DEBUG_MODE:
                            print(f"[bridge-debug] Discovered: addr={addr}, port={port}")

                        sess = sessions.get(tel_id)
                        if sess and addr and port:
                            try:
                                sess.rtp.peer = (addr, int(port))
                                print(
                                    f"[bridge] RTP peer set to {sess.rtp.peer} for tel {tel_id} / ext {ch_id}"
                                )
                                # Prime symmetric RTP with a few silence frames (20ms @ 8k = 160 samples)
                                for _ in range(6):  # ~120ms
                                    await sess.rtp.send_payload(ulaw_silence_frame(160), 160)
                                    await asyncio.sleep(0.02)
                                if DEBUG_MODE:
                                    print(f"[bridge-debug] Sent {6} silence frames to prime RTP")
                            except Exception as e:
                                print(f"[bridge] Failed to set RTP peer: {e}")
                        elif sess:
                            if DEBUG_MODE:
                                print(
                                    f"[bridge-debug] WARNING: Could not set RTP peer - addr={addr}, port={port}"
                                )
                        else:
                            if DEBUG_MODE:
                                print(
                                    f"[bridge-debug] WARNING: No session found for tel_id {tel_id}"
                                )
                        continue

                    # Handle PJSIP channels (incoming calls)
                    if not ch_name.startswith("PJSIP/"):
                        print(f"[bridge] Skipping non-PJSIP channel: {ch_name}")
                        continue

                    state = ch.get("state", "")
                    args = ev.get("args", [])
                    app_data = ch.get("dialplan", {}).get("app_data", "")

                    print(f"[bridge] StasisStart: channel {ch_id} (state: {state})")
                    print(f"[bridge] App args: {args}")
                    print(f"[bridge] App data: {app_data}")

                    # Try to extract call_id from app_data if args are empty
                    call_id_from_app_data = None
                    if app_data and "," in app_data:
                        # app_data format: "pipecat,call_id_here"
                        parts = app_data.split(",")
                        if len(parts) > 1:
                            call_id_from_app_data = parts[1].strip()
                            print(
                                f"[bridge] Extracted call_id from app_data: {call_id_from_app_data}"
                            )

                    if ch_id not in sessions and ch_id not in processing_channels:
                        print(f"[bridge] Starting session for channel {ch_id}")
                        processing_channels.add(ch_id)
                        # Pass both app_args and extracted call_id
                        asyncio.create_task(
                            start_for_channel(ari, ch_id, args, call_id_from_app_data)
                        )
                    else:
                        print(f"[bridge] Skipping {ch_id} - already in sessions or processing")

                elif t == "Dial":
                    ch_id = ev.get("channel", {}).get("id") or ev.get("peer", {}).get("id")
                    if ch_id:
                        callback_url = await get_var(ari, ch_id, "X_CALLBACK_URL")
                        if callback_url:
                            if ch_id in dial_callback_urls:
                                if DEBUG_MODE:
                                    print(
                                        f"[bridge] Callback URL already exists for {ch_id}: {dial_callback_urls[ch_id]}"
                                    )
                                pass
                            dial_callback_urls[ch_id] = callback_url
                            print(
                                f"[bridge] Dial event - stored callback URL for {ch_id}: {callback_url}"
                            )
                    else:
                        print(f"[bridge] Dial event without channel or peer ID: {ev}")

                elif t in ["StasisEnd", "ChannelDestroyed"]:
                    ch = ev.get("channel", {})
                    ch_id = ch.get("id")
                    ch_name = ch.get("name", "")

                    # Extract hangup cause information
                    cause = ev.get("cause", 0)
                    cause_txt = ev.get("cause_txt", "Unknown")

                    print(f"[bridge] {t}: {ch_id} ({ch_name}) - Cause: {cause} ({cause_txt})")

                    s = sessions.pop(ch_id, None)
                    processing_channels.discard(ch_id)
                    pending_ext.pop(ch_id, None)  # Clean up pending external media channels

                    if s:
                        # 1. If session is there means call is been established and is completed successfully
                        print(f"[bridge] Tearing down session for channel {ch_id}")

                        try:
                            if s.ws:
                                await s.ws.send(json.dumps({"event": "hangup"}))
                                await s.ws.close()
                        except Exception as e:
                            print(f"[bridge] Error sending hangup data: {e}")

                        # Clean up ext channel and bridge
                        try:
                            if s.ext_chan_id:
                                await ari.delete(f"/ari/channels/{s.ext_chan_id}")
                        except:
                            pass
                        try:
                            if s.bridge_id:
                                await ari.delete(f"/ari/bridges/{s.bridge_id}")
                        except:
                            pass
                    else:
                        # 2. If session is not there means call is not been established and is failed
                        hangup_data = {"event": "hangup", "status": get_call_status(cause)}
                        callback_url = dial_callback_urls.pop(ch_id, None)
                        if callback_url:
                            print(f"[bridge] Callback URL: {callback_url}")
                            print(f"[bridge] Hangup data: {hangup_data}")
                            try:
                                async with aiohttp.ClientSession() as session:
                                    await session.post(
                                        callback_url,
                                        data={"call_sid": ch_id, "status": get_call_status(cause)},
                                    )
                                print(f"[bridge] Called callback URL: {callback_url}")
                            except Exception as e:
                                print(f"[bridge] Callback failed: {e}")

        except Exception as e:
            print(f"[bridge] ARI WS error: {e}; reconnecting in 2s")
            await asyncio.sleep(2)


async def main():
    """Main function that runs both the ARI events handler and config reloader."""
    # Start both tasks concurrently
    await asyncio.gather(run_events(), config_reloader())


if __name__ == "__main__":
    print("[bridge] Starting Asterisk-Pipecat bridge with auto-reloading configuration...")
    asyncio.run(main())
