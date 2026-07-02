# 🚀 LinkedIn Auto-Post Generator

<div align="center">

![GitHub Actions](https://img.shields.io/badge/Automation-GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)

**Automated LinkedIn content generator for Visual Merchandising & Vendor Management professionals**

</div>

---

## 📋 What It Does

- ✅ **Auto-generates** professional LinkedIn posts daily using AI
- ✅ **Content Calendar** — different VM & Vendor topics each day
- ✅ **Human-like tone** — no robotic AI-sounding content
- ✅ **Duplicate prevention** — tracks history to ensure unique posts
- ✅ **Fallback templates** — works even without API key
- ✅ **GitHub Actions** — fully automated, runs daily at 7 AM IST
- ✅ **Recruiter-attractive** — posts that showcase VM & Vendor expertise

---

## 📅 Content Calendar

| Day | Topic | Style |
|-----|-------|-------|
| Monday | Visual Merchandising | Tips & Best Practices |
| Tuesday | Vendor Management | Thought Leadership |
| Wednesday | Engagement | Poll / Question |
| Thursday | Store Operations & VM Execution | Case Study / Story |
| Friday | Retail Branding & Display Strategy | Personal Insight |
| Saturday | Vendor Negotiation & Sourcing | Quick Tip |
| Sunday | Industry Trends & VM Innovation | Weekly Roundup |

---

## 🏗️ Project Structure

```
Linkedin-post/
├── .github/workflows/
│   ├── generate-post.yml    # Morning post automation (7 AM IST)
│   ├── evening-post.yml     # Evening post automation (6 PM IST)
│   └── check-token.yml      # Weekly token health check
├── src/
│   └── generator.py         # Main content generator
├── content/
│   ├── generated/           # New posts (ready to publish)
│   ├── published/           # Archive
│   └── history.json         # Duplicate tracking
├── config.yaml              # Settings
├── get_token.py             # LinkedIn OAuth token generator
├── requirements.txt
└── README.md
```

---

## ⚡ Setup Guide

### 1. Get Gemini API Key (Free)
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **"Create API Key"**
3. Copy the key

### 2. Add Secrets to GitHub
1. Go to this repo → **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `GEMINI_API_KEY` — Google Gemini API key
   - `LINKEDIN_TOKEN` — LinkedIn access token (use `get_token.py`)
   - `LINKEDIN_CLIENT_ID` — LinkedIn app client ID
   - `LINKEDIN_CLIENT_SECRET` — LinkedIn app secret
   - `LINKEDIN_REFRESH_TOKEN` — For auto-refresh
   - `GH_PAT` — GitHub PAT for secret rotation

### 3. Enable GitHub Actions
1. Go to **Actions** tab in this repo
2. Click **"I understand my workflows, go ahead and enable them"**
3. The workflow runs automatically twice daily (7 AM + 6 PM IST)

### 4. Manual Run (Optional)
1. Go to **Actions** → **Generate LinkedIn Post**
2. Click **"Run workflow"**
3. Check the generated post in `content/generated/`

---

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
content:
  max_words: 250       # Post length
  tone: "professional" # professional, casual, inspirational
  emoji_level: "low"   # low, medium, high

ai:
  provider: "gemini"
  temperature: 0.8     # 0.0 = focused, 1.0 = creative
```

---

## 🎯 Topics Covered

- **Visual Merchandising** — display design, planograms, window setups, lighting, fixture strategy
- **Vendor Management** — vendor evaluation, relationship building, delivery coordination
- **Store Operations & VM Execution** — launch planning, execution frameworks, store setups
- **Retail Branding & Display** — brand experience, in-store marketing, signage strategy
- **Vendor Negotiation & Sourcing** — cost optimization, quality benchmarking, supplier partnerships
- **VM Trends & Innovation** — sustainable materials, retail tech, AI in VM, digital displays
- **Industry Trends** — future of retail, retail transformation, omnichannel experiences

---

## 💡 Why This Content Strategy?

This generator creates posts that:
1. **Showcase deep VM expertise** — practical tips recruiters recognize as real experience
2. **Demonstrate vendor management skills** — a high-demand skill in retail operations
3. **Build thought leadership** — positioning as a go-to voice in retail VM
4. **Attract recruiter attention** — consistent posting on niche topics gets profile views
5. **Drive engagement** — polls, questions, and relatable stories boost visibility

---

## 📝 How to Use Generated Posts
1. Check `content/generated/` folder daily
2. Posts auto-publish to LinkedIn (if token is configured)
3. Fallback: Copy post content → Paste on LinkedIn → Publish
4. History tracked in `content/history.json`

---

## 💡 Future Roadmap
- [ ] Multi-image carousel posts for VM before/after
- [ ] Telegram/Email notifications for new posts
- [ ] Engagement analytics tracking
- [ ] AI-generated VM display images
- [ ] LinkedIn newsletter integration

---

**Built with ❤️ by [visualcraft-ops](https://github.com/visualcraft-ops)**
