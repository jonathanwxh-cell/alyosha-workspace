# Recovery Guide

How to restore Alyosha from scratch. Assumes zero technical knowledge.

---

## Overview

Alyosha runs on a cloud server. If that server dies, you need to:
1. Get a new server
2. Install the software
3. Restore the backup

**Time needed:** ~30-60 minutes

---

## Part 1: Get a Server

You need a Linux server in the cloud. Options:

### Option A: AWS (Amazon Web Services)
1. Go to https://aws.amazon.com
2. Create account (or sign in)
3. Search for "EC2" and click it
4. Click "Launch Instance"
5. Settings:
   - Name: `alyosha`
   - OS: Ubuntu 22.04 or 24.04
   - Instance type: `t3.small` (2GB RAM) or larger
   - Create a new key pair → download the `.pem` file (KEEP THIS SAFE)
   - Allow SSH traffic
6. Click "Launch Instance"
7. Note the Public IP address

### Option B: DigitalOcean (simpler)
1. Go to https://digitalocean.com
2. Create account
3. Click "Create" → "Droplets"
4. Choose Ubuntu 22.04 or 24.04
5. Plan: Basic, $6/month (1GB) or $12/month (2GB recommended)
6. Choose region closest to Singapore
7. Authentication: Password (simpler) or SSH key
8. Click "Create Droplet"
9. Note the IP address

### Option C: Any VPS Provider
Vultr, Linode, Hetzner all work. Just get Ubuntu 22.04+ with at least 1GB RAM.

---

## Part 2: Connect to Your Server

### On Mac/Linux:
Open Terminal and type:
```bash
ssh root@YOUR_IP_ADDRESS
```
Replace `YOUR_IP_ADDRESS` with the IP from Part 1.

If using AWS with a .pem file:
```bash
ssh -i /path/to/your-key.pem ubuntu@YOUR_IP_ADDRESS
```

### On Windows:
1. Download PuTTY: https://putty.org
2. Open PuTTY
3. Enter your IP address
4. Click "Open"
5. Login as `root` (or `ubuntu` for AWS)

**First time connecting?** Type `yes` when asked about fingerprint.

---

## Part 3: Create a User (if logged in as root)

Don't run everything as root. Create a user:

```bash
# Create user (replace 'ubuntu' with any name you want)
adduser ubuntu

# Give them admin powers
usermod -aG sudo ubuntu

# Switch to that user
su - ubuntu
```

---

## Part 4: Install Node.js

OpenClaw needs Node.js to run. Install it:

```bash
# Download and run the Node.js installer
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -

# Install Node.js
sudo apt-get install -y nodejs

# Verify it worked (should show v22.x.x)
node --version
```

---

## Part 5: Install Git

Git is needed to download the backup:

```bash
sudo apt-get install -y git
```

---

## Part 6: Install OpenClaw

```bash
# Create directory for global npm packages
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'

# Add to PATH (so you can run openclaw command)
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Install OpenClaw
npm install -g openclaw

# Verify it worked
openclaw --version
```

---

## Part 7: Set Up GitHub Access

You need to download the backup from GitHub.

### Option A: HTTPS (simpler, but asks for password)
Skip to Part 8 and use HTTPS URL.

### Option B: SSH Key (recommended, no password needed)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"
# Press Enter for all prompts (default location, no passphrase)

# Show your public key
cat ~/.ssh/id_ed25519.pub
```

Copy that entire line (starts with `ssh-ed25519`).

Then:
1. Go to https://github.com/settings/keys
2. Click "New SSH Key"
3. Paste the key
4. Click "Add SSH Key"

---

## Part 8: Download the Backup

```bash
# Create OpenClaw directory
mkdir -p ~/.openclaw

# Download workspace from GitHub
cd ~/.openclaw

# If using SSH (recommended):
git clone git@github.com:jonathanwxh-cell/alyosha-workspace.git workspace

# OR if using HTTPS:
git clone https://github.com/jonathanwxh-cell/alyosha-workspace.git workspace
```

---

## Part 9: Restore Config

```bash
# Copy the backed-up config
cp ~/.openclaw/workspace/backups/openclaw.json ~/.openclaw/openclaw.json
```

---

## Part 10: Set Up API Keys

API keys are NOT stored in the backup (for security). You need to re-enter them.

```bash
# Create secure directory
mkdir -p ~/.secure
chmod 700 ~/.secure
```

Now create each key file. Get the values from your password manager or the original service.

### Required Keys:

**Anthropic (Claude AI):**
```bash
nano ~/.secure/anthropic.env
# Paste: ANTHROPIC_API_KEY=sk-ant-xxxxx
# Press Ctrl+X, then Y, then Enter to save
```

**OpenAI:**
```bash
nano ~/.secure/openai.env
# Paste: OPENAI_API_KEY=sk-xxxxx
```

**Telegram Bot:**
```bash
nano ~/.secure/telegram.env
# Paste: TELEGRAM_BOT_TOKEN=xxxxx
```

**Financial Modeling Prep:**
```bash
nano ~/.secure/fmp.env
# Paste: FMP_API_KEY=xxxxx
```

After creating all key files:
```bash
chmod 600 ~/.secure/*
```

---

## Part 11: Initialize OpenClaw

```bash
openclaw init
```

This will ask you questions. Answer based on your setup:
- Anthropic API key: Enter it
- Telegram: Enter bot token and your user ID (421085848)
- etc.

---

## Part 12: Start OpenClaw

```bash
# Start the gateway
openclaw gateway start

# Check it's running
openclaw status
```

You should see "Gateway: running" or similar.

---

## Part 13: Test It

Send a message to your Telegram bot. If Alyosha responds, you're done! 🎉

---

## Troubleshooting

### "Command not found: openclaw"
```bash
source ~/.bashrc
```

### "Permission denied"
```bash
sudo chown -R $USER:$USER ~/.openclaw
```

### "Cannot connect to GitHub"
Check your SSH key is added to GitHub (Part 7).

### Gateway won't start
```bash
openclaw gateway logs
```
Look for error messages.

### Bot not responding
1. Check Telegram bot token is correct
2. Make sure you messaged the right bot
3. Check `openclaw status`

---

## What Gets Restored

| Component | Status |
|-----------|--------|
| ✅ Alyosha's personality (SOUL.md) | Restored from backup |
| ✅ All memories | Restored from backup |
| ✅ Scripts and tools | Restored from backup |
| ✅ Config settings | Restored from backup |
| ⚠️ API keys | Must re-enter manually |
| ⚠️ Cron jobs | Restored, but check they're running |

---

## Keep the Backup Updated

The backup auto-updates daily at 8pm SGT. But if you make important changes, you can manually backup:

```bash
cd ~/.openclaw/workspace
git add -A
git commit -m "Manual backup"
git push
```

---

## Emergency Contacts

- **OpenClaw Discord:** https://discord.com/invite/clawd
- **OpenClaw Docs:** https://docs.openclaw.ai
- **GitHub Issues:** https://github.com/openclaw/openclaw/issues

---

*Last updated: 2026-02-04*
