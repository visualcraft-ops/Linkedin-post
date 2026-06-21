# 🚀 LinkedIn Auto-Post Generator

<div align="center">

![GitHub Actions](https://img.shields.io/badge/Automation-GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)

**Automated LinkedIn content generator for Visual Merchandising & HR professionals**

</div>

---

## 📋 What It Does

- ✅ **Auto-generates** professional LinkedIn posts daily using AI
- ✅ **Content Calendar** — different topics each day of the week
- ✅ **Human-like tone** — no robotic AI-sounding content
- ✅ **Duplicate prevention** — tracks history to ensure unique posts
- ✅ **Fallback templates** — works even without API key
- ✅ **GitHub Actions** — fully automated, runs daily at 7 AM IST

---

## 📅 Content Calendar

| Day | Topic | Style |
|-----|-------|-------|
| Monday | Visual Merchandising | Tips & Best Practices |
| Tuesday | HR & Recruitment | Thought Leadership |
| Wednesday | Engagement | Poll / Question |
| Thursday | Store Operations | Case Study / Story |
| Friday | Career & Leadership | Personal Insight |
| Saturday | Employee Engagement | Quick Tip |
| Sunday | Industry Trends | Weekly Roundup |

---

## 🏗️ Project Structure

```
Linkedin-post/
├── .github/workflows/
│   └── generate-post.yml    # Daily automation
├── src/
│   └── generator.py         # Main content generator
├── content/
│   ├── generated/           # New posts (ready to publish)
│   ├── published/           # Archive
│   └── history.json         # Duplicate tracking
├── config.yaml              # Settings
├── requirements.txt
└── README.md
```

---

## ⚡ Setup Guide

### 1. Get Gemini API Key (Free)

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **"Create API Key"**
3. Copy the key

### 2. Add Secret to GitHub

1. Go to this repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Name: `GEMINI_API_KEY`
4. Value: Paste your API key
5. Click **Add secret**

### 3. Enable GitHub Actions

1. Go to **Actions** tab in this repo
2. Click **"I understand my workflows, go ahead and enable them"**
3. The workflow runs automatically daily at 7:00 AM IST

### 4. Manual Run (Optional)

1. Go to **Actions** → **Generate LinkedIn Post**
2. Click **"Run workflow"**
3. Optionally override the topic
4. Check the generated post in `content/generated/`

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

## 📝 How to Use Generated Posts

1. Check `content/generated/` folder daily
2. Copy the post content
3. Paste on LinkedIn → Publish
4. Move file to `content/published/` (auto-tracked)

---

## 🎯 Topics Covered

- Visual Merchandising & Display
- Store Operations & Launches
- HR & Talent Acquisition
- Employee Onboarding & Training
- Leadership & Career Growth
- Employee Engagement
- Retail Industry Trends
- Workplace Culture

---

## 💡 Future Roadmap

- [ ] LinkedIn API auto-publishing (Phase 2)
- [ ] Telegram/Email notifications for new posts
- [ ] Multi-model AI fallback (OpenAI, Claude)
- [ ] Engagement analytics tracking
- [ ] Image generation for posts

---

<div align="center">

**Built with ❤️ by [visualcraft-ops](https://github.com/visualcraft-ops)**

</div>
