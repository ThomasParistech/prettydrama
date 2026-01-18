# 🎭 PrettyDrama

A theater rehearsal tool that converts scripts into interactive web pages with high-quality TTS-generated audio.

**[Live Demo: Transport de Femmes](https://thomasparistech.github.io/prettydrama/)**

---

## 🚀 Workflow

1. **Script (`.txt`)** → 2. **Docker (TTS)** → 3. **Python (UI Builder)** → 4. **Web Browser**

---

## ⚡ Quick Start

### 1. Format your script

Create `full_drama.txt` using this structure:

```text
Title of the Play
==========Act Name==========
***Scene Name***
<Character Name> Dialogue text
<Other Character> Their response

```

### 2. Generate Audio

Requires **Docker** + **NVIDIA GPU**. This will process the script and generate voice files.

```bash
sh run.sh

```

### 3. Build Interface

Run the generator to create the interactive rehearsal page:

```bash
python3 generate_rehearsal.py

```

### 4. Rehearse

Open `index.html` in your browser.

> **Tip:** Host the folder on **GitHub Pages** to practice on your phone/tablet during rehearsal.
