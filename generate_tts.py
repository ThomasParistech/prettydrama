import os
import torch
import torchaudio
from TTS.api import TTS
from drama import Drama


def clean_text_for_tts(text: str) -> str:
    """Clean text to reduce end-of-sentence TTS artifacts."""
    text = text.strip()
    # Ensure sentence ends with punctuation (helps XTTS end cleanly)
    if text and text[-1] not in '.!?…;:':
        text += '.'
    return text


def load_vad_model():
    """Load Silero VAD model."""
    model, utils = torch.hub.load(
        repo_or_dir='snakers4/silero-vad',
        model='silero_vad',
        force_reload=False,
        trust_repo=True,
    )
    return model, utils


def trim_audio_with_vad(audio_path: str, vad_model, get_speech_timestamps, read_audio, save_audio, buffer_ms: int = 150):
    """Trim trailing silence/artifacts using VAD."""
    SAMPLE_RATE = 16000

    # Load and resample audio for VAD (requires 16kHz)
    wav, sr = torchaudio.load(audio_path)
    if sr != SAMPLE_RATE:
        resampler = torchaudio.transforms.Resample(sr, SAMPLE_RATE)
        wav_16k = resampler(wav)
    else:
        wav_16k = wav

    # Get speech timestamps
    speech_timestamps = get_speech_timestamps(wav_16k.squeeze(), vad_model, sampling_rate=SAMPLE_RATE)

    if not speech_timestamps:
        return  # No speech detected, keep original

    # Find end of last speech segment
    last_speech_end = speech_timestamps[-1]['end']

    # Convert back to original sample rate and add buffer
    buffer_samples = int(buffer_ms * sr / 1000)
    end_sample_orig = int(last_speech_end * sr / SAMPLE_RATE) + buffer_samples
    end_sample_orig = min(end_sample_orig, wav.shape[1])

    # Trim and save
    trimmed = wav[:, :end_sample_orig]
    torchaudio.save(audio_path, trimmed, sr)


# ==== SETTINGS PROFILE ====
# Choose: "default", "stable", or "balanced"
PROFILE = "default"

# Available profiles with their TTS settings and output directories
PROFILES = {
    "default": {
        "settings": {},
        "output_dir": "/root/tts-output-default",
    },
    "stable": {
        "settings": {
            "temperature": 0.85,
            "repetition_penalty": 10.0,
            "top_k": 80,
            "top_p": 0.9,
        },
        "output_dir": "/root/tts-output-stable",
    },
    "balanced": {
        "settings": {
            "temperature": 0.55,
            "repetition_penalty": 2.5,
            "top_k": 40,
            "top_p": 0.75,
        },
        "output_dir": "/root/tts-output-balanced",
    },
}

TTS_SETTINGS = PROFILES[PROFILE]["settings"]
OUTPUT_DIR = PROFILES[PROFILE]["output_dir"]

print(f"Using profile: {PROFILE}")
print(f"Settings: {TTS_SETTINGS or 'default'}")
print(f"Output: {OUTPUT_DIR}")

# Voice mapping for characters
VOICE_MAP = {
    # Male voices
    "capitaine": "Damien Black",
    "docteur": "Ferran Simen",
    "serge": "Baldur Sanjin",
    "tim": "Filip Traverse",
    # Female voices
    "catherine": "Nova Hogarth",
    "marthe": "Henriette Usha",
    "napo": "Daisy Studious",
    "annie": "Ana Florence",
    "sarah": "Maja Ruoho",
    "charlotte": "Claribel Dervla",
}

print("Loading drama file...")
drama = Drama.from_file("/root/full_drama.txt")

print("Loading TTS model...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
tts.to("cuda")

print("Loading VAD model for trimming...")
vad_model, vad_utils = load_vad_model()
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = vad_utils

total_lines = sum(
    len(scene.dialogues)
    for act in drama.acts
    for scene in act.scenes
)
current_line = 0

for act_idx, act in enumerate(drama.acts, start=1):
    act_dir = f"{OUTPUT_DIR}/act{act_idx}"
    os.makedirs(act_dir, exist_ok=True)

    for scene_idx, scene in enumerate(act.scenes, start=1):
        scene_dir = f"{act_dir}/scene{scene_idx}"
        os.makedirs(scene_dir, exist_ok=True)

        for line_idx, (character, dialogue) in enumerate(scene.dialogues, start=1):
            current_line += 1
            speaker = VOICE_MAP.get(character.lower())

            if speaker is None:
                print(f"[{current_line}/{total_lines}] Warning: No voice mapping for '{character}', skipping")
                continue

            filename = f"{line_idx:03d}_{character}.wav"
            output_path = f"{scene_dir}/{filename}"

            print(f"[{current_line}/{total_lines}] Act {act_idx}, Scene {scene_idx}: {character} -> {speaker}")
            print(f"    Text: {dialogue[:50]}{'...' if len(dialogue) > 50 else ''}")

            clean_dialogue = clean_text_for_tts(dialogue)
            tts.tts_to_file(
                text=clean_dialogue,
                speaker=speaker,
                language="fr",
                file_path=output_path,
                **TTS_SETTINGS,
            )

            # Trim trailing artifacts with VAD
            trim_audio_with_vad(output_path, vad_model, get_speech_timestamps, read_audio, save_audio)

print("Done!")
print(f"Output files organized in: {OUTPUT_DIR}/act<N>/scene<N>/")