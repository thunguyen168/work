# 🚀 How to Deploy to Render

## Files to Add to Your GitHub Repository

Add these files to your `thunguyen168/work` repository:

1. `app.py` - The web application
2. `templates/index.html` - The webpage
3. `requirements.txt` - Replace your existing one with this version
4. `render.yaml` - Render configuration
5. `Procfile` - Start command
6. `runtime.txt` - Python version

---

## Step-by-Step Deployment Instructions

### Step 1: Add Files to GitHub

1. Go to your repository: https://github.com/thunguyen168/work
2. Upload the files I've provided (or copy/paste their contents)
3. Make sure `templates/index.html` is in a `templates` folder

### Step 2: Create a Render Account

1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with your GitHub account (easiest option)

### Step 3: Create a New Web Service

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub account if prompted
3. Find and select your repository: `thunguyen168/work`
4. Click **"Connect"**

### Step 4: Configure the Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `ai-foresight-scanner` (or any name you like) |
| **Region** | Choose closest to you |
| **Branch** | `claude/ai-trend-scraper-tool-PKuNV` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120` |

### Step 5: Add Your API Keys (Important!)

1. Scroll down to **"Environment Variables"**
2. Click **"Add Environment Variable"**
3. Add your keys:

   | Key | Value |
   |-----|-------|
   | `ANTHROPIC_API_KEY` | Your Anthropic key (sk-ant-...) |
   | `SERPER_API_KEY` | Your Serper key |

   *(Or use `BRAVE_API_KEY` if you have Brave instead of Serper)*

### Step 6: Deploy!

1. Click **"Create Web Service"**
2. Wait for the build (usually 2-5 minutes)
3. Once complete, Render gives you a URL like: `https://ai-foresight-scanner.onrender.com`

---

## 🎉 You're Done!

Visit your URL to use your AI Foresight Scanner!

---

## Troubleshooting

**Build fails?**
- Check that all files are in the right places
- Make sure `requirements.txt` is in the root folder

**App crashes?**
- Check that your API keys are set correctly in Render
- Look at the logs in Render dashboard

**Timeout errors?**
- The free tier has limits; scanning can take time
- Consider upgrading to a paid plan for longer timeouts

---

## Cost

- **Free tier**: Good for testing, has some limits
- **Paid**: Starts at $7/month for always-on service
