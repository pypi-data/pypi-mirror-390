# Pipecat Flows Agent Handbook

## Mission & Context
- **Primary goal**: build controllable voice agents that split work across multiple conversation nodes using the new flow framework under `src/pipecat_flows/` and the `ringg-bot/` runtime. The legacy single-agent example at `/Users/kalicharanvemuru/Documents/Code/dv-pipecat/examples/ringg-chatbot` is now read-only reference material.
- **Old vs new**: the old example bundled telephony orchestration, business logic, and prompts into one monolithic agent. This repository decouples those responsibilities into FlowManager-driven nodes so that each task (greeting, authentication, routing, escalation, etc.) has its own state, context policy, actions, and tool set.
- **Authoritative docs** live here. Copy anything you need from the old repo, but always implement against the structures described below. Do not point LLMs back to `examples/ringg-chatbot` when you want code changes.

## Where Things Live Now
- `src/pipecat_flows/` &nbsp;— reusable flow engine (FlowManager, adapters, action execution, shared types).
- `ringg-bot/` &nbsp;— production bot implementation that consumes FlowManager. Contains runtime config parsing, transport setup, telephony serializers, utilities, and flow-specific tools.
  - `ringg-bot/utils/generate_config.py` converts runtime JSON into strongly-typed configs and into Pipecat Flow node definitions.
  - `ringg-bot/utils/flow_tools/` holds flow-native functions (query KB, transfer calls, wait for DTMF, etc.) that are registered as node tools.
  - `ringg-bot/transports/` and `ringg-bot/voice_services/` wrap telephony/WebRTC integrations and provider-specific audio services.
  - `ringg-bot/PIPECAT_ARCHITECTURE.md` (synced from the old repo) is the deep dive on base Pipecat pipeline, frames, and processor architecture.
- `../dv-pipecat/src/pipecat/` &nbsp;— core Pipecat engine modules (frames, processors, base pipeline); lives in the adjacent repository and underpins this flows layer.
- `tests/` mirrors `src/pipecat_flows/` for unit coverage. Bot-level simulations live under `ringg-bot/tests/` and leverage the pipeline testing harness.

## Flow Engine Essentials (`src/pipecat_flows`)
- **`FlowManager`** (`manager.py`) orchestrates node lifecycles. It:
  - Registers tools/functions with the active LLM service via provider adapters (`adapters.py`).
  - Executes `pre_actions` and `post_actions` via `ActionManager` (`actions.py`) while respecting downstream frame ordering and bot speaking state.
  - Tracks shared `state`, pending transitions, and context strategy per node (`types.ContextStrategyConfig`).
  - Understands both **static flows** (predefined `FlowConfig`) and **dynamic flows** (runtime node injection).
- **Context strategies**: `APPEND`, `RESET`, `RESET_WITH_SUMMARY`. Summaries are generated through provider adapters when `summary_prompt` is supplied.
- **Function schemas**: wrap each callable (direct Python coroutine, JSON schema-defined function, or legacy dict) in a `FlowsFunctionSchema` so FlowManager can:
  - derive name/description/parameters,
  - register it with the provider adapter,
  - route tool calls to the correct Python handler.
- **Actions**: `tts_say`, `end_conversation`, and `function` are built-ins. You can register custom action handlers on `ActionManager` or attach inline `function` actions that execute coroutine callbacks inside the pipeline without breaking frame ordering.
- **Error taxonomy**: `FlowInitializationError`, `FlowTransitionError`, `InvalidFunctionError`, `ActionError`. Make sure LLM prompts surface these when asking for diagnostics.

## Runtime Configuration & Multi-Node Design
- **Entry format**: external orchestrator sends JSON that matches `ringg-bot/utils/generate_config.RunConfig`.
  - `orchestration_mode` determines single vs multi node but our default is multi-node.
  - `flow_config` defines each node: `role_messages`, `task_messages`, context policy, `pre_actions`, `post_actions`, and two tool buckets:
    - `predefined_tools`: shortcuts for built-in direct functions (`query_kb`, `stay_on_line`, `dtmf_output`, `switch_language`, `end_call`, `call_transfer`, `wait_for_dtmf`).
    - `functions`: API-backed or generic adapters that call out to HTTP endpoints via `_function_:generic_function` with optional caching/formatters.
    - `transition_functions`: explicit state transitions that return `{status, next_node}` pairs.
- `parse_flow_config_to_pipecat()` turns that JSON into a FlowManager-ready dict by:
  - Turning every tool into a `FlowsFunctionSchema` with bound handlers.
  - Normalizing action configs (auto enabling `mirror_context` on `tts_say`, disabling cache by default).
  - Resolving `ContextStrategyCustom` into `ContextStrategyConfig`.
- **Runtime overrides** (`Node.overrides`) let you change VAD, fillers, DTMF, or other channel-specific settings for a single node and are consumed when the bot builds pipeline processors.

## How the Bot Uses Flows (`ringg-bot/bot_with_flows.py`)
1. **Config ingestion**: `generate_call_config()` normalizes payload (language codes, `from` → `from_number`, etc.) and returns `RunConfig` with nested `CallConfig` + `FlowConfig`.
2. **Service bootstrap** (`utils/bot_common.initialize_services`): spins up LLM/STT/TTS providers based on the call config (supports OpenAI, Azure, Groq, Vistaar, Deepgram, ElevenLabs, etc.). Handles voice options, vocab injection, caching toggles, and noise filtering.
3. **Pipeline wiring**:
   - Builds `PipelineTask`, transports (`transports.factory.build_transport`), VAD analyzers (`SileroVADAnalyzer`), smart turn modules, background audio mixers, transcript handlers, Redis clients, and hold/idle detectors.
   - Generates `pipecat_flow_config` via `parse_flow_config_to_pipecat` and instantiates `FlowManager` with:
     - Pipeline task for frame scheduling.
     - LLM service + provider adapter auto-detected in `FlowManager.__init__`.
     - `context_aggregator` based on `OpenAILLMContext` (or provider equivalent via adapters).
     - Transport reference so actions can push frames directly.
4. **Execution loop**: the pipeline runner streams frames between transport → STT → FlowManager-controlled LLM → TTS → transport. `ActionManager` uses special frames (`FunctionActionFrame`, `ActionFinishedFrame`, `BotStoppedSpeakingFrame`) to respect downstream ordering and to trigger deferred `post_actions` only after the bot finishes speaking.
5. **State transitions**: node functions call `flow_manager.set_next_node(...)` (via transition handlers) or return `(FlowResult, next_node)` tuples. Context strategies determine how chat history is preserved when switching nodes.
6. **Shutdown**: `end_call` tools/actions push `EndFrame` and clean up transports, mixers, Redis locks, Weaviate connections, and local recordings.

## End-of-Call Notice (pre-hangup announcement)

Add a short announcement before the telephony provider cuts the call at `max_call_length`.

- `timeout_msg_on` (bool): Enable/disable the feature. Default: `false`.
- `timeout_texts` (map): Language → message. Keys can be base 2‑letter (e.g., "en", "hi") or locale codes (e.g., "en-IN", "hi-IN"). Example: `{ "en-IN": "Call ending.", "hi-IN": "कॉल समाप्त हो रही है." }`
- `timeout_msg_dur` (int): Seconds before `max_call_length` to speak the message. Default: `10`.

Behavior:
- Language is inferred from the most recent LLM assistant output (script/diacritics heuristic). Keys in `timeout_texts` are normalized to their base 2‑letter codes when matching (e.g., "en-IN" → "en").
- Allowed languages are derived from `call_config.language` and `call_config.add_langs` (normalized to base 2‑letter codes). If the detected language is not allowed, the notice falls back to "en" if present, otherwise the first available entry.
- The pipeline sends a StartInterruption frame to cut ongoing bot speech, then mutes STT while delivering the final message so user speech doesn't interfere.

Example `call_config`:
```json
{
  "max_call_length": 300,
  "language": "en-IN",
  "add_langs": ["hi-IN"],
  "timeout_msg_on": true,
  "timeout_texts": {
    "en-IN": "We're wrapping up this call.",
    "hi-IN": "यह कॉल समाप्त हो रही है."
  },
  "timeout_msg_dur": 12
}
```

## Toolkit Summary
- **Predefined direct tools** (flow-native and coroutine friendly):
  - `query_kb`: retrieval-augmented answers with optional deterministic field filters; uses `rag/weaviate_script.py` client and respects `rag_collection_name`.
  - `stay_on_line`: keeps participant engaged while escalation or manual join happens.
  - `dtmf_output`, `wait_for_dtmf`: output tones and collect keypad input with optional timeout/digit requirements.
  - `switch_language`: swaps STT/TTS configuration mid-call.
  - `end_call`: gracefully hang up with optional reason phrases.
  - `call_transfer`: connects to live agent, updates telephony transport, and coordinates background audio fillers.
- **Generic API functions**: define `http` payload in config and FlowManager will call `_function_:generic_function`, transparently handle caching (`cache_ttl`, `cache_response`), and format responses (`response_formatter`, `responseSelectedKeys`).
- **Actions**:
  - `tts_say` supports `use_cache`, `mirror_context`, and custom text; it is rendered via `ActionManager._handle_tts_action` by pushing `TTSSpeakFrame` (with optional caching hook in `say_with_cache`).
  - `function` actions run inline async coroutines inside the pipeline (useful for analytics, notifications, or gating state).
  - `end_conversation` injects `EndFrame` and signals transports to hang up.

## Telephony & Transports
- `ringg-bot/server.py` exposes FastAPI HTTP + WebSocket endpoints for Twilio/Plivo/Exotel/Asterisk/ConVox streaming.
- Serializers (`utils/bot_common.get_telephony_serialiser`) adapt audio framing per provider (sample rates, codecs, auth details).
- Transports layer (`transports/`) adds WebRTC (Daily Web Call), WebSocket bridging, and channel-aware configuration through `build_transport`.
- Voice services (`voice_services/`) encapsulate provider-specific quirks (e.g., ElevenLabs v1/v2 API selection, Azure deployment names, Cartesia streaming) so FlowManager stays provider-agnostic.

## Testing & Diagnostics
- `ringg-bot/PIPELINE_TESTING.md` documents frame-level simulations. Use `pipeline_test.py` to feed deterministic frame sequences (user start/stop speaking, transcriptions, interruptions) through the full pipeline without telephony.
- `tests/test_manager.py`, `tests/test_actions.py`, etc., cover FlowManager and ActionManager edge cases (context resets, action ordering, function registration). Extend these tests when adding new features.
- Logging: the bot binds `call_id` to the logger context. Use `logger.bind(...)` when adding instrumentation so traces stay grouped per call.
- Retry & timeout knobs live in `utils/pipeline.py` (idle handlers, hold detector) and `utils/stay_on_line_processor.py`. Update both place and config schema when adjusting thresholds.

## Working Guidelines for LLM Instructions
- Always operate on `ringg-bot/` when modifying production bot logic. Do **not** resurrect `examples/ringg-chatbot`; mention it only as historical reference.
- When adding a new conversational capability:
  1. Extend the runtime schema in `utils/generate_config.py` (Pydantic models).
  2. Create tool/action implementation (prefer `utils/flow_tools` for node functions) with docstrings explaining purpose and expected args.
  3. Register tool via flow config (predefined or API) and ensure tests cover the new behavior.
  4. Update documentation (this file plus any relevant Markdown under `ringg-bot/`).
- Respect context policies: avoid hard-coding resets or summaries—use `ContextStrategyConfig`. Summaries rely on adapter-specific `generate_summary` implementations; provide `summary_prompt` when you expect the LLM to compress history.
- Keep transports and services stateless between calls; shared resources (Redis, Weaviate) must be acquired/released inside the call lifecycle.

## Reference Documents in This Repo
- `ringg-bot/PIPECAT_ARCHITECTURE.md` — deep dive on Pipecat frames, pipelines, services (copied from the legacy repo for completeness).
- `ringg-bot/DEPLOYMENT.md` — GKE deployment pipeline (branches, Helm charts, canary vs stable strategy).
- `ringg-bot/README.md` — Twilio/WebSocket quick start (update instructions here if startup commands change).
- `ringg-bot/PIPELINE_TESTING.md` — simulation harness documentation.
- `docs/` — broader Pipecat flows user guides (keep in sync when adding features).

## Call Transfer System (Asterisk/SIP Integration)

### Overview
The call transfer system supports multiple transfer methods for different SIP providers and integration scenarios. It uses a **Strategy Pattern** for extensibility.

### Supported Transfer Methods

1. **SIP REFER (RFC 3515)** - Default method
   - Standard SIP blind transfer via REFER message
   - Sends REFER to existing SIP peer (not Asterisk)
   - SIP provider handles transfer on their end
   - **No outbound trunk needed** - uses existing channel
   - Most compatible with SIP trunks

2. **HTTP Callback** - Custom API integration
   - Calls client's API to notify about transfer
   - Client handles transfer logic on their end
   - Useful for complex routing requirements

3. **Dialplan Context** - Advanced Asterisk routing
   - Redirects to custom Asterisk dialplan context
   - Full control over transfer logic in Asterisk
   - Enables IVR-based transfers

### Configuration

#### Option 1: Via Dialplan Variables (Recommended for Inbound)

Set transfer configuration in `extensions.conf`:

```ini
[PB_Fintech_RINGG]
exten => _X.,1,NoOp(Incoming call from PB Fintech)
 same => n,Set(__INBOUND_PROVIDER=pb_fintech)
 same => n,Set(__TRANSFER_TYPE=sip_refer)              ; Transfer method
 same => n,Set(__TRANSFER_SIP_DOMAIN=pbfintech.com)    ; Optional: SIP domain
 same => n,Stasis(pipecat,${EXTEN})
 same => n,Hangup()
```

These variables are automatically extracted by pipecat-bridge and passed to the bot.

#### Option 2: Via Runtime Config (For Outbound or Override)

Transfer behavior should be configured under `call_config.transfer`. Provider-specific runtime details are injected later by the bridge.

```json
{
  "telephony_provider": "asterisk",
  "transfer": {
    "type": "sip_refer|http_callback|dialplan_context",
    "sip_domain": "pbfintech.com",
    "context": "custom-transfer-context",
    "extension_template": "{target}",
    "summary": {
      "enabled": true,
      "send_on": "parallel",
      "generate": {"prompt": "Summarize conversation...", "max_chars": 800},
      "http": {"url": "https://api.client.com/transfer/summary"}
    },
    "announcement": {"enabled": true, "mode": "speak_then_transfer"}
  }
}
```

### Architecture

**Location**: `ringg-bot/utils/call_transfer_strategies.py`

**Strategy Classes**:
- `CallTransferStrategy` - Abstract base class
- `SipReferTransferStrategy` - SIP REFER implementation
- `HttpCallbackTransferStrategy` - HTTP API callback
- `DialplanContextTransferStrategy` - Dialplan context redirect

**Usage in Code** (merge agent config with runtime overrides):
```python
from utils.call_transfer_strategies import get_transfer_strategy

# Build effective transfer config by merging agent cfg and runtime overrides
effective_transfer = {}
if getattr(call_config, "transfer", None):
    effective_transfer.update(call_config.transfer)
effective_transfer.update(provider_metadata.get("transfer", {}) or {})

transfer_type = effective_transfer.get("type", "sip_refer")
strategy = get_transfer_strategy(transfer_type)

# Execute transfer
result = await strategy.transfer(
    channel_id=channel_id,
    target=target_number,
    provider_metadata={**provider_metadata, "transfer": effective_transfer},
    bot_logger=logger,
    summary=conversation_summary
)
```

### Integration Points

1. **Flow Tools**: `ringg-bot/utils/flow_tools/call_transfer.py`
   - Used by FlowManager nodes with `call_transfer` predefined tool
   - Supports conversation summary generation via `_generate_transfer_summary()`

2. **LLM Functions**: `ringg-bot/utils/llm_functions/call_transfer.py`
   - Used by legacy single-node agents
   - Direct LLM tool call handling

3. **Custom WebSocket**: `ringg-bot/websocket/websocket_service.py`
   - For custom telephony providers
   - Uses `CallTransferFrame` pushed through transport

### Channel ID Resolution

For Asterisk transfers, channel_id can come from:
- **Inbound calls**: `provider_metadata["asterisk_channel_id"]` (set by pipecat-bridge.py)
- **Outbound calls**: `call_id` IS the channel_id (fallback)

```python
channel_id = provider_metadata.get("asterisk_channel_id") or call_id
```

### Adding New Transfer Methods

1. Create new strategy class inheriting from `CallTransferStrategy`
2. Implement `transfer()` method
3. Register in `TRANSFER_STRATEGIES` registry
4. Document configuration fields

Example:
```python
class MyCustomTransferStrategy(CallTransferStrategy):
    async def transfer(self, channel_id, target, provider_metadata, bot_logger, summary):
        # Custom logic here
        return {"status": "success", "data": {...}}

# Register
TRANSFER_STRATEGIES["my_custom"] = MyCustomTransferStrategy()
```

### Client Documentation

See `docs/CALL_TRANSFER_API.md` for complete API documentation to share with integration partners.
See `docs/examples/pb_fintech_call_transfer_config.json` for example configurations.

Developer design details (including provider identification and strategy behavior) are in `docs/IMPLEMENTATION_SUMMARY.md`.
For summary delivery and announcement options, see `docs/CALL_TRANSFER_SUMMARY_DESIGN.md`. Typical partner payload defaults normalize identifiers to two fields:

```
{
  "event": "call_summary",
  "provider": "pb_fintech",
  "identifiers": { "ringg_call_id": "...", "tel_call_id": "..." },
  "summary": "..."
}
```

### Testing

Test transfers with different methods:
```bash
# Enable Asterisk ARI debug
asterisk -rx "ari set debug on"

# Monitor bot logs
tail -f /var/log/ringg/bot.log | grep "call_transfer"

# Test SIP REFER
curl -X POST https://api.ringg.ai/call \
  -d '{"call_config": {"transfer": {"type": "sip_refer"}}}'
```

---

## Quick FAQ
- **"Where do I define a new node?"** — In the runtime payload (`flow_config.nodes[...]`), then ensure `generate_config.py` understands any new fields you introduce.
- **"How do I trigger a node switch manually?"** — Transition function handlers return `(FlowResult, next_node)` or call `flow_manager.set_next_node(name)` inside the function.
- **"Can a node reuse tools from another node?"** — Yes, add the same predefined tool or API entry. Tool handlers are reusable coroutines; context policy determines how much prior conversation the node inherits.
- **"How do I speak immediately without waiting for TTS cache?"** — Set `use_cache: false` (default) or configure `mirror_context` to avoid echoing system prompts. `ActionManager` already queues speech frames correctly.
- **"Where is the single-node agent prompt now?"** — Legacy fields (`prompt`, `kb_data`, `tools`, `intro_message`) still exist in `CallConfig` for backwards compatibility but should be avoided. Use flow nodes instead.
- **"How do I configure call transfers for a specific SIP client?"** — Set `call_config.transfer.type` and related fields. Provider-specific runtime details (like SIP provider, channel id, and dialplan-injected overrides) are added automatically by the bridge.

### Runtime-injected fields
- `provider_metadata.asterisk_channel_id`, `provider_metadata.asterisk_sip_provider` — set by the bridge for Asterisk calls.
- `provider_metadata.transfer.type`, `provider_metadata.transfer.sip_domain` — may be injected from dialplan variables (`TRANSFER_TYPE`, `TRANSFER_SIP_DOMAIN`) or ARI variables for outbound calls. Agents typically do not need to set these.

## Next Steps
- Before coding, confirm the desired behavior aligns with FlowManager capabilities described above.
- Run `ruff` and `pytest` after changes; for telephony features, also run `python ringg-bot/pipeline_test.py` with relevant scenarios.
- Keep this handbook updated whenever new node types, tools, or transports are introduced.
