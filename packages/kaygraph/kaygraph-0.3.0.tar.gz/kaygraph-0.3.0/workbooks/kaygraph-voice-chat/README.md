# KayGraph Voice Chat

**Category**: 🔴 Demonstration Example (Uses Mock STT/TTS)

This example demonstrates how to build voice-enabled conversational AI using KayGraph. It integrates speech-to-text (STT) and text-to-speech (TTS) with intelligent conversation management.

> ⚠️ **Important**: This example uses mock audio processing to demonstrate the voice chat pattern without requiring audio APIs or hardware. All STT returns "mock transcription" and TTS generates fake audio data. See [Converting to Production](#converting-to-production) for real audio implementation.

## Features Demonstrated

1. **Speech-to-Text**: Convert voice input to text using multiple providers
2. **Text-to-Speech**: Generate natural speech from AI responses
3. **Streaming Audio**: Handle real-time audio streams
4. **Voice Activity Detection**: Detect when user starts/stops speaking
5. **Conversation Memory**: Maintain context across voice interactions

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Audio Capture   │────▶│ Speech-to-Text  │────▶│ Process Intent  │
│ (Microphone)    │     │ (STT Node)      │     │ (LLM Node)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Audio Playback  │◀────│ Text-to-Speech  │◀────│ Generate Reply  │
│ (Speaker)       │     │ (TTS Node)      │     │ (Response Node) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Usage

### Basic Voice Chat
```bash
# Start voice chat with default settings
python main.py

# Use specific STT/TTS providers
python main.py --stt whisper --tts elevenlabs

# Set conversation personality
python main.py --personality "friendly assistant"
```

### Advanced Options
```bash
# Enable wake word detection
python main.py --wake-word "hey assistant"

# Use push-to-talk instead of voice activity detection
python main.py --push-to-talk

# Save conversation audio
python main.py --save-audio ./recordings/
```

## Supported Providers

### Speech-to-Text (STT)
- **Whisper** (OpenAI): High accuracy, multiple languages
- **Google Speech**: Fast, streaming support
- **Azure Speech**: Enterprise features
- **Local Whisper**: Privacy-focused, offline

### Text-to-Speech (TTS)
- **ElevenLabs**: Most natural voices
- **Google TTS**: Fast, many languages
- **Azure TTS**: Neural voices
- **Local TTS**: Privacy-focused

## Examples

### 1. Simple Voice Assistant
Basic voice interaction with conversation memory.

### 2. Multi-lingual Support
Automatically detect and respond in user's language.

### 3. Voice-Controlled Actions
Execute commands based on voice input.

### 4. Emotional TTS
Adjust voice tone based on conversation context.

## Key Concepts

### Voice Activity Detection (VAD)
- Detects speech segments in audio stream
- Reduces false triggers and improves UX
- Configurable sensitivity

### Audio Streaming
- Handles real-time audio processing
- Buffering for optimal performance
- Graceful handling of network issues

### Conversation Context
- Maintains conversation history
- Speaker diarization (who said what)
- Emotion and intent tracking

## Production Considerations

1. **Latency Optimization**
   - Use streaming STT for faster response
   - Pre-generate common TTS phrases
   - Local models for critical paths

2. **Error Handling**
   - Fallback to text input on audio issues
   - Retry logic for API failures
   - Graceful degradation

3. **Privacy & Security**
   - Option for local processing
   - Audio data retention policies
   - User consent management

4. **Scalability**
   - Queue audio processing tasks
   - Load balance across providers
   - Cache TTS outputs

## Converting to Production

This example uses mock audio processing for demonstration. To implement real voice chat:

### 1. Replace Mock STT Implementation

In `voice_nodes.py`, replace the mock transcription:

```python
# Current mock implementation (line ~135)
async def exec_async(self, audio_data):
    return "This is a mock transcription for demo purposes"

# Production implementation with OpenAI Whisper
async def exec_async(self, audio_data):
    import openai
    client = openai.Client(api_key=os.environ["OPENAI_API_KEY"])
    
    # Save audio to temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        f.write(audio_data)
        f.flush()
        
        # Transcribe with Whisper
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=open(f.name, "rb")
        )
    return transcript.text
```

### 2. Replace Mock TTS Implementation

In `voice_nodes.py`, replace the mock audio generation:

```python
# Current mock implementation (lines ~212-230)
async def exec_async(self, text):
    # Returns fake audio data
    mock_audio = b"MOCK_AUDIO_DATA" * 1000
    return mock_audio

# Production implementation with ElevenLabs
async def exec_async(self, text):
    import requests
    
    response = requests.post(
        "https://api.elevenlabs.io/v1/text-to-speech/voice-id",
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
        json={"text": text, "voice_settings": {...}}
    )
    return response.content  # Actual audio data
```

### 3. Implement Real Audio Capture

Replace mock audio recording:

```python
# Current mock (lines ~314-325)
def record_audio(duration=5):
    return b"FAKE_AUDIO" * 1000

# Production with pyaudio
import pyaudio
import wave

def record_audio(duration=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    return b''.join(frames)
```

### 4. Required Dependencies

Add to requirements.txt:
```
openai>=1.0.0          # For Whisper STT
elevenlabs>=0.2.0      # For TTS (or alternative)
pyaudio>=0.2.11        # For audio capture
numpy>=1.24.0          # For audio processing
webrtcvad>=2.0.10      # For voice activity detection
```

### 5. Environment Setup

```bash
# API Keys
export OPENAI_API_KEY="sk-..."
export ELEVENLABS_API_KEY="..."

# Or for Google Cloud
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### 6. Hardware Requirements

- **Microphone**: For audio input
- **Speakers/Headphones**: For audio output
- **Permissions**: Microphone access on the system

## Mock vs Production Comparison

| Feature | Mock Implementation | Production Implementation |
|---------|-------------------|--------------------------|
| STT | Returns "mock transcription" | Real speech recognition |
| TTS | Returns fake audio bytes | Generates real speech |
| Audio Capture | Returns dummy data | Records from microphone |
| Latency | Instant | 1-3 seconds typical |
| Cost | Free | ~$0.006/minute (Whisper) |
| Hardware | None required | Microphone + speakers |