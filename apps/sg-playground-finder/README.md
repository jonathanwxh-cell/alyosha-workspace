# 🎠 SG Playground Finder

**Find the perfect playground for your little ones in Singapore**

## ✨ Features

- **Interactive Map** — All 25+ playgrounds on a Leaflet map
- **Filter by Feature** — Water play, slides, high-element, nature, themed, etc.
- **Smart Cards** — Age range, opening hours, highlights
- **Click to Focus** — Tap a card to zoom to playground on map
- **Mobile Responsive** — Works on phones and tablets

## 🚀 Quick Start

```bash
cd apps/sg-playground-finder
python3 server.py
# Opens at http://localhost:8082
```

Or use any static server:
```bash
cd public
npx serve
```

## 📊 Current Data

- **25 playgrounds** curated from top parent blogs
- Regions: North, South, East, West, Central, North-East
- Features tracked: slides, water-play, high-element, nature, themed, etc.

## 🗺️ Tech Stack

- **Frontend**: Vanilla HTML/CSS/JS
- **Map**: Leaflet.js (free, no API key)
- **Data**: JSON (easy to extend)

## 📝 Next Steps

1. [ ] Add more playgrounds (goal: 100+)
2. [ ] Integrate Instagram photos via Apify
3. [ ] Add Google Maps reviews
4. [ ] TikTok video embeds
5. [ ] User reviews/ratings
6. [ ] Deploy to Vercel/Render

## 📁 Structure

```
sg-playground-finder/
├── data/
│   └── playgrounds.json    # Playground database
├── public/
│   ├── index.html          # Main app
│   └── data/
│       └── playgrounds.json
├── server.py               # Simple Python server
└── README.md
```

## 🎯 Differentiation Strategy

This app focuses on **social media integration** — the gap in existing solutions like LetzGoPlay:
- Instagram photo feeds per playground
- TikTok video reviews
- Aggregated Google Maps reviews
- "Trending this week" based on social mentions

---

*Built by Alyosha 🕯️ for Jon*
