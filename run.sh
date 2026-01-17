docker run --rm --gpus all \
  -e COQUI_TOS_AGREED=1 \
  -e PYTHONUNBUFFERED=1 \
  -v $PWD/tts-output-default:/root/tts-output-default \
  -v $PWD/tts-output-stable:/root/tts-output-stable \
  -v $PWD/tts-output-balanced:/root/tts-output-balanced \
  -v $PWD/tts-models-cache:/root/.local/share/tts \
  -v $PWD/vad-models-cache:/root/.cache/torch/hub \
  -v $PWD/generate_tts.py:/root/generate_tts.py \
  -v $PWD/drama.py:/root/drama.py \
  -v $PWD/full_drama.txt:/root/full_drama.txt \
  --entrypoint python3 \
  ghcr.io/coqui-ai/tts \
  -u /root/generate_tts.py