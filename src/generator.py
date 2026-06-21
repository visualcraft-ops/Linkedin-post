"""LinkedIn Post Generator — Auto-generates and publishes viral-worthy content."""
import os
import json
import random
import hashlib
import requests
from datetime import datetime, date
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    genai = None

CONTENT_DIR = Path(__file__).parent.parent / "content"
GENERATED_DIR = CONTENT_DIR / "generated"
PUBLISHED_DIR = CONTENT_DIR / "published"
HISTORY_FILE = CONTENT_DIR / "history.json"

LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN")
LINKEDIN_VERSION = "202506"
POST_SESSION = os.environ.get("POST_SESSION", "morning")

# ============================================================
# CONTENT STRATEGY — Morning: Professional | Evening: Engaging
# ============================================================

MORNING_CALENDAR = {
    0: {"topic": "Visual Merchandising", "style": "actionable_tips"},
    1: {"topic": "HR & People Management", "style": "thought_leadership"},
    2: {"topic": "Store Operations", "style": "case_study"},
    3: {"topic": "Career & Leadership", "style": "personal_story"},
    4: {"topic": "Employee Engagement", "style": "framework"},
    5: {"topic": "Retail Strategy", "style": "contrarian_take"},
    6: {"topic": "Industry Trends", "style": "future_prediction"},
}

EVENING_CALENDAR = {
    0: {"topic": "Quick VM Tip", "style": "micro_content"},
    1: {"topic": "HR Hot Take", "style": "debate_starter"},
    2: {"topic": "Retail Life", "style": "relatable_story"},
    3: {"topic": "Career Advice", "style": "poll"},
    4: {"topic": "Team Culture", "style": "gratitude_post"},
    5: {"topic": "Weekend Wisdom", "style": "listicle"},
    6: {"topic": "Week Ahead", "style": "poll"},
}

# ============================================================
# VIRAL HOOKS — First 2 lines are everything on LinkedIn
# ============================================================

HOOKS = {
    "actionable_tips": [
        "Stop doing this with your store displays.\n\nI see it everywhere →",
        "3 VM changes that increased our footfall by 40%.\n\nNone of them cost money →",
        "Your mannequins are lying to customers.\n\nHere's what I mean →",
        "I set up 5 stores this year. Same mistake in all of them at first →",
        "The window display formula that works every single time →",
    ],
    "thought_leadership": [
        "HR in retail is broken.\n\nHere's what nobody wants to admit →",
        "We hire for experience. We should hire for energy.\n\nLet me explain →",
        "The real reason retail attrition is 60%+?\n\nIt's not the salary →",
        "I've onboarded 100+ retail staff. The ones who stayed all had ONE thing in common →",
        "Unpopular opinion: Most retail training programs are a waste of time.\n\nHere's why →",
    ],
    "case_study": [
        "Day 1 of a new store launch.\n\nEverything that can go wrong, did →",
        "We had 48 hours to redesign an entire store. Here's what happened →",
        "A ₹200 change in our display increased sales by 25%.\n\nThe story →",
        "The store was losing ₹3L/month. One operational change fixed it →",
        "I inherited a team that hated their jobs. 90 days later, zero attrition.\n\nHere's the playbook →",
    ],
    "personal_story": [
        "8 years ago, I was arranging mannequins.\n\nToday I build retail teams.\n\nHere's the messy middle →",
        "My worst day in retail taught me my best lesson →",
        "I almost quit retail in 2019.\n\nGlad I didn't. Here's what changed →",
        "Nobody in my family understood what 'Visual Merchandising' meant.\n\nNow they do →",
        "The feedback that changed my entire career trajectory →",
    ],
    "framework": [
        "My 3-step framework for building engaged retail teams:\n\n(Steal this) →",
        "The CARE framework I use for employee onboarding:\n\nC.A.R.E. →",
        "How I run a store launch in 30 days (step-by-step) →",
        "The 5-5-5 rule that keeps my team motivated:\n\n5 minutes, 5 words, 5 days →",
        "Want a high-performing store team? Use this matrix →",
    ],
    "contrarian_take": [
        "Hot take: Beautiful stores with bad teams will ALWAYS lose.\n\nFight me on this →",
        "Controversial: VM is not about making things 'look pretty'.\n\nIt's about →",
        "Everyone's obsessed with digital. I think physical retail will win.\n\nHere's my case →",
        "Stop blaming Gen Z for retail attrition.\n\nThe problem is YOUR onboarding →",
        "The 'customer is always right' is destroying retail teams.\n\nHere's a better approach →",
    ],
    "future_prediction": [
        "Retail in 2030 will look NOTHING like today.\n\n5 predictions →",
        "3 retail roles that won't exist in 5 years.\n\nAnd 3 new ones that will →",
        "AI is coming for VM. But not how you think →",
        "The future of HR in retail isn't human.\n\nOr is it? 🤔 →",
        "Physical stores aren't dying. They're evolving into something bigger →",
    ],
    "micro_content": [
        "Quick VM tip that takes 2 minutes ⚡\n\n→",
        "One thing I do every Monday that transforms the week →",
        "The smallest change with the biggest impact in any store →",
        "60-second store audit trick I use every single day →",
    ],
    "debate_starter": [
        "Agree or disagree?\n\n→",
        "I said this in a meeting and the room went silent →",
        "This might be my most controversial retail opinion →",
        "Tell me I'm wrong about this →",
    ],
    "relatable_story": [
        "Retail life. Nobody tells you about these moments →",
        "When the delivery arrives 30 mins before store opening 😅\n\nRetail people, you know →",
        "That moment when the customer asks for something you JUST moved from the display →",
        "Retail managers on a Monday vs Friday.\n\nA thread →",
    ],
    "gratitude_post": [
        "Shoutout to every retail team member who →",
        "The unsung heroes of retail are the people who →",
        "Something I don't say enough to my team →",
    ],
    "listicle": [
        "7 things I learned this week in retail →",
        "5 books that made me a better retail leader →",
        "4 habits of the best store managers I've worked with →",
    ],
    "poll": [],
}

# ============================================================
# POLL TEMPLATES
# ============================================================

POLL_TEMPLATES = [
    {
        "commentary": "Every retailer debates this. Let's settle it 👇\n\n#RetailStrategy #VisualMerchandising #StoreOperations",
        "question": "What drives more footfall to a store?",
        "options": ["Window displays", "Social media ads", "Word of mouth", "Location"],
    },
    {
        "commentary": "Honest answers only! 🙌\n\nWhat's YOUR biggest challenge in retail hiring?\n\n#HRCommunity #Recruitment #RetailHR",
        "question": "Biggest retail hiring challenge?",
        "options": ["High attrition", "Finding skilled staff", "Budget constraints", "Cultural fit"],
    },
    {
        "commentary": "Store launch veterans — what's your priority? 🎯\n\n#StoreOperations #RetailExcellence #NewStore",
        "question": "Most critical for store launch?",
        "options": ["Perfect displays", "Trained team", "Marketing buzz", "Inventory ready"],
    },
    {
        "commentary": "Career growth in retail looks different for everyone 🚀\n\n#CareerGrowth #RetailCareers #Leadership",
        "question": "Best skill for retail career growth?",
        "options": ["People management", "Visual merchandising", "Data analytics", "Customer empathy"],
    },
    {
        "commentary": "Low-budget engagement wins. What works best? 💡\n\n#EmployeeEngagement #TeamBuilding #WorkplaceCulture",
        "question": "What motivates retail teams most?",
        "options": ["Public recognition", "Growth opportunities", "Flexible hours", "Team outings"],
    },
    {
        "commentary": "VM people — this one's for you! 🎨\n\n#VisualMerchandising #RetailDisplay #VMTips",
        "question": "What stops a customer at a window?",
        "options": ["Bold lighting", "Minimalist design", "Storytelling", "Color contrast"],
    },
    {
        "commentary": "The future is coming fast 🚀 Where's your bet?\n\n#RetailTrends #FutureOfWork #Innovation",
        "question": "Which trend dominates retail next?",
        "options": ["AI-powered VM", "Experiential stores", "Sustainability", "Omnichannel"],
    },
    {
        "commentary": "First-week onboarding shapes everything 🎯\n\n#Onboarding #HRTips #EmployeeExperience",
        "question": "Most important in onboarding week 1?",
        "options": ["Buddy system", "Brand immersion", "Role clarity", "Team intros"],
    },
    {
        "commentary": "Monday morning debate for my retail network ☕\n\n#RetailLife #StoreManagement #RetailDebate",
        "question": "What makes a great store manager?",
        "options": ["Team builder", "Problem solver", "Customer-first", "Detail-oriented"],
    },
    {
        "commentary": "Settling this once and for all 🔥\n\n#VisualMerchandising #Retail #StoreDesign",
        "question": "More impact on store sales?",
        "options": ["Window display", "In-store layout", "Music & scent", "Staff energy"],
    },
]

# ============================================================
# HASHTAG BANK
# ============================================================

HASHTAGS = {
    "Visual Merchandising": ["#VisualMerchandising", "#RetailDisplay", "#StoreDesign", "#VMTips", "#WindowDisplay", "#RetailExperience", "#Merchandising"],
    "HR & People Management": ["#HumanResources", "#Recruitment", "#TalentAcquisition", "#PeopleFirst", "#HRTech", "#RetailHR", "#Hiring"],
    "Store Operations": ["#RetailOperations", "#StoreManagement", "#RetailExcellence", "#CustomerExperience", "#RetailStrategy", "#StoreLaunch"],
    "Career & Leadership": ["#Leadership", "#CareerGrowth", "#ProfessionalDevelopment", "#CareerAdvice", "#GrowthMindset", "#WomenInRetail"],
    "Employee Engagement": ["#EmployeeEngagement", "#WorkplaceCulture", "#TeamBuilding", "#EmployeeExperience", "#PeopleMatter", "#RetailTeams"],
    "Retail Strategy": ["#RetailStrategy", "#RetailInnovation", "#CustomerExperience", "#RetailGrowth", "#BrickAndMortar", "#RetailLeadership"],
    "Industry Trends": ["#FutureOfWork", "#RetailTrends", "#HRTrends", "#Innovation", "#DigitalTransformation", "#RetailTech"],
    "Quick VM Tip": ["#VMTips", "#VisualMerchandising", "#RetailHacks", "#StoreDisplay"],
    "HR Hot Take": ["#HRCommunity", "#RetailHR", "#TalentManagement", "#HotTake"],
    "Retail Life": ["#RetailLife", "#RetailProblems", "#StoreLife", "#RetailHumor"],
    "Career Advice": ["#CareerTips", "#RetailCareers", "#ProfessionalGrowth", "#Mentoring"],
    "Team Culture": ["#TeamCulture", "#WorkplaceWellbeing", "#RetailTeams", "#Gratitude"],
    "Weekend Wisdom": ["#WeekendWisdom", "#RetailLearnings", "#SaturdayThoughts", "#GrowthMindset"],
    "Week Ahead": ["#MondayMotivation", "#WeekAhead", "#RetailGoals", "#NewWeek"],
}


def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return {"posts": [], "hashes": []}


def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def get_today_config():
    day = date.today().weekday()
    if POST_SESSION == "evening":
        return EVENING_CALENDAR[day]
    return MORNING_CALENDAR[day]


def build_prompt(topic, style):
    hooks = HOOKS.get(style, HOOKS["actionable_tips"])
    hook = random.choice(hooks).replace("{topic}", topic.lower()) if hooks else ""
    hashtags = " ".join(random.sample(HASHTAGS.get(topic, HASHTAGS["Career & Leadership"]), min(4, len(HASHTAGS.get(topic, [])))))

    session_context = ""
    if POST_SESSION == "evening":
        session_context = """
- This is an EVENING post — make it lighter, more conversational, snackable
- Keep it under 150 words
- More personal, less preachy
- Can be slightly humorous or relatable"""
    else:
        session_context = """
- This is a MORNING post — professional, value-driven, actionable
- Length: 150-250 words (optimal for LinkedIn engagement)
- Focus on providing genuine value or sharing a real insight"""

    return f"""You are writing a LinkedIn post AS Preethi Prasanna — a professional with 8+ years in Visual Merchandising & Store Operations, now expanding into HR/People Management. She's worked on store launches, built teams from scratch, and managed VM for premium retail brands in India.

Write ONE LinkedIn post:
- Topic: {topic}
- Style: {style}
- Opening hook (use or adapt): "{hook}"
{session_context}

WRITING RULES:
- First 2 lines MUST create curiosity (this is what shows before "see more")
- Use line breaks aggressively (every 1-2 sentences)
- Short paragraphs, punchy sentences
- Include ONE specific number, example, or scenario from Indian retail
- End with a question that people WANT to answer in comments
- Add 4 relevant hashtags at the end: {hashtags}
- Use 2-3 emojis max (not every line)
- Write like a real person posting on their phone, not a corporate comms team

NEVER DO:
- Start with "I" as the very first word
- Use "In today's fast-paced world" or "Let me share" or "As professionals"
- Write generic advice without specifics
- Sound like ChatGPT (no "It's important to note", "Here's the thing", "At the end of the day")
- Use more than 250 words

VOICE: Confident but humble. Direct. Occasional humor. Real experiences > theory.

Output ONLY the post text. Nothing else."""


def generate_with_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    if not genai:
        raise ImportError("google-generativeai package not installed")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


def generate_fallback(topic, style):
    """Fallback templates when API unavailable."""
    templates = [
        f"Stop scrolling.\n\nIf you're in retail, this will save you hours.\n\nAfter 5+ store launches, here's my cheat sheet for {topic.lower()}:\n\n→ Start with your customer's eye level\n→ Change displays every 14 days (not when you feel like it)\n→ Train your team on WHY, not just HOW\n→ Measure footfall before/after every change\n\nThe stores that win aren't doing anything revolutionary.\nThey're doing the basics consistently.\n\nWhich one do you struggle with most? 👇\n\n#VisualMerchandising #RetailOperations #StoreManagement #RetailTips",
        f"The biggest myth in retail?\n\n'Good VM sells itself.'\n\nNo. Good VM + trained staff + right energy = sales.\n\nI've seen stores with stunning displays and zero conversions.\nI've seen stores with basic VM but incredible teams crushing targets.\n\nThe difference isn't the display.\nIt's the team behind it.\n\n{topic} is a team sport. Build accordingly.\n\nAgree? Disagree? Tell me 👇\n\n#RetailExcellence #TeamBuilding #VisualMerchandising #StoreOperations",
        f"Real talk about {topic.lower()}.\n\nNobody posts about the failures. So let me go first.\n\nI once spent 3 days perfecting a store display.\nCustomers walked past it without a second glance.\n\nThe fix? I asked a customer what they were looking for.\nRebuilt the display around THEIR journey in 2 hours.\n\nResult: 35% increase in dwell time.\n\nLesson: We design for Instagram. We should design for customers.\n\nWhat's a retail fail that taught you something? 👇\n\n#RetailLearning #VisualMerchandising #CustomerFirst #RetailTips",
        f"Coffee's ready ☕ Here's your Monday {topic.lower()} reminder:\n\n1. Your team mirrors your energy (check yours first)\n2. One small display change > zero changes while waiting for 'the big revamp'\n3. Ask your newest team member what confuses them (they see what you've normalized)\n4. Document what works (future you will thank present you)\n\nSimple? Yes.\nDoes everyone do it? No.\n\nThat's the edge.\n\nWhich one are you doing this week? 👇\n\n#RetailLeadership #StoreOperations #RetailTips #MondayMotivation",
        f"Quiet confession from 8 years in retail:\n\nThe best store I ever managed wasn't the most beautiful one.\n\nIt was the one where:\n→ Every team member greeted by name\n→ The stockroom was organized (not just the floor)\n→ We celebrated small wins loudly\n→ Training happened daily, not quarterly\n\nRetail success isn't a visual. It's a feeling.\n\nYour customers feel what your team feels.\n\nBuild the team first. The aesthetics follow.\n\nWhat made YOUR best store 'the best'? 👇\n\n#RetailExcellence #TeamCulture #StoreOperations #EmployeeEngagement",
    ]
    return random.choice(templates)


def is_duplicate(content, history):
    content_hash = hashlib.md5(content.encode()).hexdigest()
    return content_hash in history.get("hashes", [])


def save_post(content, topic, style):
    today = date.today().isoformat()
    session = f"_{POST_SESSION}" if POST_SESSION == "evening" else ""
    filename = f"{today}{session}_{topic.lower().replace(' & ', '-').replace(' ', '-')}.md"
    filepath = GENERATED_DIR / filename
    filepath.write_text(f"---\ndate: {today}\ntopic: {topic}\nstyle: {style}\nsession: {POST_SESSION}\n---\n\n{content}\n")
    return filepath


def get_person_id():
    r = requests.get("https://api.linkedin.com/v2/userinfo",
                     headers={"Authorization": f"Bearer {LINKEDIN_TOKEN}"}, timeout=30)
    if not r.ok:
        raise RuntimeError(f"Failed to get person ID: {r.status_code} {r.text}")
    return r.json()["sub"]


def publish_to_linkedin(content, poll_data=None):
    """Publish post or poll to LinkedIn. Returns post URN on success."""
    if not LINKEDIN_TOKEN:
        print("⚠️ LINKEDIN_TOKEN not set — skipping publish")
        return None

    try:
        person_id = get_person_id()
        headers = {
            "Authorization": f"Bearer {LINKEDIN_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": LINKEDIN_VERSION,
        }
        body = {
            "author": f"urn:li:person:{person_id}",
            "commentary": content,
            "visibility": "PUBLIC",
            "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        if poll_data:
            body["content"] = {
                "poll": {
                    "question": poll_data["question"][:140],
                    "options": [{"text": opt[:30]} for opt in poll_data["options"][:4]],
                    "settings": {"duration": "THREE_DAYS"},
                }
            }
        r = requests.post("https://api.linkedin.com/rest/posts",
                          headers=headers, json=body, timeout=30)
        if r.status_code == 401:
            print("❌ Token expired! Regenerate with get_token.py")
            return None
        if not r.ok:
            print(f"❌ Post failed: {r.status_code} {r.text}")
            return None
        post_urn = r.headers.get("x-restli-id", "")
        print(f"✅ Published {'poll' if poll_data else 'post'} to LinkedIn! URN: {post_urn}")
        return post_urn
    except Exception as e:
        print(f"❌ Publishing error: {e}")
        return None


def build_poll_prompt(topic):
    return f"""Generate a LinkedIn POLL for Preethi Prasanna (8+ years Visual Merchandising & Store Ops, expanding to HR).

Topic: {topic}

Requirements:
- Commentary: 2-3 punchy lines that make people WANT to vote. Include 3-4 hashtags.
- Question: max 140 chars, clear and debatable
- 4 options: max 30 chars each, all should feel like valid answers
- Make it relevant to Indian retail/HR professionals

Output EXACTLY as JSON (nothing else):
{{"commentary": "text with hashtags", "question": "question?", "options": ["A", "B", "C", "D"]}}"""


def generate_poll(topic):
    try:
        raw = generate_with_gemini(build_poll_prompt(topic))
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        poll = json.loads(raw)
        if "question" in poll and "options" in poll and len(poll["options"]) >= 2:
            print("✅ Poll generated with Gemini")
            return poll
    except Exception as e:
        print(f"⚠️ Gemini poll failed ({e}), using template")
    return random.choice(POLL_TEMPLATES)


# ============================================================
# SMART TAGGING — Mention relevant creators for visibility
# ============================================================

CREATOR_TAGS = {
    "Visual Merchandising": [
        "Retail design enthusiasts",
        "VM community",
        "Store designers and merchandisers",
    ],
    "HR & People Management": [
        "HR leaders in retail",
        "People-first leaders",
        "Talent acquisition community",
    ],
    "Store Operations": [
        "Retail ops professionals",
        "Store managers",
        "Retail leaders",
    ],
    "Career & Leadership": [
        "Career coaches",
        "Women in retail leadership",
        "Professional development community",
    ],
    "Employee Engagement": [
        "People & culture leaders",
        "Workplace culture advocates",
        "Employee experience community",
    ],
}


def add_engagement_tag(content, topic):
    """Add a subtle community callout to boost reach."""
    tags = CREATOR_TAGS.get(topic, CREATOR_TAGS.get("Career & Leadership", []))
    if tags and random.random() < 0.6:  # 60% of posts get a tag line
        tag = random.choice(tags)
        callouts = [
            f"\n\n🔔 {tag} — what's your take?",
            f"\n\nCalling all {tag.lower()} 👆",
            f"\n\n💬 {tag}, I'd love your perspective.",
        ]
        content += random.choice(callouts)
    return content


# ============================================================
# SELF-COMMENT BOOST — Algorithm hack
# ============================================================

BOOST_COMMENTS = [
    "Curious to hear from people who've been in retail 5+ years — has this changed for you?",
    "Also worth noting: this applies differently in tier-1 vs tier-2 cities. Would love to hear regional perspectives.",
    "For anyone starting in retail — bookmark this. I wish someone told me this on day 1.",
    "The responses here are gold 🙌 Keep them coming — learning from all of you.",
    "Follow-up thought: the best part about sharing here is realizing how many of us face the same challenges daily.",
    "Retail friends — tag someone who needs to see this today 👇",
    "This sparked a great conversation in my DMs too. If you want to discuss further, feel free to connect!",
    "Adding context: this is based on my experience in premium retail (Portico, lifestyle brands). May differ for value retail.",
    "Quick clarification from the comments — yes, this works for both large format and standalone stores.",
    "Loving the different perspectives here! The retail community on LinkedIn is genuinely one of the best 🙌",
]


def post_self_comment(post_urn):
    """Post a follow-up comment on own post to boost engagement."""
    if not LINKEDIN_TOKEN or not post_urn:
        return False

    try:
        import time
        time.sleep(30)  # Wait 30 seconds before commenting (looks natural)

        person_id = get_person_id()
        headers = {
            "Authorization": f"Bearer {LINKEDIN_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": LINKEDIN_VERSION,
        }

        comment_text = random.choice(BOOST_COMMENTS)
        body = {
            "actor": f"urn:li:person:{person_id}",
            "object": post_urn,
            "message": {"text": comment_text},
        }
        r = requests.post("https://api.linkedin.com/rest/socialActions/{}/comments".format(post_urn),
                          headers=headers, json=body, timeout=30)
        if r.ok or r.status_code == 201:
            print(f"💬 Self-comment posted: '{comment_text[:50]}...'")
            return True
        else:
            print(f"⚠️ Comment failed: {r.status_code} {r.text}")
            return False
    except Exception as e:
        print(f"⚠️ Comment error: {e}")
        return False


def main():
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

    history = load_history()
    config = get_today_config()
    topic = config["topic"]
    style = config["style"]

    print(f"{'🌅' if POST_SESSION == 'morning' else '🌙'} {POST_SESSION.upper()} | Topic: {topic} | Style: {style}")

    is_poll = (style == "poll")

    if is_poll:
        print("📊 Generating LinkedIn POLL")
        poll_data = generate_poll(topic)
        content = poll_data.get("commentary", "Share your thoughts! 👇")
        filepath = save_post(content + f"\n\n[POLL: {poll_data['question']}]\n{chr(10).join(poll_data['options'])}", topic, "poll")
        post_urn = publish_to_linkedin(content, poll_data)
    else:
        try:
            content = generate_with_gemini(build_prompt(topic, style))
            print("✅ Generated with Gemini")
        except Exception as e:
            print(f"⚠️ Gemini unavailable ({e}), using fallback")
            content = generate_fallback(topic, style)

        if is_duplicate(content, history):
            print("🔄 Duplicate detected, using fallback")
            content = generate_fallback(topic, style)

        # Add smart community tag
        content = add_engagement_tag(content, topic)

        filepath = save_post(content, topic, style)
        post_urn = publish_to_linkedin(content)
        poll_data = None

    # Self-comment boost (only on morning posts, 70% of the time)
    if post_urn and POST_SESSION == "morning" and random.random() < 0.7:
        print("💬 Adding self-comment boost...")
        post_self_comment(post_urn)

    # Update history
    published = post_urn is not None
    history["posts"].append({
        "date": date.today().isoformat(),
        "session": POST_SESSION,
        "topic": topic,
        "style": style,
        "file": filepath.name,
        "hash": hashlib.md5(content.encode()).hexdigest(),
        "published": published,
        "post_urn": post_urn or "",
        "type": "poll" if is_poll else "text",
    })
    history["hashes"].append(hashlib.md5(content.encode()).hexdigest())
    save_history(history)

    print(f"\n{'='*50}\n📝 {'POLL' if is_poll else 'POST'}:\n{'='*50}")
    print(content)
    if is_poll:
        print(f"\n📊 {poll_data['question']}")
        for i, opt in enumerate(poll_data['options'], 1):
            print(f"   {i}. {opt}")
    print("=" * 50)


if __name__ == "__main__":
    main()
