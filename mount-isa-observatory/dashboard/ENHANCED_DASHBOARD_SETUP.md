# Enhanced Dashboard Setup Guide

## 🎉 What's New?

The enhanced dashboard is a **world-class upgrade** with:

### ✨ Key Features

1. **Real-Time Data** - Direct connection to Supabase (no manual updates!)
2. **Search & Filters** - Find any program, community, or category instantly
3. **Multiple Sort Options** - View by total $, per capita, program count, name
4. **Share Buttons** - Tweet, copy link, export CSV
5. **Responsive Design** - Perfect on desktop, tablet, and mobile
6. **Modern UI** - Dark theme, smooth animations, professional design
7. **Interactive Charts** - Hover for details, click for more

---

## 🚀 Quick Setup (2 Minutes)

### Step 1: Get Supabase Credentials

1. Go to your Supabase project: https://app.supabase.com
2. Click on your project
3. Go to **Settings** → **API**
4. Copy these two values:
   - **URL** (under "Project URL")
   - **anon/public key** (under "Project API keys")

### Step 2: Configure Dashboard

1. Open `dashboard/enhanced-dashboard.html` in a text editor
2. Find lines 615-616 (near the top of the `<script>` section):

```javascript
const SUPABASE_URL = 'YOUR_SUPABASE_URL';  // Replace with your URL
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY';  // Replace with your anon key
```

3. Replace with your actual values:

```javascript
const SUPABASE_URL = 'https://your-project.supabase.co';
const SUPABASE_ANON_KEY = 'your-actual-anon-key-here';
```

4. Save the file

### Step 3: Open Dashboard

```bash
# Mac
open dashboard/enhanced-dashboard.html

# Linux
xdg-open dashboard/enhanced-dashboard.html

# Windows
start dashboard/enhanced-dashboard.html
```

**That's it!** Your dashboard is now live with real-time data! 🎊

---

## 🔒 Security Note

**The anon key is SAFE to use in the browser** - it's designed for public access and Supabase has Row Level Security (RLS) to protect your data. The anon key can only:
- ✅ Read public data
- ❌ NOT modify data (unless you explicitly allow it)
- ❌ NOT access restricted data

If you want extra security, you can enable RLS policies in Supabase.

---

## 📊 Dashboard Features Guide

### Search

Type anything in the search box:
- Community name: "Mount Isa"
- Program name: "headspace"
- Category: "Education"

Results update instantly as you type!

### Filters

**Filter by Community:**
- Select one community to see only its data
- Combines with search and category filters

**Filter by Category:**
- View only programs in a specific category
- Great for comparing education vs mental health vs safety

**Sort Options:**
- **Total Funding** - See who gets the most money
- **Per Capita** - Fair comparison accounting for population
- **Program Count** - Number of programs per community
- **Name** - Alphabetical order

### Actions

**Export Data**
- Downloads CSV file with all visible data
- Open in Excel, Google Sheets, or any spreadsheet app
- Perfect for further analysis

**Share on Twitter**
- Pre-populated tweet with key statistics
- One click to share findings

**Copy Link**
- Copy current URL to clipboard
- Share with colleagues, council members, media

### Charts

**Top Communities by Total Funding**
- Bar chart showing highest funded communities
- Mount Isa highlighted in purple
- Hover for exact amounts

**Per Capita Funding Comparison**
- Horizontal bar chart
- Shows funding adjusted for population
- Mount Isa leads here!

### Community Cards

Click any community card to:
- See detailed breakdown (coming in Phase 2!)
- Currently shows alert with summary

Cards show:
- Total funding
- Per capita amount
- Number of programs
- Population
- Top 5 categories
- Mount Isa has special "#1 Per Capita" badge

---

## 🎨 Customization

### Change Colors

Edit the CSS variables in the `<style>` section:

```css
:root {
    --primary: #9333ea;        /* Main purple color */
    --primary-dark: #7e22ce;   /* Darker purple */
    --primary-light: #a78bfa;  /* Lighter purple */
    --bg-dark: #0f172a;        /* Background dark */
    --bg-card: #1e293b;        /* Card background */
}
```

Try different colors:
- Blue: `#3b82f6`
- Green: `#10b981`
- Red: `#ef4444`
- Orange: `#f59e0b`

### Add Your Branding

Around line 39, add your logo:

```html
<header>
    <div class="header-content">
        <img src="your-logo.png" alt="Logo" style="height: 50px; margin-bottom: 1rem;">
        <h1>Queensland Youth Funding Observatory</h1>
        ...
    </div>
</header>
```

### Change Title

Line 6:

```html
<title>Your Custom Title Here</title>
```

---

## 🌐 Hosting Options

### Option 1: GitHub Pages (Free)

1. Commit the dashboard to Git
2. Push to GitHub
3. Go to repository Settings → Pages
4. Select branch and `/dashboard` folder
5. Your dashboard will be at: `https://yourusername.github.io/repo-name/enhanced-dashboard.html`

### Option 2: Vercel (Free, Fastest)

1. Install Vercel CLI: `npm install -g vercel`
2. In dashboard folder: `vercel`
3. Follow prompts
4. Get instant URL: `https://your-project.vercel.app`

### Option 3: Netlify (Free, Easy)

1. Drag and drop `dashboard` folder to https://app.netlify.com/drop
2. Get instant URL
3. Optional: Add custom domain

### Option 4: Local Network (For Presentations)

```bash
# Start simple web server
cd dashboard
python3 -m http.server 8000

# Access from any device on same network
# http://YOUR-IP:8000/enhanced-dashboard.html
```

---

## 🐛 Troubleshooting

### "Supabase Not Configured" Error

**Problem:** Dashboard shows warning about Supabase credentials

**Solution:**
1. Check you updated BOTH `SUPABASE_URL` and `SUPABASE_ANON_KEY`
2. Make sure you didn't leave the placeholder text
3. Verify there are no typos
4. Refresh the page after saving

### "Error Loading Data" Message

**Problem:** Dashboard can't fetch data from Supabase

**Solution:**
1. Check your internet connection
2. Verify Supabase project is active (not paused)
3. Check browser console (F12) for detailed error
4. Verify anon key has read permissions
5. Try regenerating API keys in Supabase

### Data Looks Wrong

**Problem:** Numbers don't match what you expect

**Solution:**
1. Run `python scripts/export_database_summary.py` to verify database totals
2. Check for duplicate programs in database
3. Verify programs have correct `locations_mentioned` array
4. Refresh Supabase browser cache: `Ctrl/Cmd + Shift + R`

### Charts Not Showing

**Problem:** Charts section is empty

**Solution:**
1. Make sure Chart.js loaded (check network tab in browser console)
2. Check for JavaScript errors in console (F12)
3. Verify there's data to display
4. Try hard refresh: `Ctrl/Cmd + Shift + R`

### Slow Performance

**Problem:** Dashboard loads slowly

**Solution:**
1. Check Supabase query performance in Supabase dashboard
2. Consider adding indexes to `locations_mentioned` column
3. Implement pagination if you have 1000+ programs
4. Host on fast CDN (Vercel, Netlify)

---

## 📈 Usage Statistics

Want to track how many people use your dashboard?

### Option 1: Plausible Analytics (Privacy-friendly)

```html
<!-- Add before </head> -->
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

Cost: $9/month, respects privacy, no cookies

### Option 2: Simple Counter

Use Supabase to track pageviews:

```javascript
// Add after fetchData() in initializeApp()
await supabase.from('pageviews').insert({
    page: 'enhanced-dashboard',
    timestamp: new Date().toISOString()
});
```

---

## 🎯 Next Steps

Once your enhanced dashboard is running:

1. **Share the link** with community stakeholders
2. **Gather feedback** on what features they want
3. **Add custom branding** (logo, colors, title)
4. **Host publicly** (GitHub Pages, Vercel, or Netlify)
5. **Embed on website** (iframe or widget)

### Ready for Phase 2?

When you're ready, we can add:
- **Interactive Map** of Queensland with funding overlay
- **Program Detail Pages** with full descriptions
- **Time Series Charts** showing funding over time
- **Comparison Tools** to compare 2+ communities
- **Download PDF Reports** with one click
- **Email Alerts** for new programs

---

## 💡 Pro Tips

### Tip 1: Create Saved Views

Bookmark URLs with filters applied:
```
enhanced-dashboard.html?community=Mount+Isa&category=Education
```

Share these links to show specific insights!

### Tip 2: Export for Presentations

1. Filter to show what you want
2. Take screenshot (Cmd/Ctrl + Shift + 4 on Mac)
3. Use in PowerPoint/Keynote
4. Or export CSV and create charts in Excel

### Tip 3: Mobile Demo

The dashboard works perfectly on mobile:
- Open on your phone for field demos
- Share link via SMS/WhatsApp
- Present on iPad at community meetings

### Tip 4: Custom Population Data

Update the POPULATION_DATA object (line 620) with 2024 census numbers when available:

```javascript
const POPULATION_DATA = {
    'Mount Isa': 18765,  // Updated 2024 figure
    // ... other communities
};
```

---

## ❓ Questions?

Check the code comments for detailed explanations, or review:
- **PLATFORM_ROADMAP.md** - Full feature roadmap
- **ANALYSIS_AND_REPORTING_GUIDE.md** - Data export guides
- **README_ADDITIONAL_LOADERS.md** - Data loading guides

---

## 🎉 You're Done!

You now have a **world-class data platform** that's:
- ✅ Real-time (no manual updates)
- ✅ Interactive (search, filter, sort)
- ✅ Shareable (social media, links, exports)
- ✅ Beautiful (modern UI, smooth animations)
- ✅ Professional (charts, stats, insights)

**Welcome to the future of open data! 🚀**
