#!/bin/sh
# Enough Light: one command from source to finished film. Usage: sh build.sh   (LIB = the Lemo-Opuscar library)
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
LIB=${LIB:-/root/lemo-opuscar}
export LIB
[ -f "$LIB/core/render/video.mjs" ] || { echo "set LIB to the Lemo-Opuscar library folder"; exit 1; }
PY="$LIB/.venv/bin/python"
cd "$HERE"
[ -f paper.jpg ] || "$PY" paper.py
[ -f fonts.css ] || node fetch_fonts.mjs
[ -f voices/dur.json ] || "$PY" "$LIB/core/tts/tts.py" lines.json voices
cd "$LIB"
node core/render/events.mjs "$HERE"
node core/render/video.mjs "$HERE" --fps 60 --workers 4 --out "$HERE/out/video.mp4"
"$PY" "$HERE/mix.py"
"$PY" -c "import json,sys; e=json.load(open(sys.argv[1]))['ev']; json.dump([{'t0':x['t0'],'t1':x['t1'],'text':x['text']} for x in e if x['type']=='sub'], open(sys.argv[2],'w'))" "$HERE/events.json" "$HERE/out/cues.json"
"$PY" core/render/srt.py "$HERE/out/cues.json" "$HERE/enough-light.srt"
sh core/render/mux.sh "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/enough-light.mp4" 60
node core/render/still.mjs "$HERE" 29.6 --prefix poster_ --out "$HERE/out"
cp "$HERE/out/poster_29.6.jpg" "$HERE/poster.jpg"
echo "done: $HERE/enough-light.mp4"
