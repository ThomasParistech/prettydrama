# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PrettyDrama is a theater rehearsal tool that converts drama scripts into an interactive web-based rehearsal interface with text-to-speech audio. It helps actors practice their lines by playing other characters' dialogues while masking or highlighting the user's lines.

## Architecture

The system has three main components:

1. **Drama Parser** (`drama.py`): Dataclass-based parser that reads drama text files into a hierarchical structure: Drama → Acts → Scenes → Dialogues (character, text tuples)

2. **TTS Generator** (`generate_tts.py`): Uses Coqui XTTS v2 to generate audio for each dialogue line, organized by act/scene in the output directory. Includes VAD-based audio trimming.

3. **Rehearsal Page Generator** (`generate_rehearsal.py`): Generates a self-contained `index.html` with embedded drama data and JavaScript player. The HTML template is embedded in the Python file.

## Drama File Format

```
Title of the Play
==========Act==========
***Scene***
<character> Dialogue text
continued dialogue on next line
<other_character> Their dialogue
```

- First line is the title
- `=act=` (case-insensitive) marks act boundaries
- `*scene*` (case-insensitive) marks scene boundaries
- `<character>` at line start indicates speaker (subsequent lines continue the dialogue)

## Commands

### Generate TTS Audio (requires GPU and Docker)
```bash
./run.sh
```
This runs the Coqui TTS container with GPU support, generating audio files to `tts-output-default/`.

### Generate Rehearsal HTML
```bash
python3 generate_rehearsal.py
```
Produces `index.html` that can be opened directly in a browser. The generated HTML is self-contained with all drama data embedded as JSON.

## Key Files

- `full_drama.txt`: The main drama script being worked on
- `index.html`: Generated rehearsal interface (do not edit directly - regenerate from `generate_rehearsal.py`)
- Voice mappings are in `generate_tts.py` in the `VOICE_MAP` dictionary
