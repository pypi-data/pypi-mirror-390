step 1 - just set the upstreams first -> eg. ( git remote add upstream https://github.com/pipecat-ai/pipecat.git )

upstream        https://github.com/pipecat-ai/pipecat.git (fetch)
upstream        https://github.com/pipecat-ai/pipecat.git (push)

step 2 - just go to the branch from where you want the changes to be merged

git checkout dv-stage

step 3 - git fetch upstream --tags

step 4 - you will see the versions like this - v0.0.87, v0.0.88 … v0.0.90

step 5 - Now for example - if you want to bump to the version 0.90

git checkout -b dv0.0.90 tags/v0.0.90

step 6 - now merge the branch ( eg. dv-stage to your branch ) - git merge dv-stage

step 7 - now fix the merge conflicts

pipecat/services/stt_service.py

stt is always muted be it voicemail is on or not, when the bot is speaking, voicemail detector sits below the stt and just does it’s job ( summarize or end the call ) and doesn’t sends the frames to llm.

# Only process audio if not muted, unless voicemail_detect is enabled and first speech not handled.

# If first speech is handled, we dont need to worry anymore.

if self.\_muted and ((not self.\_voicemail_detect) or self.\_first_speech_handled):
            return
We added this code in process_frame:
elif isinstance(frame, BotStoppedSpeakingFrame):
            if not self.\_first_speech_handled:
                self.\_first_speech_handled = True
            await self.push_frame(frame, direction)

Inside start method:
if hasattr(frame, "metadata") and "voicemail_detect" in frame.metadata:
            self.\_voicemail_detect = frame.metadata["voicemail_detect"]

Inside init:

# Custom fields from ai_services.py for voicemail and first speech handling

self.\_first_speech_handled: bool = False
        self.\_voicemail_detect: bool = False

src/pipecat/processors/aggregators/openai_llm_context.py
Function: get_messages_for_logging

# Remove the first message if it's a system message and there are messages

if len(msgs) > 0 and msgs[0].get("role") == "system":
            msgs.pop(0)

##         return json.dumps(msgs, ensure_ascii=False)

transports/websocket/fastapi.py:
self.\_conversation_id = None

Inside setup:
if _.metadata and "call_id" in _.metadata:
            self._conversation_id = _.metadata["call_id"]

---

except Exception as e:
            if isinstance(e, WebSocketDisconnect):
                logger.warning(
                    f"{self} WebSocket disconnected during send: {e}, application_state: {self.\_websocket.application_state}",
                    call_id=self.\_conversation_id,
                )
            else:
                logger.error(
                    f"{self} exception sending data: {e.**class**.**name**} ({e}), application_state: {self.\_websocket.application_state}",
                    call_id=self.\_conversation_id,
                )

frame_processor.py
self.logger = logger  # Will later be replaced with a bound logger
Inside \_\_start:
if frame.metadata and "call_id" in frame.metadata:
            self.logger = logger.bind(call_id=frame.metadata["call_id"])
            self.\_metrics.set_logger(self.logger)

azure/stt.py: Complete changes

stt_mute_filter.py:

# Then push the original frame

# Conditionally include InputAudioRawFrame in suppression tuple based on voicemail_detection_enabled

suppression_types = (
            InterruptionFrame,
            StartInterruptionFrame,
            VADUserStartedSpeakingFrame,
            VADUserStoppedSpeakingFrame,
            UserStartedSpeakingFrame,
            UserStoppedSpeakingFrame,
            InterimTranscriptionFrame,
            TranscriptionFrame,
        )
        if not self.\_voicemail_detection_enabled:
            suppression_types = suppression_types + (InputAudioRawFrame,)

---

Inside process_frame:
elif isinstance(frame, StartDTMFCaptureFrame):
            self.\_dtmf_capture_active = True
            should_mute = await self.\_should_mute()
        elif isinstance(frame, EndDTMFCaptureFrame):
            self.\_dtmf_capture_active = False
            should_mute = await self.\_should_mute()

---

In mute startegies:
case STTMuteStrategy.DTMF_CAPTURE:
                    if self.\_dtmf_capture_active:
                        return True

---

Inside \_\_init:
self.\_voicemail_detection_enabled = False  # Default to False
        self.\_dtmf_capture_active = False

BOT_VAD_STOP_SECS = 0.30 -> I think we set this in base_output.py
self.\_register_event_handler("on_output_terminated")

elif isinstance(frame, EndFrame): and in elif isinstance(frame, CancelFrame):
await self.\_call_event_handler("on_output_terminated", frame)
---
In the frames.py we made VADParamsUpdateFrame as SystemFrame 
and in base_input.py we added elif isinstance(frame, VADParamsUpdateFrame): before SystemFrame is handled.