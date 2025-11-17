# Mac Setup Guide for Loading Data to Supabase

## Step 1: Create Virtual Environment

```bash
cd ~/mount-isa-economies/mount-isa-observatory

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

## Step 2: Install Dependencies

```bash
pip install python-dotenv supabase
```

## Step 3: Set Up .env File

Create your `.env` file:
```bash
nano .env
```

Add these lines (replace with your actual Supabase credentials):
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

## Step 4: Run the Loader

```bash
python scripts/load_comprehensive_funding.py
```

## Step 5: Deactivate Virtual Environment (When Done)

```bash
deactivate
```

---

## Future Use

Every time you want to run the script:

```bash
cd ~/mount-isa-economies/mount-isa-observatory
source venv/bin/activate
python scripts/load_comprehensive_funding.py
deactivate
```

---

## Quick One-Liner (After Initial Setup)

```bash
cd ~/mount-isa-economies/mount-isa-observatory && source venv/bin/activate && python scripts/load_comprehensive_funding.py && deactivate
```

---

## Troubleshooting

**"No such file or directory: .env"**
→ Make sure you created the `.env` file in the mount-isa-observatory directory

**"Missing Supabase credentials"**
→ Check your `.env` file has both:
  - SUPABASE_URL=...
  - SUPABASE_SERVICE_ROLE_KEY=...

**Still getting externally-managed-environment**
→ Make sure you activated the virtual environment: `source venv/bin/activate`
→ You should see `(venv)` in your prompt

---

## Alternative: Use Existing Virtual Environment

If you already have a virtual environment somewhere:

```bash
cd ~/mount-isa-economies/mount-isa-observatory
source /path/to/your/existing/venv/bin/activate
pip install python-dotenv supabase
python scripts/load_comprehensive_funding.py
```
