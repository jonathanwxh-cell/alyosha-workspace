# Podcast Transcription Flow

**Date:** 2026-02-04
**Tool:** OpenAI Whisper API (skill: openai-whisper-api)
**Budget:** $10/month (~28 hours of audio)

## Pricing Reference
- Whisper API: $0.006/min
- 1-hour podcast: ~$0.36
- 4-hour podcast: ~$1.44

## The Flow

### 1. Find Podcast
- RSS feeds, YouTube, Spotify links
- Prioritize: Lex Fridman, Dwarkesh, podcasts with investment angles

### 2. Download Audio
```bash
# YouTube
yt-dlp -x --audio-format mp3 "URL"

# Direct MP3
curl -O "URL"
```

### 3. Transcribe via Whisper
```bash
# Using the skill
python3 scripts/whisper-transcribe.py input.mp3 -o transcript.txt
```

### 4. Analyze
- Read full transcript
- Extract key insights
- Form opinions
- Find cross-domain connections
- Investment angles where relevant

### 5. Surface to Jon
Format:
```
🎙️ **Podcast: [Title]**
Guest: [Name]
Duration: [X hrs]

**Key Insights:**
• [Insight 1]
• [Insight 2]

**My Take:** [Opinion + connections]

**Investment Angle:** [If any]
```

## Use Cases
- Lex Fridman interviews (AI researchers, scientists)
- Dwarkesh Patel (deep tech, history)
- Invest Like the Best (finance)
- EconTalk (economics)
- Any podcast Jon shares

## When to Use
✓ Jon shares a specific episode
✓ High-signal guest (AI researchers, founders, scientists)
✓ Cross-domain topics that connect to interests

## When to Skip
✗ Generic news podcasts (better to read)
✗ Entertainment-only content
✗ Very long series (pick highlights)

---
*Cost-effective way to consume audio content and surface insights*
