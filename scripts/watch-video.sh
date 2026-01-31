#!/usr/bin/env bash
#
# watch-video.sh - Extract insights from videos
#
# Usage:
#   ./watch-video.sh <url> [--frames N] [--output FILE]
#
# Tries transcript first (cheap), falls back to frame extraction + vision.
#

set -euo pipefail

FRAMES=5
OUTPUT=""
URL=""
TRANSCRIPT_ONLY=false
FRAMES_ONLY=false
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

usage() {
  echo "Usage: $0 <video-url> [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --frames N        Number of frames to extract (default: 5)"
  echo "  --output FILE     Write output to file instead of stdout"
  echo "  --transcript-only Only fetch transcript, skip frame extraction on failure"
  echo "  --frames-only     Skip transcript, go straight to frame extraction"
  echo "  -h, --help        Show this help"
  echo ""
  echo "Examples:"
  echo "  $0 'https://youtube.com/watch?v=xxx'"
  echo "  $0 'https://youtube.com/watch?v=xxx' --transcript-only"
  echo "  $0 'https://youtube.com/watch?v=xxx' --frames 10"
  exit 0
}

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help) usage ;;
    --frames) FRAMES="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --transcript-only) TRANSCRIPT_ONLY=true; shift ;;
    --frames-only) FRAMES_ONLY=true; shift ;;
    -*) echo "Unknown option: $1"; usage ;;
    *) URL="$1"; shift ;;
  esac
done

[[ -z "$URL" ]] && { echo "Error: URL required"; usage; }
[[ "$TRANSCRIPT_ONLY" == true && "$FRAMES_ONLY" == true ]] && { echo "Error: Cannot use both --transcript-only and --frames-only"; exit 1; }

log() { echo "[watch-video] $*" >&2; }

# Extract video ID from YouTube URL
extract_youtube_id() {
  local url="$1"
  if [[ "$url" =~ youtube\.com/watch\?v=([a-zA-Z0-9_-]+) ]]; then
    echo "${BASH_REMATCH[1]}"
  elif [[ "$url" =~ youtu\.be/([a-zA-Z0-9_-]+) ]]; then
    echo "${BASH_REMATCH[1]}"
  elif [[ "$url" =~ youtube\.com/shorts/([a-zA-Z0-9_-]+) ]]; then
    echo "${BASH_REMATCH[1]}"
  fi
}

# Try to get YouTube transcript
get_youtube_transcript() {
  local video_id="$1"
  python3 << EOF
from youtube_transcript_api import YouTubeTranscriptApi
try:
    api = YouTubeTranscriptApi()
    transcript = api.fetch("$video_id")
    for snippet in transcript.snippets:
        print(snippet.text)
except Exception as e:
    import sys
    print(f"Transcript error: {e}", file=sys.stderr)
    sys.exit(1)
EOF
}

# Get video metadata (returns: title, duration, description as separate lines)
get_video_title() {
  yt-dlp --no-download --print "%(title)s" "$1" 2>/dev/null || echo "Unknown"
}
get_video_duration() {
  yt-dlp --no-download --print "%(duration)s" "$1" 2>/dev/null || echo "0"
}
get_video_desc() {
  yt-dlp --no-download --print "%(description).500s" "$1" 2>/dev/null || echo ""
}

# Download video for frame extraction
download_video() {
  local url="$1"
  local out="$2"
  log "Downloading video..."
  yt-dlp -f 'bestvideo[height<=720]+bestaudio/best[height<=720]/best' \
    --merge-output-format mp4 \
    -o "$out" \
    --no-playlist \
    --max-filesize 100M \
    "$url" 2>/dev/null
}

# Extract frames at intervals
extract_frames() {
  local video="$1"
  local outdir="$2"
  local n="$3"
  
  # Get duration
  local duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$video" 2>/dev/null | cut -d. -f1)
  [[ -z "$duration" || "$duration" == "N/A" ]] && duration=60
  
  local interval=$((duration / (n + 1)))
  [[ $interval -lt 1 ]] && interval=1
  
  log "Extracting $n frames from ${duration}s video (every ${interval}s)..."
  
  for i in $(seq 1 $n); do
    local ts=$((i * interval))
    local outfile="$outdir/frame_$(printf '%03d' $i).jpg"
    ffmpeg -ss "$ts" -i "$video" -vframes 1 -q:v 2 "$outfile" 2>/dev/null
  done
}

# Main
log "Processing: $URL"

# Get video info
TITLE=$(get_video_title "$URL")
DURATION=$(get_video_duration "$URL")
DESC=$(get_video_desc "$URL")
log "Title: $TITLE (${DURATION}s)"

result=""
result+="# Video Analysis\n\n"
result+="**Title:** $TITLE\n"
result+="**Duration:** ${DURATION}s\n"
result+="**URL:** $URL\n\n"

# Track what we got
GOT_TRANSCRIPT=false
MEDIA_LINES=""

# Try transcript first (unless --frames-only)
if [[ "$FRAMES_ONLY" != true ]]; then
  VIDEO_ID=$(extract_youtube_id "$URL")
  if [[ -n "$VIDEO_ID" ]]; then
    log "Attempting to fetch transcript..."
    if transcript=$(get_youtube_transcript "$VIDEO_ID" 2>/dev/null); then
      log "✅ Got transcript"
      result+="## Transcript\n\n"
      result+="$transcript\n"
      GOT_TRANSCRIPT=true
    else
      log "No transcript available"
    fi
  else
    log "Not a YouTube URL, skipping transcript"
  fi
fi

# Fall back to frame extraction if no transcript (unless --transcript-only)
if [[ "$GOT_TRANSCRIPT" != true && "$TRANSCRIPT_ONLY" != true ]]; then
  log "Falling back to frame extraction..."
  VIDEO_FILE="$TMPDIR/video.mp4"
  FRAMES_DIR="$TMPDIR/frames"
  mkdir -p "$FRAMES_DIR"
  
  if download_video "$URL" "$VIDEO_FILE"; then
    extract_frames "$VIDEO_FILE" "$FRAMES_DIR" "$FRAMES"
    
    result+="## Extracted Frames\n\n"
    result+="Extracted $FRAMES frames for visual analysis.\n\n"
    
    # Collect MEDIA lines (output separately at end)
    for f in "$FRAMES_DIR"/*.jpg; do
      [[ -f "$f" ]] && MEDIA_LINES+="MEDIA:$f"$'\n'
    done
  else
    result+="## Error\n\nFailed to download video for frame extraction.\n"
  fi
elif [[ "$GOT_TRANSCRIPT" != true && "$TRANSCRIPT_ONLY" == true ]]; then
  result+="## No Transcript\n\nTranscript not available and --transcript-only was set.\n"
fi

# Output description if available
if [[ -n "$DESC" && "$DESC" != "null" ]]; then
  result+="\n## Description\n\n$DESC\n"
fi

# Output MEDIA lines first (easier to parse)
[[ -n "$MEDIA_LINES" ]] && echo -n "$MEDIA_LINES"

# Output result
if [[ -n "$OUTPUT" ]]; then
  echo -e "$result" > "$OUTPUT"
  log "Output written to: $OUTPUT"
else
  echo -e "$result"
fi
