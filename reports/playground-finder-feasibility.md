# Singapore Playground Finder App — Feasibility Report

**Date:** 2026-01-31  
**Prepared by:** Alyosha 🕯️

---

## 📋 Executive Summary

**Verdict: FEASIBLE but COMPETITIVE**

A playground finder app for Singapore parents is technically feasible with readily available data sources. However, a strong incumbent exists (LetzGoPlay). Success would require differentiation through superior social media integration and UX.

---

## 🏆 Competitive Landscape

### Existing Competitor: LetzGoPlay
- **Website:** letzgoplay.com
- **Coverage:** 1,500+ playgrounds, 600+ with photos
- **Features:** Reviews, ratings, filters by area/age/features
- **Platform:** Mobile app + web
- **Moat:** First-mover, established user base, community contributions

### Other Apps (International)
- **PlayScout** (App Store) - US-focused, photo contributions
- **PlayGroundr** (App Store) - Family reviews, cleanliness ratings

### Gap Analysis
| Feature | LetzGoPlay | Opportunity |
|---------|------------|-------------|
| Basic info | ✅ Strong | — |
| Photos | ✅ 600+ | More coverage |
| Reviews | ✅ Yes | Better aggregation |
| **Instagram content** | ❌ No | ✅ **Big gap** |
| **TikTok videos** | ❌ No | ✅ **Big gap** |
| **Google Maps reviews** | ❌ Limited | ✅ **Gap** |
| Real-time crowd info | ❌ No | Possible differentiator |
| Parent community | Partial | Could be stronger |

---

## 📊 Data Sources Available

### 1. Government Data (Free)
| Source | What | API |
|--------|------|-----|
| data.gov.sg | Park facilities, locations | GeoJSON ✅ |
| NParks | Parks, amenities | GeoJSON ✅ |

**Note:** Contains park-level data but playground-specific data may need extraction from facility types.

### 2. Google Maps Platform (Paid)
| API | What | Pricing |
|-----|------|---------|
| Places API (New) | Locations, details, hours | $17/1000 requests |
| Reviews API | User reviews, ratings | Included |
| Photos API | User-uploaded photos | $7/1000 requests |

**Capability:** Search "playground" in an area → get all results with ratings, reviews, photos.

### 3. Social Media (via Apify — Jon has this)

#### Instagram
- **Apify Actor:** `apify/instagram-hashtag-scraper`
- **Hashtags to scrape:**
  - #singaporeplayground
  - #sgplayground
  - #playgroundsg
  - #kidssingapore
  - #sgmums #sgparents
- **Data:** Photos, captions, likes, comments, location tags
- **Cost:** ~$5/10,000 results

#### TikTok
- **Apify Actor:** `clockworks/tiktok-hashtag-scraper`
- **Hashtags:** #sgplayground #singaporekids #playgroundreview
- **Data:** Videos, views, likes, transcripts
- **Cost:** ~$5/10,000 results

### 4. Other Sources
- **Hardwarezone EDMW** — Parent discussions
- **Reddit r/singapore** — Playground recommendations
- **Mothership/Mustsharenews** — Playground features

---

## 🔧 Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Web/PWA)                      │
│  - Map view (Google Maps / Mapbox)                          │
│  - List view with filters                                   │
│  - Playground detail pages                                  │
│  - Social media feed integration                            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
│  - Python (Flask/FastAPI) or Node.js                        │
│  - PostgreSQL + PostGIS for geo queries                     │
│  - Redis for caching                                        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      DATA PIPELINE                           │
│  - Daily: Scrape Instagram/TikTok hashtags                  │
│  - Weekly: Refresh Google Maps data                         │
│  - Monthly: Sync with NParks data                           │
│  - AI: Sentiment analysis on reviews                        │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack Recommendation
| Component | Choice | Why |
|-----------|--------|-----|
| Frontend | Next.js + Tailwind | Fast, SEO-friendly |
| Backend | Python FastAPI | Quick to build, good for data |
| Database | Supabase (Postgres + PostGIS) | Free tier, geo-ready |
| Maps | Mapbox | Cheaper than Google, nice UX |
| Hosting | Vercel + Render | Free/cheap tiers |
| Scraping | Apify (already have) | Instagram/TikTok |

---

## 💰 Cost Estimate

### Development
| Phase | Time | Notes |
|-------|------|-------|
| MVP | 2-3 weeks | Basic map + 100 playgrounds |
| Beta | 2-3 months | Full features, 500+ playgrounds |
| Launch | Ongoing | Community building |

### Running Costs (Monthly)
| Item | Cost |
|------|------|
| Hosting (Vercel + Render) | $0-20 |
| Database (Supabase) | $0-25 |
| Google Maps API | $50-100 |
| Apify scraping | $20-50 |
| **Total** | **$70-195/mo** |

---

## 🎯 Differentiation Strategy

### Option A: "Social-First Playground Finder"
- **Hook:** "See what parents are ACTUALLY saying on Instagram and TikTok"
- **Differentiator:** Aggregate and display social media content that LetzGoPlay doesn't have
- **Features:**
  - Instagram photo feed for each playground
  - TikTok video reviews
  - "Trending this week" based on social mentions
  - Sentiment analysis ("87% positive vibes")

### Option B: "Real-Time Crowd Intelligence"
- **Hook:** "Is the playground crowded right now?"
- **Differentiator:** Use Google Popular Times + user check-ins
- **Features:**
  - Crowd level estimates
  - Best times to visit
  - "Live" updates from parents

### Option C: "The Premium Experience"
- **Hook:** "Curated, not just catalogued"
- **Differentiator:** Editorial content + AI summaries
- **Features:**
  - AI-generated "What parents love" summaries
  - Expert-curated "hidden gems" lists
  - Age-appropriate recommendations with reasoning

---

## ⚠️ Risks & Challenges

| Risk | Severity | Mitigation |
|------|----------|------------|
| LetzGoPlay dominance | High | Focus on social media differentiation |
| Data accuracy | Medium | Multiple source validation |
| Social API changes | Medium | Cache aggressively, diversify sources |
| User acquisition | High | SEO, content marketing, parent groups |
| Monetization unclear | Medium | Ads, sponsored listings, premium features |

---

## ✅ Recommendation

### GO — with conditions:

1. **Don't try to out-feature LetzGoPlay on basics.** They have 1,500+ playgrounds. Catching up is a grind.

2. **Win on social integration.** This is the clear gap. Parents LOVE seeing real Instagram/TikTok content. LetzGoPlay doesn't have this.

3. **Start with a focused MVP:**
   - 100-200 top playgrounds (curated, not comprehensive)
   - Instagram/TikTok feed for each
   - Google Maps reviews aggregated
   - Beautiful, fast UI

4. **Test demand before building:**
   - Create an Instagram account posting playground content
   - Build an audience first
   - Validate that parents want this

### MVP Scope (2-3 weeks)
- [ ] Scrape top 200 Singapore playgrounds from Google Maps
- [ ] Enrich with Instagram hashtag content
- [ ] Simple map UI with filtering
- [ ] Deploy on Vercel
- [ ] Share in parent Facebook groups for feedback

---

## 📎 Resources

- LetzGoPlay: https://letzgoplay.com
- NParks Data: https://data.gov.sg/datasets/d_14d807e20158338fd578c2913953516e
- Google Places API: https://developers.google.com/maps/documentation/places
- Apify Instagram: https://apify.com/apify/instagram-hashtag-scraper
- Apify TikTok: https://apify.com/clockworks/tiktok-hashtag-scraper

---

*Report generated by Alyosha. Want me to start building the MVP?* 🕯️
