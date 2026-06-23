"""LinkedIn Post Generator — Auto-generates and publishes viral-worthy content."""
import os
import json
import random
import hashlib
import time
import requests
from datetime import datetime, date
from pathlib import Path

try:
    from google import genai
except ImportError:
    genai = None

CONTENT_DIR = Path(__file__).parent.parent / "content"
GENERATED_DIR = CONTENT_DIR / "generated"
PUBLISHED_DIR = CONTENT_DIR / "published"
HISTORY_FILE = CONTENT_DIR / "history.json"

LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN")
LINKEDIN_VERSION = "202606"
POST_SESSION = os.environ.get("POST_SESSION", "morning")

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


POLL_TEMPLATES = [
    {"commentary": "Every retailer debates this. Let's settle it 👇\n\n#RetailStrategy #VisualMerchandising #StoreOperations", "question": "What drives more footfall to a store?", "options": ["Window displays", "Social media ads", "Word of mouth", "Location"]},
    {"commentary": "Honest answers only! 🙌\n\nWhat's YOUR biggest challenge in retail hiring?\n\n#HRCommunity #Recruitment #RetailHR", "question": "Biggest retail hiring challenge?", "options": ["High attrition", "Finding skilled staff", "Budget constraints", "Cultural fit"]},
    {"commentary": "Store launch veterans — what's your priority? 🎯\n\n#StoreOperations #RetailExcellence #NewStore", "question": "Most critical for store launch?", "options": ["Perfect displays", "Trained team", "Marketing buzz", "Inventory ready"]},
    {"commentary": "Career growth in retail looks different for everyone 🚀\n\n#CareerGrowth #RetailCareers #Leadership", "question": "Best skill for retail career growth?", "options": ["People management", "Visual merchandising", "Data analytics", "Customer empathy"]},
    {"commentary": "Low-budget engagement wins. What works best? 💡\n\n#EmployeeEngagement #TeamBuilding #WorkplaceCulture", "question": "What motivates retail teams most?", "options": ["Public recognition", "Growth opportunities", "Flexible hours", "Team outings"]},
    {"commentary": "VM people — this one's for you! 🎨\n\n#VisualMerchandising #RetailDisplay #VMTips", "question": "What stops a customer at a window?", "options": ["Bold lighting", "Minimalist design", "Storytelling", "Color contrast"]},
    {"commentary": "The future is coming fast 🚀 Where's your bet?\n\n#RetailTrends #FutureOfWork #Innovation", "question": "Which trend dominates retail next?", "options": ["AI-powered VM", "Experiential stores", "Sustainability", "Omnichannel"]},
    {"commentary": "First-week onboarding shapes everything 🎯\n\n#Onboarding #HRTips #EmployeeExperience", "question": "Most important in onboarding week 1?", "options": ["Buddy system", "Brand immersion", "Role clarity", "Team intros"]},
    {"commentary": "Monday morning debate for my retail network ☕\n\n#RetailLife #StoreManagement #RetailDebate", "question": "What makes a great store manager?", "options": ["Team builder", "Problem solver", "Customer-first", "Detail-oriented"]},
    {"commentary": "Settling this once and for all 🔥\n\n#VisualMerchandising #Retail #StoreDesign", "question": "More impact on store sales?", "options": ["Window display", "In-store layout", "Music & scent", "Staff energy"]},
]

HASHTAGS = {
    "Visual Merchandising": ["#VisualMerchandising", "#RetailDisplay", "#StoreDesign", "#VMTips", "#WindowDisplay", "#RetailExperience"],
    "HR & People Management": ["#HumanResources", "#Recruitment", "#TalentAcquisition", "#PeopleFirst", "#RetailHR", "#Hiring"],
    "Store Operations": ["#RetailOperations", "#StoreManagement", "#RetailExcellence", "#CustomerExperience", "#RetailStrategy"],
    "Career & Leadership": ["#Leadership", "#CareerGrowth", "#ProfessionalDevelopment", "#CareerAdvice", "#GrowthMindset", "#WomenInRetail"],
    "Employee Engagement": ["#EmployeeEngagement", "#WorkplaceCulture", "#TeamBuilding", "#EmployeeExperience", "#PeopleMatter"],
    "Retail Strategy": ["#RetailStrategy", "#RetailInnovation", "#CustomerExperience", "#RetailGrowth", "#RetailLeadership"],
    "Industry Trends": ["#FutureOfWork", "#RetailTrends", "#HRTrends", "#Innovation", "#DigitalTransformation", "#RetailTech"],
    "Quick VM Tip": ["#VMTips", "#VisualMerchandising", "#RetailHacks", "#StoreDisplay"],
    "HR Hot Take": ["#HRCommunity", "#RetailHR", "#TalentManagement", "#HotTake"],
    "Retail Life": ["#RetailLife", "#RetailProblems", "#StoreLife", "#RetailHumor"],
    "Career Advice": ["#CareerTips", "#RetailCareers", "#ProfessionalGrowth", "#Mentoring"],
    "Team Culture": ["#TeamCulture", "#WorkplaceWellbeing", "#RetailTeams", "#Gratitude"],
    "Weekend Wisdom": ["#WeekendWisdom", "#RetailLearnings", "#SaturdayThoughts", "#GrowthMindset"],
    "Week Ahead": ["#MondayMotivation", "#WeekAhead", "#RetailGoals", "#NewWeek"],
}

CREATOR_TAGS = {
    "Visual Merchandising": ["Retail design enthusiasts", "VM community", "Store designers and merchandisers"],
    "HR & People Management": ["HR leaders in retail", "People-first leaders", "Talent acquisition community"],
    "Store Operations": ["Retail ops professionals", "Store managers", "Retail leaders"],
    "Career & Leadership": ["Career coaches", "Women in retail leadership", "Professional development community"],
    "Employee Engagement": ["People & culture leaders", "Workplace culture advocates", "Employee experience community"],
}

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



# ============================================================
# CORE FUNCTIONS
# ============================================================

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
    hook = random.choice(hooks) if hooks else ""
    tags = " ".join(random.sample(HASHTAGS.get(topic, HASHTAGS["Career & Leadership"]), min(4, len(HASHTAGS.get(topic, [])))))

    session_ctx = ""
    if POST_SESSION == "evening":
        session_ctx = "- EVENING post: lighter, conversational, under 150 words, slightly humorous"
    else:
        session_ctx = "- MORNING post: professional, value-driven, 150-250 words"

    return f"""Write a LinkedIn post AS Preethi Prasanna — 8+ years in Visual Merchandising & Store Operations, expanding into HR/People Management. Worked on store launches, built teams, managed VM for premium retail brands in India.

Topic: {topic} | Style: {style}
Opening hook (adapt): "{hook}"
{session_ctx}

RULES:
- First 2 lines MUST create curiosity (shows before "see more")
- Line breaks every 1-2 sentences. Short punchy paragraphs.
- ONE specific number/example from Indian retail
- End with a question people WANT to answer
- 4 hashtags at end: {tags}
- 2-3 emojis max
- Write like a real person, NOT a corporate comms team

NEVER: Start with "I", use "In today's fast-paced world", sound like ChatGPT, exceed 250 words.

Output ONLY the post text."""


def generate_with_gemini(prompt):
    """Generate content using the new google-genai SDK."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    if not genai:
        raise ImportError("google-genai package not installed")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    text = response.text.strip()
    if not text or len(text) < 50:
        raise ValueError(f"Gemini returned too-short response: '{text[:100]}'")
    return text


def generate_fallback(topic, style):
    """Fallback templates when API unavailable."""
    templates = [
        f"Stop scrolling.\n\nIf you're in retail, this will save you hours.\n\nAfter 5+ store launches, here's my cheat sheet for {topic.lower()}:\n\n→ Start with your customer's eye level\n→ Change displays every 14 days (not when you feel like it)\n→ Train your team on WHY, not just HOW\n→ Measure footfall before/after every change\n\nThe stores that win aren't doing anything revolutionary.\nThey're doing the basics consistently.\n\nWhich one do you struggle with most? 👇\n\n#VisualMerchandising #RetailOperations #StoreManagement #RetailTips",
        f"The biggest myth in retail?\n\n'Good VM sells itself.'\n\nNo. Good VM + trained staff + right energy = sales.\n\nI've seen stores with stunning displays and zero conversions.\nI've seen stores with basic VM but incredible teams crushing targets.\n\nThe difference isn't the display.\nIt's the team behind it.\n\n{topic} is a team sport. Build accordingly.\n\nAgree? Disagree? Tell me 👇\n\n#RetailExcellence #TeamBuilding #VisualMerchandising #StoreOperations",
        f"Real talk about {topic.lower()}.\n\nNobody posts about the failures. So let me go first.\n\nI once spent 3 days perfecting a store display.\nCustomers walked past it without a second glance.\n\nThe fix? I asked a customer what they were looking for.\nRebuilt the display around THEIR journey in 2 hours.\n\nResult: 35% increase in dwell time.\n\nLesson: We design for Instagram. We should design for customers.\n\nWhat's a retail fail that taught you something? 👇\n\n#RetailLearning #VisualMerchandising #CustomerFirst #RetailTips",
        f"Here's a {topic.lower()} reminder that costs ₹0:\n\n1. Your team mirrors your energy (check yours first)\n2. One small display change > zero changes while waiting for 'the big revamp'\n3. Ask your newest team member what confuses them\n4. Document what works (future you will thank present you)\n\nSimple? Yes.\nDoes everyone do it? No.\n\nThat's the edge.\n\nWhich one are you implementing this week? 👇\n\n#RetailLeadership #StoreOperations #RetailTips #RetailExcellence",
        f"Quiet confession from 8 years in retail:\n\nThe best store I ever managed wasn't the most beautiful one.\n\nIt was the one where:\n→ Every team member greeted by name\n→ The stockroom was organized (not just the floor)\n→ We celebrated small wins loudly\n→ Training happened daily, not quarterly\n\nRetail success isn't a visual. It's a feeling.\n\nYour customers feel what your team feels.\n\nBuild the team first. The aesthetics follow.\n\nWhat made YOUR best store 'the best'? 👇\n\n#RetailExcellence #TeamCulture #StoreOperations #EmployeeEngagement",
    ]
    return random.choice(templates)


def is_duplicate(content, history):
    return hashlib.md5(content.encode()).hexdigest() in history.get("hashes", [])



# ============================================================
# LINKEDIN TOKEN REFRESH
# ============================================================

def refresh_linkedin_token():
    """Refresh LinkedIn token and update GitHub secret. Returns new token or None."""
    refresh_token = os.environ.get("LINKEDIN_REFRESH_TOKEN")
    client_id = os.environ.get("LINKEDIN_CLIENT_ID")
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")
    gh_pat = os.environ.get("GH_PAT")
    if not all([refresh_token, client_id, client_secret]):
        print("⚠️ Missing refresh token env vars")
        return None
    try:
        r = requests.post("https://www.linkedin.com/oauth/v2/accessToken", data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }, timeout=30)
        if not r.ok:
            print(f"❌ Token refresh failed: {r.status_code} {r.text}")
            return None
        new_token = r.json().get("access_token")
        if not new_token:
            return None
        print("✅ LinkedIn token refreshed successfully")
        # Update GitHub secret
        if gh_pat:
            try:
                from nacl import encoding, public
                repo = "visualcraft-ops/Linkedin-post"
                gh_headers = {"Authorization": f"Bearer {gh_pat}", "Accept": "application/vnd.github+json"}
                key_resp = requests.get(f"https://api.github.com/repos/{repo}/actions/secrets/public-key", headers=gh_headers, timeout=30)
                if key_resp.ok:
                    key_data = key_resp.json()
                    public_key = public.PublicKey(key_data["key"].encode("utf-8"), encoding.Base64Encoder())
                    sealed_box = public.SealedBox(public_key)
                    encrypted = sealed_box.encrypt(new_token.encode("utf-8"))
                    encrypted_value = encoding.Base64Encoder.encode(encrypted).decode("utf-8")
                    requests.put(f"https://api.github.com/repos/{repo}/actions/secrets/LINKEDIN_TOKEN",
                                 headers=gh_headers, json={"encrypted_value": encrypted_value, "key_id": key_data["key_id"]}, timeout=30)
                    print("✅ GitHub secret LINKEDIN_TOKEN updated")
            except Exception as e:
                print(f"⚠️ Failed to update GitHub secret: {e}")
        return new_token
    except Exception as e:
        print(f"❌ Token refresh error: {e}")
        return None


# ============================================================
# LINKEDIN API FUNCTIONS
# ============================================================

def get_person_id():
    r = requests.get("https://api.linkedin.com/v2/userinfo",
                     headers={"Authorization": f"Bearer {LINKEDIN_TOKEN}"}, timeout=30)
    if not r.ok:
        raise RuntimeError(f"Failed to get person ID: {r.status_code} {r.text}")
    return r.json()["sub"]


def publish_to_linkedin(content, poll_data=None):
    """Publish post or poll. Returns post URN on success."""
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
        r = requests.post("https://api.linkedin.com/rest/posts", headers=headers, json=body, timeout=30)
        if r.status_code == 401:
            print("❌ Token expired! Attempting auto-refresh...")
            new_token = refresh_linkedin_token()
            if new_token:
                headers["Authorization"] = f"Bearer {new_token}"
                r = requests.post("https://api.linkedin.com/rest/posts", headers=headers, json=body, timeout=30)
                if r.ok:
                    post_urn = r.headers.get("x-restli-id", "")
                    print(f"✅ Published {'poll' if poll_data else 'post'} after refresh! URN: {post_urn}")
                    return post_urn
                print(f"❌ Post failed after refresh: {r.status_code} {r.text}")
            return None
        if not r.ok:
            print(f"❌ Post failed: {r.status_code} {r.text}")
            return None
        post_urn = r.headers.get("x-restli-id", "")
        print(f"✅ Published {'poll' if poll_data else 'post'}! URN: {post_urn}")
        return post_urn
    except Exception as e:
        print(f"❌ Publishing error: {e}")
        return None


def post_self_comment(post_urn):
    """Post a follow-up comment on own post to boost engagement."""
    if not LINKEDIN_TOKEN or not post_urn:
        return False
    try:
        time.sleep(30)  # Wait 30s to look natural
        person_id = get_person_id()
        headers = {
            "Authorization": f"Bearer {LINKEDIN_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": LINKEDIN_VERSION,
        }
        comment_text = random.choice(BOOST_COMMENTS)
        # Convert ugcPost URN to activity URN for comments API
        # x-restli-id returns "urn:li:ugcPost:123" but comments need activity URN
        # Use the ugcPost URN directly in the URL path
        url = f"https://api.linkedin.com/rest/socialActions/{post_urn}/comments"
        body = {
            "actor": f"urn:li:person:{person_id}",
            "object": post_urn,
            "message": {"text": comment_text},
        }
        r = requests.post(url, headers=headers, json=body, timeout=30)
        if r.status_code in (200, 201):
            print(f"💬 Self-comment posted: '{comment_text[:50]}...'")
            return True
        print(f"⚠️ Comment failed: {r.status_code} {r.text}")
        return False
    except Exception as e:
        print(f"⚠️ Comment error: {e}")
        return False


def add_engagement_tag(content, topic):
    """Add a subtle community callout to boost reach."""
    tags = CREATOR_TAGS.get(topic, CREATOR_TAGS.get("Career & Leadership", []))
    if tags and random.random() < 0.6:
        tag = random.choice(tags)
        callouts = [
            f"\n\n🔔 {tag} — what's your take?",
            f"\n\nCalling all {tag.lower()} 👆",
            f"\n\n💬 {tag}, I'd love your perspective.",
        ]
        content += random.choice(callouts)
    return content


def save_post(content, topic, style):
    today = date.today().isoformat()
    session = f"_{POST_SESSION}" if POST_SESSION == "evening" else ""
    filename = f"{today}{session}_{topic.lower().replace(' & ', '-').replace(' ', '-')}.md"
    filepath = GENERATED_DIR / filename
    filepath.write_text(f"---\ndate: {today}\ntopic: {topic}\nstyle: {style}\nsession: {POST_SESSION}\n---\n\n{content}\n")
    return filepath


def build_poll_prompt(topic):
    return f"""Generate a LinkedIn POLL for Preethi Prasanna (8+ years Visual Merchandising & Store Ops, expanding to HR).
Topic: {topic}
- Commentary: 2-3 punchy lines that make people WANT to vote. Include 3-4 hashtags.
- Question: max 140 chars, clear and debatable
- 4 options: max 30 chars each, all valid answers
- Relevant to Indian retail/HR professionals
Output EXACTLY as JSON: {{"commentary": "text", "question": "q?", "options": ["A", "B", "C", "D"]}}"""


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
# MAIN
# ============================================================

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
        filepath = save_post(content + f"\n\n[POLL: {poll_data['question']}]\n" + "\n".join(poll_data["options"]), topic, "poll")
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

        content = add_engagement_tag(content, topic)
        filepath = save_post(content, topic, style)
        post_urn = publish_to_linkedin(content)
        poll_data = None

    # Self-comment boost (morning posts, 70% of time)
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
    if is_poll and poll_data:
        print(f"\n📊 {poll_data['question']}")
        for i, opt in enumerate(poll_data['options'], 1):
            print(f"   {i}. {opt}")
    print("=" * 50)


if __name__ == "__main__":
    main()
