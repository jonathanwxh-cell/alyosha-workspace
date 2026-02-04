# TOOLS.md — Local Tool Notes

## Web / Search
- **Primary:** Brave Search (`web_search`) + `web_fetch`
- **Apify:** EXPENSIVE — last resort only

## Financial Data
- **FMP:** `scripts/fmp-client.py` (Ultimate tier, real-time quotes)
- **yfinance:** `scripts/stock-quote.py` (free backup)
- **Analysis:** `scripts/analyze-stock.py TICKER` (spawns Sonnet)
- **Full docs:** `docs/financial-tools-guide.md`

## Audio
- **TTS:** OpenAI tts-1, voice: nova — **$5/mo budget**, Jon prefers text
- **Whisper:** $10/mo budget, ~28 hrs/month
- **Format:** MP3 only (not OGG)

## Key Scripts
| Script | Purpose |
|--------|---------|
| `turn-cost.py` | Per-turn cost estimate |
| `real-cost-tracker.py` | Daily cost from sessions |
| `session-rotation.py` | Context % check |
| `thesis-tracker.py` | Investment thesis tracking |
| `position-tracker.py` | Open position alerts |
| `fmp-client.py` | Stock quotes/metrics |

## Moltbook
- Profile: AlyoshaSG (pending claim)
- Skill: `skills/moltbook/`

## Security
- fail2ban active on SSH
- Monthly audit cron (1st of month)
- `scripts/secure-serve.sh` for temp hosting

---
*Detailed tool docs: `docs/tools-reference.md`*
