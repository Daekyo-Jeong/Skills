#!/usr/bin/env bash
# Install runtime deps for the instrumental-music skill (idempotent).
set -e
if [[ "$(uname)" == "Darwin" ]]; then
  command -v fluidsynth >/dev/null || brew install fluid-synth
  command -v ffmpeg >/dev/null || brew install ffmpeg
  SF=~/.claude/soundfonts/default.sf2
  if [[ ! -f $SF && -z "$MUSIC_SF2" ]]; then
    mkdir -p ~/.claude/soundfonts
    echo "No GM SoundFont found. Put one at $SF (e.g. FluidR3_GM.sf2 or GeneralUser GS) or export MUSIC_SF2=/path/to.sf2"
  fi
else
  if ! command -v fluidsynth >/dev/null || [[ ! -f /usr/share/sounds/sf2/FluidR3_GM.sf2 ]]; then
    sudo apt-get update -qq && sudo apt-get install -y -qq fluidsynth fluid-soundfont-gm ffmpeg
  fi
fi
python3 -m pip install -q numpy scipy pretty_midi pyloudnorm
echo "ok"
