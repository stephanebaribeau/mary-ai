# Mary — A Voice & Vision AI Companion

A conversational AI companion you talk to out loud. She listens through your
microphone, sees you through your webcam, recognizes you, reacts to your mood,
and answers with a synthesized voice through a real-time 3D avatar whose lips
move in sync with her speech.

Mary speaks Québécois French by default, but the personality and language are
fully configurable in `personality.py`.

## Features

- **Voice conversation:** voice activity detection, local speech-to-text with
  [faster-whisper](https://github.com/SYSTRAN/faster-whisper), local
  text-to-speech with [Piper](https://github.com/rhasspy/piper)
- **Claude as the brain:** persona, conversation history, and long-term memory
  (facts about the user are extracted and saved between sessions)
- **Local vision pipeline:** motion detection, face identification, and
  emotion detection all run locally. Claude is only called when something
  worth reacting to happens.
- **Mary's own emotions:** she has her own reactions to the conversation
  (happy, sad, angry, neutral, relaxed), independent of the user's detected mood
- **3D avatar:** a VRM model rendered in Godot, with real-time lip-sync driven
  by the audio amplitude and facial expressions driven by her emotion
- **Proactive behavior:** she greets you when she recognizes you and checks in
  after long silences

## Architecture

```
Microphone ─► VAD ─► Whisper (STT) ─┐
                                    ├─► Claude ─► reply + emotion
Webcam ─► motion ─► face ID ─► mood ┘               │
                                                     ▼
                              Piper (TTS) ─► speakers
                                    │
                         amplitude + emotion (UDP)
                                    ▼
                         Godot 3D avatar (VRM)
```

## Requirements

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)
- A microphone and a webcam
- [Godot 4.x](https://godotengine.org/) with the
  [godot-vrm](https://github.com/V-Sekai/godot-vrm) and
  [Godot-MToon-Shader](https://github.com/V-Sekai/Godot-MToon-Shader) addons
- A `.vrm` avatar (for example created with
  [VRoid Studio](https://vroid.com/en/studio))
- A Piper voice model (e.g. `fr_FR-siwis-medium`) placed in `voices/`

## Setup

```bash
git clone https://github.com/<your-username>/mary-ai-companion.git
cd mary-ai-companion
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # then add your ANTHROPIC_API_KEY
```

Download a Piper voice into `voices/`, then adjust the microphone name hint
(`MIC_NAME_HINT`) in `audio_io.py` to match your device.

## Running

1. Open the Godot project and run the avatar scene (F6).
2. In a terminal: `python main.py`
3. Wait for "Je t'écoute..." and start talking. Press Ctrl+C to quit
   (Mary saves what she learned about you before exiting).

## Project structure

| File | Role |
|------|------|
| `main.py` | Event loop tying audio, vision, brain, and speech together |
| `brain.py` | Claude conversation, memory updates, emotion classification |
| `personality.py` | System prompt and persona |
| `memory.py` | Long-term fact storage |
| `audio_io.py` | Microphone capture, voice activity detection, playback |
| `stt.py` / `tts.py` | Speech-to-text and text-to-speech |
| `vision.py` | Webcam watcher: motion, identity, mood triggers |
| `identity.py` / `emotion.py` | Local face recognition and emotion detection |
| `lipsync.py` | UDP bridge sending mouth amplitude and emotion to Godot |
| `config.py` | Central settings |

## Privacy

Face recognition, emotion detection, and speech-to-text run locally. Only text
(and occasionally a webcam frame when something notable happens) is sent to the
Anthropic API. Memory and face data stay on your machine and are excluded from
version control.

## Roadmap

- Finer-grained emotion detection with MediaPipe blendshapes
- Whisper hallucination filtering
- Higher-fidelity avatars
- Smoother expression transitions

## License
Licensed under the [Apache License, Version 2.0](LICENSE).
