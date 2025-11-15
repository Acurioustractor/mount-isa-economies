# Environment Variable Management - Best Practices

**World-class, production-grade environment configuration for Mount Isa Economic Observatory**

---

## 🎯 Overview

This project uses a **multi-layered environment variable system** that prevents accidental overwrites, provides local overrides, and follows industry best practices.

---

## 📁 File Structure

| File | Purpose | Git Tracked? | Priority |
|------|---------|--------------|----------|
| `.env.example` | Template with placeholders | ✅ Yes | Lowest (fallback) |
| `.env` | Your main configuration | ❌ No | Medium |
| `.env.local` | Local overrides | ❌ No | Highest |
| `.envrc` | direnv auto-loader | ✅ Yes | - |

### Priority Order (highest wins):
```
.env.local > .env > .env.example
```

---

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Run setup script
./scripts/setup-env.sh

# Validate configuration
./scripts/validate-env.sh
```

### Option 2: Manual Setup

```bash
# Copy template
cp .env.example .env

# Set secure permissions
chmod 600 .env

# Edit with your credentials
nano .env

# Validate
./scripts/validate-env.sh
```

---

## 🔐 World-Class Features

### 1. Auto-Loading with direnv (Recommended)

**Install direnv** (one-time):
```bash
# macOS
brew install direnv

# Ubuntu/Debian
sudo apt install direnv

# Add to shell (~/.bashrc or ~/.zshrc)
eval "$(direnv hook bash)"  # for bash
eval "$(direnv hook zsh)"   # for zsh
```

**Enable for this project**:
```bash
cd mount-isa-observatory
direnv allow
```

Now environment variables **automatically load** when you `cd` into the directory!

### 2. Local Overrides with .env.local

Create `.env.local` for machine-specific overrides:

```bash
# .env.local - Never committed to git
# Overrides values in .env

# Use local database instead of Supabase
DB_HOST=localhost
DB_PASSWORD=my_local_password

# Use different OpenAI key for testing
OPENAI_API_KEY=sk-test-...
```

**Priority**: `.env.local` values always win over `.env`

### 3. Secrets Manager Integration (Enterprise)

For team/production environments, integrate with secrets managers:

#### Option A: 1Password CLI

```bash
# Install 1Password CLI
brew install --cask 1password-cli

# Store secrets
op item create --category=login \
  --title="Mount Isa Observatory - OpenAI" \
  credential=sk-...

# Add to .envrc (already has commented template)
export OPENAI_API_KEY=$(op read "op://Private/OpenAI/credential")
```

#### Option B: AWS Secrets Manager

```bash
# Store in AWS
aws secretsmanager create-secret \
  --name mount-isa/openai-key \
  --secret-string "sk-..."

# Retrieve in scripts
export OPENAI_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id mount-isa/openai-key \
  --query SecretString --output text)
```

#### Option C: Doppler (Modern SaaS)

```bash
# Install Doppler CLI
brew install dopplerhq/cli/doppler

# Setup project
doppler setup

# Secrets automatically sync to .env
```

### 4. Secure File Permissions

Your `.env` file is automatically protected:

```bash
chmod 600 .env  # Owner read/write only
```

**Verification**:
```bash
ls -la .env
# Should show: -rw-------  (600)
```

### 5. Validation on Every Run

Add to your scripts:

```python
# Python example
import os
import sys

def validate_env():
    required = ['ABN_LOOKUP_GUID']
    missing = [key for key in required if not os.getenv(key)]

    if missing:
        print(f"❌ ERROR: Missing required env vars: {missing}")
        print("   Run: ./scripts/validate-env.sh")
        sys.exit(1)

    print("✅ Environment validated")

# Run at script start
validate_env()
```

---

## 🛡️ Protection Against Overwrites

### How This Prevents Overwrites

1. **`.gitignore` protection**:
   - `.env` is never committed to git
   - Git operations won't overwrite it

2. **Setup script safety**:
   - `setup-env.sh` asks before overwriting existing `.env`
   - Creates from `.env.example`, not from remote

3. **Local overrides**:
   - Use `.env.local` for temporary changes
   - Your main `.env` stays stable

4. **Backup strategy** (recommended):
   ```bash
   # Automatic backup on edit
   alias edit-env='cp .env .env.backup && nano .env'

   # Or use version-controlled secrets (encrypted)
   # See "Advanced: Encrypted .env" section below
   ```

---

## 🎓 Best Practices

### ✅ DO

- **Use `.env.local` for local testing** - Never edit `.env` for temporary changes
- **Keep `.env.example` updated** - Add new variables with placeholder values
- **Set secure permissions** - Always `chmod 600 .env`
- **Validate before running** - Use `./scripts/validate-env.sh`
- **Backup your `.env`** - To password manager or encrypted storage
- **Use different keys for dev/prod** - Never use prod keys in development

### ❌ DON'T

- **Never commit `.env` to git** - Already protected by `.gitignore`
- **Never share `.env` in Slack/email** - Use secrets manager
- **Never use placeholder values** - Replace `your_key_here` with real keys
- **Never store secrets in scripts** - Always use environment variables
- **Never screenshot `.env`** - Secrets are visible

---

## 🔧 Advanced Setups

### 1. Multiple Environments

```bash
# Development
.env.development

# Staging
.env.staging

# Production
.env.production
```

Load based on environment:
```bash
# In your scripts
ENV=${NODE_ENV:-development}
source .env.$ENV
```

### 2. Encrypted .env Files

Use `git-crypt` or `sops` for team sharing:

```bash
# Install git-crypt
brew install git-crypt

# Initialize
git-crypt init

# Add to .gitattributes
echo ".env filter=git-crypt diff=git-crypt" >> .gitattributes

# Now .env is encrypted in git!
git add .env
git commit -m "Add encrypted .env"
```

### 3. Docker Integration

```dockerfile
# Dockerfile
ENV-FILE .env
```

```yaml
# docker-compose.yml
services:
  app:
    env_file:
      - .env
      - .env.local  # Optional overrides
```

### 4. CI/CD Integration

```yaml
# GitHub Actions
- name: Set up environment
  env:
    ABN_LOOKUP_GUID: ${{ secrets.ABN_LOOKUP_GUID }}
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
```

Store secrets in:
- GitHub Secrets
- GitLab CI/CD Variables
- AWS Parameter Store
- Azure Key Vault

---

## 🆘 Troubleshooting

### Problem: .env got overwritten

**Solution**:
```bash
# Check if backup exists
ls -la .env.backup .env.bak .env.old

# Restore from backup
cp .env.backup .env

# Or find in git history (if it was ever committed)
git log --all --full-history --source -- **/.env
```

### Problem: Environment variables not loading

**Solution**:
```bash
# 1. Check file exists
ls -la .env

# 2. Validate format (no spaces around =)
cat .env | grep "OPENAI_API_KEY"
# Should be: OPENAI_API_KEY=sk-...
# NOT: OPENAI_API_KEY = sk-...

# 3. Load manually
set -a
source .env
set +a

# 4. Verify
echo $ABN_LOOKUP_GUID
```

### Problem: Permission denied

**Solution**:
```bash
# Fix permissions
chmod 600 .env

# If still failing, check ownership
ls -la .env
chown $USER .env
```

### Problem: Keys not working after setup

**Solution**:
```bash
# Validate configuration
./scripts/validate-env.sh

# Check for invisible characters
cat -A .env | grep "OPENAI_API_KEY"
# Should not show ^M or other control characters

# Re-create clean file
./scripts/setup-env.sh
```

---

## 📊 Comparison: Different Approaches

| Approach | Security | Team Friendly | Auto-Load | Complexity |
|----------|----------|---------------|-----------|------------|
| **Basic .env** | ⭐⭐ | ⭐ | ❌ | ⭐ |
| **.env + direnv** | ⭐⭐⭐ | ⭐⭐ | ✅ | ⭐⭐ |
| **Secrets Manager** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐ |
| **Encrypted .env** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐ |

**Our Setup**: `.env + direnv + Local overrides`
- ⭐⭐⭐ Security (good for solo development)
- ⭐⭐⭐ Team friendly (with secrets manager integration)
- ✅ Auto-load (with direnv)
- ⭐⭐ Complexity (simple to set up)

---

## 📚 Additional Resources

### Official Documentation
- **direnv**: https://direnv.net/
- **python-dotenv**: https://pypi.org/project/python-dotenv/
- **1Password CLI**: https://developer.1password.com/docs/cli
- **Doppler**: https://docs.doppler.com/

### Security Best Practices
- **OWASP Secrets Management**: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- **12-Factor App**: https://12factor.net/config

### Tools
- **git-crypt**: Encrypt files in git repos
- **sops**: Secrets OPerationS (Mozilla)
- **Vault**: HashiCorp secrets manager
- **chamber**: AWS Parameter Store wrapper

---

## ✅ Current Status

Your setup includes:

| Feature | Status | Notes |
|---------|--------|-------|
| `.env.example` template | ✅ | Comprehensive template with all services |
| `.gitignore` protection | ✅ | All .env variants ignored |
| Setup script | ✅ | `./scripts/setup-env.sh` |
| Validation script | ✅ | `./scripts/validate-env.sh` |
| direnv config | ✅ | `.envrc` with priority loading |
| Secure permissions | ✅ | Scripts enforce chmod 600 |
| Local overrides | ✅ | `.env.local` support |
| API keys guide | ✅ | `API_KEYS_GUIDE.md` |

**You have world-class environment management! 🎉**

---

## 🎯 Recommended Workflow

### For Solo Development (Current)

```bash
# One-time setup
./scripts/setup-env.sh
direnv allow

# Daily use
cd mount-isa-observatory  # Variables auto-load
python3 scrapers/comprehensive_money_flow_scraper.py

# Before committing changes
./scripts/validate-env.sh
```

### For Team Development (Future)

```bash
# One-time setup
doppler setup  # or 1Password CLI
direnv allow

# Daily use
cd mount-isa-observatory
doppler run -- python3 scrapers/...

# Secrets stay in secrets manager, never in files
```

---

## 🚀 Next Steps

1. **Install direnv** (optional but recommended):
   ```bash
   brew install direnv
   # Add to shell config, then:
   direnv allow
   ```

2. **Run validation**:
   ```bash
   ./scripts/validate-env.sh
   ```

3. **Start scraping** (works with just ABN GUID):
   ```bash
   python3 scrapers/comprehensive_money_flow_scraper.py
   ```

4. **Add AI features** (when ready):
   - Find/create Supabase + OpenAI keys
   - Add to `.env`
   - Run `./scripts/validate-env.sh`
   - Enable AI chat: `python3 scripts/chat_with_data.py`

---

**Your environment is now protected, professional, and production-ready! 🔐**
