# Recovery Guide

How to restore Alyosha if the server dies.

---

## What You Need

1. **New server** (Ubuntu recommended, 2GB+ RAM)
2. **GitHub access** to clone the workspace
3. **API keys** (you'll need to re-enter these)

---

## Step-by-Step Recovery

### 1. Install OpenClaw

```bash
# Install Node.js (if not present)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install OpenClaw globally
npm install -g openclaw
```

### 2. Clone Workspace

```bash
mkdir -p ~/.openclaw
cd ~/.openclaw
git clone git@github.com:jonathanwxh-cell/alyosha-workspace.git workspace
```

### 3. Restore Config

The config file should be in the repo at `backups/openclaw.json`:

```bash
cp ~/.openclaw/workspace/backups/openclaw.json ~/.openclaw/openclaw.json
```

**If config is missing:** Run `openclaw init` and reconfigure manually.

### 4. Restore API Keys

Create the secure directory and add your keys:

```bash
mkdir -p ~/.secure
chmod 700 ~/.secure

# Create key files (get values from your password manager)
echo "YOUR_FMP_KEY" > ~/.secure/fmp.env
echo "YOUR_FINNHUB_KEY" > ~/.secure/finnhub.env
# ... etc

chmod 600 ~/.secure/*
```

**Keys needed:**
- `fmp.env` — Financial Modeling Prep
- `finnhub.env` — Finnhub
- (Check TOOLS.md for full list)

### 5. Start OpenClaw

```bash
openclaw gateway start
```

### 6. Verify

```bash
openclaw status
```

You should see the gateway running. Send a test message via Telegram.

---

## What's Preserved

| Component | Location | Backed Up |
|-----------|----------|-----------|
| Identity (SOUL.md, etc.) | workspace/ | ✅ GitHub |
| Memory | workspace/memory/ | ✅ GitHub |
| Scripts | workspace/scripts/ | ✅ GitHub |
| Config | backups/openclaw.json | ✅ GitHub |
| API Keys | ~/.secure/ | ❌ Manual |

---

## Backup Schedule

- **Workspace:** Auto-committed daily at 8pm SGT
- **Config:** Copied to `backups/` on changes

---

## If Something Goes Wrong

1. Check logs: `openclaw gateway logs`
2. Restart: `openclaw gateway restart`
3. Re-init if needed: `openclaw init`

---

*Last updated: 2026-02-04*
