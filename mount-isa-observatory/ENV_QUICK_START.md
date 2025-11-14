# .env Quick Start - TL;DR

**You want world-class .env management that doesn't fuck around. Here's how.**

---

## ⚡ 30-Second Setup

```bash
cd mount-isa-observatory

# Option 1: Let the script handle it (recommended)
./scripts/setup-env.sh

# Option 2: DIY
cp .env.example .env
chmod 600 .env
nano .env  # Add your keys
```

**That's it.** Your `.env` is now:
- ✅ Protected from git commits
- ✅ Secure permissions (600)
- ✅ Won't get overwritten

---

## 🔐 What's Already Set

Your `.env` has this **confirmed working key**:
```bash
ABN_LOOKUP_GUID=e3df2bb0-a40b-40f9-b771-0cef7e9d667b
```

**You can start scraping data immediately.** No other keys required.

---

## 🎯 File Priority (What Beats What)

```
.env.local  >  .env  >  .env.example
(highest)              (lowest)
```

**For local testing**: Create `.env.local` and put overrides there. Never touch `.env` for temp changes.

---

## 🚀 Auto-Load (Optional but Sick)

Install direnv and never `source .env` again:

```bash
# macOS
brew install direnv
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc

# Ubuntu
sudo apt install direnv
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc

# Enable for this project
cd mount-isa-observatory
direnv allow
```

Now env vars **auto-load** when you `cd` into the directory. Magic.

---

## ✅ Validate Your Setup

```bash
./scripts/validate-env.sh
```

Shows:
- ✅ What's configured
- ❌ What's missing
- ⚠️ What's optional

---

## 🔑 Add More Keys (When Ready)

**For AI chat features** (optional):

1. Find your old keys:
   - **Supabase**: https://app.supabase.com/ → Your Project → Settings → API
   - **OpenAI**: https://platform.openai.com/api-keys

2. Add to `.env`:
   ```bash
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJ...
   OPENAI_API_KEY=sk-...
   ```

3. Validate:
   ```bash
   ./scripts/validate-env.sh
   ```

See `API_KEYS_GUIDE.md` for detailed instructions.

---

## 🛡️ Protection Features

Your setup prevents fuckery:

| Problem | Solution |
|---------|----------|
| Git overwrites | `.gitignore` blocks all .env files |
| Accidental commits | Git won't track .env |
| Team conflicts | Use .env.local for local changes |
| Permission issues | Scripts enforce chmod 600 |
| Missing keys | Validation script catches it |

---

## 📚 Full Documentation

- **ENV_MANAGEMENT.md** - Complete best practices (direnv, secrets managers, CI/CD)
- **API_KEYS_GUIDE.md** - How to find/create all API keys
- **scripts/setup-env.sh** - Interactive setup script
- **scripts/validate-env.sh** - Validation tool

---

## 🎯 Common Commands

```bash
# Setup new .env (won't overwrite without asking)
./scripts/setup-env.sh

# Check configuration
./scripts/validate-env.sh

# Edit safely (with backup)
cp .env .env.backup && nano .env

# Use local overrides for testing
nano .env.local

# Run scrapers (works with just ABN GUID)
python3 scrapers/comprehensive_money_flow_scraper.py

# Enable AI chat (needs Supabase + OpenAI)
python3 scripts/chat_with_data.py
```

---

## ⚠️ If Shit Breaks

**Problem: .env got overwritten**
```bash
# Check for backups
ls -la .env.backup .env.bak .env.old

# Restore
cp .env.backup .env
```

**Problem: Keys not working**
```bash
# Validate config
./scripts/validate-env.sh

# Check for weird characters
cat -A .env | grep "OPENAI"

# Nuclear option: re-create
./scripts/setup-env.sh
```

**Problem: Permission denied**
```bash
chmod 600 .env
```

---

## 🎉 Summary

**What you have**:
- ✅ Production-grade .env protection
- ✅ Auto-loading with direnv (if installed)
- ✅ Local override support (.env.local)
- ✅ Validation scripts
- ✅ ABN GUID already working
- ✅ Protection against overwrites
- ✅ Secrets manager ready (1Password, Doppler, AWS, etc.)

**What works NOW**:
- All data scrapers
- Business lookups
- Media statements collection
- Contract data
- Everything except AI chat

**What needs keys**:
- AI chat interface (needs Supabase + OpenAI)

**You're set up like a pro. Go build. 🚀**
