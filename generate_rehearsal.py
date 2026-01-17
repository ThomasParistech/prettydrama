#!/usr/bin/env python3
"""Generate a mobile-friendly rehearsal webpage from drama data."""

import json
import os
from drama import Drama

DRAMA_FILE = "full_drama.txt"
TTS_OUTPUT_DIR = "tts-output"
OUTPUT_HTML = "rehearsal.html"


def generate_drama_data(drama: Drama, tts_dir: str) -> dict:
    """Convert drama to JSON-serializable structure with audio paths."""
    characters = set()
    acts_data = []

    for act_idx, act in enumerate(drama.acts, start=1):
        scenes_data = []
        for scene_idx, scene in enumerate(act.scenes, start=1):
            dialogues_data = []
            for line_idx, (character, text) in enumerate(scene.dialogues, start=1):
                characters.add(character.lower())
                audio_path = f"{tts_dir}/act{act_idx}/scene{scene_idx}/{line_idx:03d}_{character}.wav"
                dialogues_data.append({
                    "character": character,
                    "text": text,
                    "audio": audio_path
                })
            scenes_data.append({"dialogues": dialogues_data})
        acts_data.append({"scenes": scenes_data})

    return {
        "characters": sorted(characters),
        "acts": acts_data
    }


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Répétition</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-page: #f9f6f1;
            --bg-card: #ffffff;
            --bg-warm: #f3ebe0;
            --accent: #c45c3e;
            --accent-light: #e8d4c8;
            --accent-dark: #9a4530;
            --text-dark: #2d2926;
            --text-medium: #5c554e;
            --text-light: #8a8279;
            --border: #e5ddd3;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-page);
            color: var(--text-dark);
            min-height: 100vh;
            padding-bottom: 180px;
        }

        header {
            background: var(--bg-card);
            padding: 24px 20px 20px;
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid var(--border);
            box-shadow: 0 2px 8px rgba(45, 41, 38, 0.06);
        }

        .header-title {
            text-align: center;
            margin-bottom: 24px;
        }

        h1 {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.75rem;
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 4px;
        }

        .subtitle {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 0.95rem;
            font-style: italic;
            color: var(--text-light);
        }

        .nav-row {
            display: flex;
            gap: 12px;
            margin-bottom: 14px;
        }

        .select-wrapper {
            flex: 1;
            position: relative;
        }

        .select-wrapper::after {
            content: '';
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid var(--text-light);
            pointer-events: none;
        }

        .nav-row select, .rehearse-section select {
            width: 100%;
            padding: 12px 16px;
            padding-right: 36px;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: var(--bg-page);
            color: var(--text-dark);
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            font-weight: 500;
            appearance: none;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .nav-row select:focus, .rehearse-section select:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-light);
        }

        .rehearse-section {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            background: var(--bg-warm);
            border-radius: 10px;
        }

        .rehearse-section label {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1rem;
            font-style: italic;
            color: var(--text-medium);
            white-space: nowrap;
        }

        .rehearse-section .select-wrapper {
            flex: 1;
        }

        .rehearse-section .select-wrapper::after {
            border-top-color: var(--accent);
        }

        .rehearse-section select {
            background: var(--bg-card);
            border-color: var(--accent-light);
            color: var(--accent-dark);
            font-weight: 600;
        }

        .rehearse-section select:focus {
            border-color: var(--accent);
        }

        .dialogue-container {
            padding: 20px;
        }

        .dialogue-card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 12px;
            border: 1px solid var(--border);
            position: relative;
            transition: all 0.2s ease;
            box-shadow: 0 1px 3px rgba(45, 41, 38, 0.04);
        }

        .dialogue-card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 12px;
            bottom: 12px;
            width: 3px;
            background: var(--border);
            border-radius: 2px;
            transition: all 0.2s ease;
        }

        .dialogue-card.active {
            border-color: var(--accent-light);
            box-shadow: 0 4px 12px rgba(196, 92, 62, 0.1);
        }

        .dialogue-card.active::before {
            background: var(--accent);
            top: 8px;
            bottom: 8px;
        }

        .dialogue-card.muted {
            background: var(--bg-warm);
            border-color: var(--accent-light);
        }

        .dialogue-card.muted::before {
            background: var(--accent);
            opacity: 0.5;
        }

        .dialogue-card.muted.active {
            box-shadow: 0 4px 12px rgba(196, 92, 62, 0.15);
        }

        .dialogue-card.muted.active::before {
            opacity: 1;
        }

        .character-name {
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
            color: var(--text-light);
        }

        .dialogue-card.active .character-name {
            color: var(--accent);
        }

        .dialogue-card.muted .character-name {
            color: var(--accent);
        }

        .dialogue-text {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.25rem;
            line-height: 1.6;
            white-space: pre-wrap;
            color: var(--text-dark);
        }

        .dialogue-card.muted .dialogue-text {
            color: var(--text-medium);
        }

        .your-line-badge {
            display: none;
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 0.85rem;
            font-style: italic;
            color: var(--accent);
            margin-bottom: 6px;
        }

        .dialogue-card.muted .your-line-badge {
            display: block;
        }

        .controls {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to top, var(--bg-page) 80%, transparent);
            padding: 28px 20px 24px;
        }

        .controls-inner {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 16px 20px 20px;
            border: 1px solid var(--border);
            box-shadow: 0 -4px 20px rgba(45, 41, 38, 0.08);
        }

        .progress-container {
            margin-bottom: 14px;
            padding: 8px 0;
            cursor: pointer;
        }

        .progress-bar {
            width: 100%;
            height: 6px;
            background: var(--bg-warm);
            border-radius: 6px;
            overflow: hidden;
            position: relative;
        }

        .progress-bar:hover {
            height: 8px;
        }

        .progress-fill {
            height: 100%;
            background: var(--accent);
            border-radius: 6px;
            transition: width 0.15s ease;
            pointer-events: none;
        }

        .status-bar {
            text-align: center;
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 0.9rem;
            font-style: italic;
            color: var(--text-light);
            margin-bottom: 14px;
        }

        .control-buttons {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 16px;
        }

        .control-btn {
            background: var(--bg-warm);
            border: 1px solid var(--border);
            color: var(--text-medium);
            width: 48px;
            height: 48px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .control-btn:hover {
            background: var(--bg-card);
            border-color: var(--accent-light);
            color: var(--accent);
        }

        .control-btn:active {
            transform: scale(0.96);
        }

        .control-btn svg {
            width: 18px;
            height: 18px;
            fill: currentColor;
        }

        .control-btn.play-btn {
            width: 60px;
            height: 60px;
            background: var(--accent);
            border: none;
            color: white;
            box-shadow: 0 3px 10px rgba(196, 92, 62, 0.25);
        }

        .control-btn.play-btn:hover {
            background: var(--accent-dark);
            color: white;
        }

        .control-btn.play-btn svg {
            width: 22px;
            height: 22px;
        }

        .control-btn.active {
            background: var(--accent);
            border-color: var(--accent);
            color: white;
        }

        .loop-indicator {
            text-align: center;
            margin-top: 12px;
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 0.85rem;
            font-style: italic;
            color: var(--text-light);
        }

        .loop-indicator.active {
            color: var(--accent);
        }

        .wait-indicator {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            padding: 32px 40px;
            background: var(--bg-card);
            border: 2px solid var(--accent);
            border-radius: 16px;
            box-shadow: 0 20px 50px rgba(45, 41, 38, 0.2);
            z-index: 200;
        }

        .wait-indicator.visible {
            display: block;
            animation: gentle-appear 0.3s ease;
        }

        .wait-indicator-text {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.6rem;
            font-style: italic;
            color: var(--accent);
        }

        .wait-indicator-sub {
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            color: var(--text-light);
            margin-top: 10px;
        }

        @keyframes gentle-appear {
            from {
                opacity: 0;
                transform: translate(-50%, -48%);
            }
            to {
                opacity: 1;
                transform: translate(-50%, -50%);
            }
        }

        .scene-divider {
            text-align: center;
            padding: 10px 0;
            color: var(--text-light);
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <header>
        <div class="header-title">
            <h1>Répétition</h1>
            <div class="subtitle">Méthode à l'italienne</div>
        </div>
        <div class="nav-row">
            <div class="select-wrapper">
                <select id="act-select"></select>
            </div>
            <div class="select-wrapper">
                <select id="scene-select"></select>
            </div>
        </div>
        <div class="rehearse-section">
            <label>Je joue</label>
            <div class="select-wrapper">
                <select id="character-select">
                    <option value="">Écoute seule</option>
                </select>
            </div>
        </div>
    </header>

    <div class="dialogue-container" id="dialogue-container"></div>

    <div class="wait-indicator" id="wait-indicator">
        <div class="wait-indicator-text">À vous...</div>
        <div class="wait-indicator-sub">Appuyez sur suivant</div>
    </div>

    <div class="controls">
        <div class="controls-inner">
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-fill"></div>
                </div>
            </div>
            <div class="status-bar" id="status-bar">Prêt</div>
            <div class="control-buttons">
                <button class="control-btn" id="prev-btn" aria-label="Previous">
                    <svg viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
                </button>
                <button class="control-btn play-btn" id="play-btn" aria-label="Play">
                    <svg viewBox="0 0 24 24" id="play-icon"><path d="M8 5v14l11-7z"/></svg>
                </button>
                <button class="control-btn" id="next-btn" aria-label="Next">
                    <svg viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
                </button>
                <button class="control-btn" id="loop-btn" aria-label="Loop">
                    <svg viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
                </button>
            </div>
            <div class="loop-indicator" id="loop-indicator">Boucle désactivée</div>
        </div>
    </div>

    <audio id="audio-player" preload="auto"></audio>

    <script>
        const DRAMA_DATA = __DRAMA_DATA__;

        let currentActIndex = 0;
        let currentSceneIndex = 0;
        let currentDialogueIndex = 0;
        let isPlaying = false;
        let isLooping = false;
        let rehearseCharacter = "";

        const actSelect = document.getElementById("act-select");
        const sceneSelect = document.getElementById("scene-select");
        const characterSelect = document.getElementById("character-select");
        const dialogueContainer = document.getElementById("dialogue-container");
        const audioPlayer = document.getElementById("audio-player");
        const playBtn = document.getElementById("play-btn");
        const prevBtn = document.getElementById("prev-btn");
        const nextBtn = document.getElementById("next-btn");
        const loopBtn = document.getElementById("loop-btn");
        const progressFill = document.getElementById("progress-fill");
        const loopIndicator = document.getElementById("loop-indicator");
        const statusBar = document.getElementById("status-bar");
        const waitIndicator = document.getElementById("wait-indicator");

        function init() {
            // Populate act selector
            DRAMA_DATA.acts.forEach((_, i) => {
                const opt = document.createElement("option");
                opt.value = i;
                opt.textContent = `Acte ${i + 1}`;
                actSelect.appendChild(opt);
            });

            // Populate character selector
            DRAMA_DATA.characters.forEach(char => {
                const opt = document.createElement("option");
                opt.value = char;
                opt.textContent = char.charAt(0).toUpperCase() + char.slice(1);
                characterSelect.appendChild(opt);
            });

            actSelect.addEventListener("change", () => {
                currentActIndex = parseInt(actSelect.value);
                currentSceneIndex = 0;
                currentDialogueIndex = 0;
                updateSceneSelect();
                renderScene();
                stop();
            });

            sceneSelect.addEventListener("change", () => {
                currentSceneIndex = parseInt(sceneSelect.value);
                currentDialogueIndex = 0;
                renderScene();
                stop();
            });

            characterSelect.addEventListener("change", () => {
                rehearseCharacter = characterSelect.value;
                renderScene();
            });

            playBtn.addEventListener("click", togglePlay);
            prevBtn.addEventListener("click", prevDialogue);
            nextBtn.addEventListener("click", nextDialogue);
            loopBtn.addEventListener("click", toggleLoop);

            // Progress bar click to seek
            const progressContainer = document.querySelector(".progress-container");
            progressContainer.addEventListener("click", seekFromProgressBar);

            audioPlayer.addEventListener("ended", onAudioEnded);
            audioPlayer.addEventListener("timeupdate", updateProgress);

            updateSceneSelect();
            renderScene();
        }

        function updateSceneSelect() {
            sceneSelect.innerHTML = "";
            const act = DRAMA_DATA.acts[currentActIndex];
            act.scenes.forEach((_, i) => {
                const opt = document.createElement("option");
                opt.value = i;
                opt.textContent = `Scène ${i + 1}`;
                sceneSelect.appendChild(opt);
            });
            sceneSelect.value = currentSceneIndex;
        }

        function getCurrentScene() {
            return DRAMA_DATA.acts[currentActIndex].scenes[currentSceneIndex];
        }

        function renderScene() {
            const scene = getCurrentScene();
            dialogueContainer.innerHTML = "";

            scene.dialogues.forEach((d, i) => {
                const card = document.createElement("div");
                card.className = "dialogue-card";
                card.dataset.index = i;

                const isMuted = d.character.toLowerCase() === rehearseCharacter.toLowerCase();
                if (isMuted) card.classList.add("muted");

                const charEl = document.createElement("div");
                charEl.className = "character-name";
                charEl.textContent = d.character;

                const textEl = document.createElement("div");
                textEl.className = "dialogue-text";
                textEl.textContent = isMuted ? d.text : d.text;

                card.appendChild(charEl);
                card.appendChild(textEl);
                dialogueContainer.appendChild(card);

                card.addEventListener("click", () => {
                    currentDialogueIndex = i;
                    highlightCurrent();
                    if (isPlaying) playCurrentDialogue();
                });
            });

            highlightCurrent();
            updateStatus();
        }

        function highlightCurrent() {
            document.querySelectorAll(".dialogue-card").forEach((card, i) => {
                card.classList.toggle("active", i === currentDialogueIndex);
            });

            const activeCard = document.querySelector(".dialogue-card.active");
            if (activeCard) {
                activeCard.scrollIntoView({ behavior: "smooth", block: "center" });
            }
        }

        const playIconSvg = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
        const pauseIconSvg = '<svg viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';

        function togglePlay() {
            if (isPlaying) {
                stop();
            } else {
                isPlaying = true;
                playBtn.innerHTML = pauseIconSvg;
                playCurrentDialogue();
            }
        }

        function stop() {
            isPlaying = false;
            audioPlayer.pause();
            audioPlayer.currentTime = 0;
            playBtn.innerHTML = playIconSvg;
            waitIndicator.classList.remove("visible");
            updateStatus();
        }

        function playCurrentDialogue() {
            const scene = getCurrentScene();
            const dialogue = scene.dialogues[currentDialogueIndex];

            highlightCurrent();

            const isMuted = dialogue.character.toLowerCase() === rehearseCharacter.toLowerCase();

            if (isMuted) {
                // Show wait indicator and wait for user to tap next or timeout
                waitIndicator.classList.add("visible");
                statusBar.textContent = `À vous : ${dialogue.character}`;

                // Auto-advance after a pause (3 seconds per line of text, min 3s)
                const waitTime = Math.max(3000, dialogue.text.length * 80);
                setTimeout(() => {
                    if (isPlaying && currentDialogueIndex === scene.dialogues.indexOf(dialogue)) {
                        waitIndicator.classList.remove("visible");
                        advanceDialogue();
                    }
                }, waitTime);
            } else {
                waitIndicator.classList.remove("visible");
                statusBar.textContent = `En cours : ${dialogue.character}`;
                audioPlayer.src = dialogue.audio;
                audioPlayer.play().catch(e => {
                    console.error("Audio play error:", e);
                    statusBar.textContent = "Appuyez pour activer l'audio";
                });
            }

            updateProgress();
        }

        function onAudioEnded() {
            if (isPlaying) {
                advanceDialogue();
            }
        }

        function advanceDialogue() {
            const scene = getCurrentScene();
            currentDialogueIndex++;

            if (currentDialogueIndex >= scene.dialogues.length) {
                if (isLooping) {
                    currentDialogueIndex = 0;
                    playCurrentDialogue();
                } else {
                    currentDialogueIndex = scene.dialogues.length - 1;
                    stop();
                    statusBar.textContent = "Scène terminée";
                }
            } else {
                playCurrentDialogue();
            }
        }

        function prevDialogue() {
            currentDialogueIndex = Math.max(0, currentDialogueIndex - 1);
            highlightCurrent();
            if (isPlaying) playCurrentDialogue();
            else updateStatus();
        }

        function nextDialogue() {
            const scene = getCurrentScene();
            waitIndicator.classList.remove("visible");
            if (currentDialogueIndex < scene.dialogues.length - 1) {
                currentDialogueIndex++;
                highlightCurrent();
                if (isPlaying) playCurrentDialogue();
                else updateStatus();
            } else if (isLooping) {
                currentDialogueIndex = 0;
                highlightCurrent();
                if (isPlaying) playCurrentDialogue();
                else updateStatus();
            }
        }

        function toggleLoop() {
            isLooping = !isLooping;
            loopBtn.classList.toggle("active", isLooping);
            loopIndicator.textContent = isLooping ? "Boucle activée" : "Boucle désactivée";
            loopIndicator.classList.toggle("active", isLooping);
        }

        function seekFromProgressBar(e) {
            const scene = getCurrentScene();
            const total = scene.dialogues.length;
            const rect = e.currentTarget.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const percentage = clickX / rect.width;
            const newIndex = Math.floor(percentage * total);

            currentDialogueIndex = Math.max(0, Math.min(newIndex, total - 1));
            waitIndicator.classList.remove("visible");
            highlightCurrent();
            updateProgress();

            if (isPlaying) {
                audioPlayer.pause();
                playCurrentDialogue();
            } else {
                updateStatus();
            }
        }

        function updateProgress() {
            const scene = getCurrentScene();
            const total = scene.dialogues.length;
            const progress = ((currentDialogueIndex + 1) / total) * 100;
            progressFill.style.width = progress + "%";
        }

        function updateStatus() {
            const scene = getCurrentScene();
            statusBar.textContent = `Réplique ${currentDialogueIndex + 1} sur ${scene.dialogues.length}`;
        }

        init();
    </script>
</body>
</html>
'''


def main():
    print("Loading drama...")
    drama = Drama.from_file(DRAMA_FILE)

    print("Generating drama data...")
    drama_data = generate_drama_data(drama, TTS_OUTPUT_DIR)

    print("Generating HTML...")
    html = HTML_TEMPLATE.replace("__DRAMA_DATA__", json.dumps(drama_data, ensure_ascii=False))

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Done! Open {OUTPUT_HTML} in a browser.")
    print(f"Characters: {', '.join(drama_data['characters'])}")
    print(f"Acts: {len(drama_data['acts'])}")


if __name__ == "__main__":
    main()