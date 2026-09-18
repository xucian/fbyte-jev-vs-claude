TASKS = {
    "bouncer": {
        "name": "The Bouncer",
        "emoji": "\U0001f6aa",
        "tagline": "Single-Label Intent Routing",
        "questions": [
            {
                "name": "department",
                "type": "choice",
                "instructions": "Which department should handle this customer message?",
                "criteria": {
                    "billing": ["Charges", "Invoices", "Refunds", "Payments", "Pricing", "Subscription fees"],
                    "technical": ["Bugs", "Crashes", "Errors", "Performance", "Outages", "Broken features"],
                    "account": ["Login", "Settings", "Profile", "Access", "Merge", "Recovery"],
                    "shipping": ["Delivery", "Tracking", "Address", "Transit", "Package"],
                    "returns": ["Return", "Exchange", "Warranty", "Refund process"],
                    "sales": ["Purchase", "Plans", "Enterprise", "Demo", "Pricing inquiry", "Volume"],
                    "security": ["Breach", "Unauthorized", "Fraud", "Stolen", "Suspicious activity"],
                    "other": None,
                },
            }
        ],
        "claude_prompt": (
            "Classify the following customer message into exactly one department.\n"
            "Departments: billing, technical, account, shipping, returns, sales, security, other\n\n"
            "Message: \"{text}\"\n\n"
            "Return ONLY valid JSON:\n"
            '{"department": "<department>", "department_confidence": <0.0-1.0>}'
        ),
        "scoring": {"department": "exact"},
        "cases": [
            {"id": 1, "text": "My card was charged twice but I also can't log in", "ground_truth": {"department": "billing"}},
            {"id": 2, "text": "I want to upgrade but your pricing page is broken", "ground_truth": {"department": "technical"}},
            {"id": 3, "text": "Someone else is buying stuff with my account", "ground_truth": {"department": "security"}},
            {"id": 4, "text": "When will my refund ship back to my card?", "ground_truth": {"department": "returns"}},
            {"id": 5, "text": "Do you have an API? I'd like to integrate.", "ground_truth": {"department": "sales"}},
            {"id": 6, "text": "I changed my email but now I can't reset my password", "ground_truth": {"department": "account"}},
            {"id": 7, "text": "Your app crashes every time I open the notifications tab", "ground_truth": {"department": "technical"}},
            {"id": 8, "text": "I'm a reseller — can I get volume pricing?", "ground_truth": {"department": "sales"}},
            {"id": 9, "text": "My package says delivered but I never got it", "ground_truth": {"department": "shipping"}},
            {"id": 10, "text": "I just got a password reset email I didn't request", "ground_truth": {"department": "security"}},
            {"id": 11, "text": "I was charged $49 but my plan says $29 — also the upgrade button is grayed out", "ground_truth": {"department": "billing"}},
            {"id": 12, "text": "Can I merge two accounts into one? I have credits on both.", "ground_truth": {"department": "account"}},
            {"id": 13, "text": "The PDF export has been broken for a week — our reports are due Friday", "ground_truth": {"department": "technical"}},
            {"id": 14, "text": "I shipped back my return two weeks ago and the refund hasn't posted — is it lost?", "ground_truth": {"department": "returns"}},
            {"id": 15, "text": "We're evaluating your enterprise plan for 200+ seats — who should I talk to?", "ground_truth": {"department": "sales"}},
            {"id": 16, "text": "I left my phone at a coffee shop and need to revoke all active sessions now", "ground_truth": {"department": "security"}},
            {"id": 17, "text": "My order shipped to my old address even though I updated it before checkout", "ground_truth": {"department": "shipping"}},
            {"id": 18, "text": "I need a copy of all invoices from last quarter for our tax filing", "ground_truth": {"department": "billing"}},
            {"id": 19, "text": "Just wanted to say thanks — your product helped me finish a project on time. Keep up the great work!", "ground_truth": {"department": "other"}},
            {"id": 20, "text": "I accidentally deleted my workspace and all my team's projects — can you recover it?", "ground_truth": {"department": "account"}},
        ],
    },

    "lie_detector": {
        "name": "The Lie Detector",
        "emoji": "\U0001f50d",
        "tagline": "Fake Review Detection",
        "questions": [
            {
                "name": "sentiment",
                "type": "choice",
                "instructions": "What is the overall sentiment of this product review?",
                "criteria": {
                    "positive": ["Great", "Love", "Amazing", "Best", "Recommend"],
                    "negative": ["Terrible", "Broke", "Worst", "Hate", "Garbage"],
                    "neutral": ["Okay", "Fine", "Average", "Decent", "Mixed"],
                },
            },
            {
                "name": "fakeness",
                "type": "score",
                "instructions": "How likely is this review to be fake or astroturfed?",
                "criteria": [
                    "Definitely genuine — specific details, personal experience, balanced",
                    "Likely genuine — some specifics, natural tone",
                    "Uncertain — could go either way",
                    "Likely fake — generic, exaggerated, promotional",
                    "Definitely fake — template-like, shill, competitor bash",
                ],
            },
            {
                "name": "pii",
                "type": "noul",
                "instructions": "Does this review contain personally identifiable information (names, addresses, phone numbers, emails, employee IDs)?",
            },
        ],
        "claude_prompt": (
            "Analyze the following product review on three dimensions:\n"
            "1. Sentiment: positive, negative, or neutral\n"
            "2. Fakeness: 0.0 (definitely genuine) to 1.0 (definitely fake)\n"
            "3. Contains PII (names, addresses, phone numbers, emails, employee IDs): true or false\n\n"
            "Review: \"{text}\"\n\n"
            "Return ONLY valid JSON:\n"
            '{"sentiment": "<positive|negative|neutral>", "sentiment_confidence": <0.0-1.0>, '
            '"fakeness": <0.0-1.0>, "fakeness_confidence": <0.0-1.0>, '
            '"pii": <true|false>, "pii_confidence": <0.0-1.0>}'
        ),
        "scoring": {"sentiment": "exact", "fakeness": "continuous", "pii": "exact"},
        "cases": [
            {
                "id": 1,
                "text": "I've been using this blender for 3 months and it's AMAZING!!! Model XR-7700B is the best $49.99 purchase. Buy from amzn.link/d/abc123",
                "ground_truth": {"sentiment": "positive", "fakeness": 0.7, "pii": False},
            },
            {
                "id": 2,
                "text": "Bought this for my daughter Sarah at 123 Oak St, it broke day one. Absolute garbage. Called support and John employee #4421 was rude.",
                "ground_truth": {"sentiment": "negative", "fakeness": 0.1, "pii": True},
            },
            {
                "id": 3,
                "text": "Five stars. Great product. Would buy again. Highly recommended. A+++++++ seller.",
                "ground_truth": {"sentiment": "positive", "fakeness": 0.9, "pii": False},
            },
            {
                "id": 4,
                "text": "I've been a barista for 12 years and this grinder is mediocre at best. The burrs are cheap steel, not ceramic as listed. My Baratza from 2015 outperforms it. Save your money.",
                "ground_truth": {"sentiment": "negative", "fakeness": 0.05, "pii": False},
            },
            {
                "id": 5,
                "text": "UPDATE: Changing from 1 star to 4 stars. Manager Emily (store #2847, Portland location) personally called me and resolved everything. The replacement unit works perfectly.",
                "ground_truth": {"sentiment": "positive", "fakeness": 0.1, "pii": True},
            },
            {
                "id": 6,
                "text": "DO NOT BUY! This company's competitor XYZ Brand makes the exact same thing for half the price. I tested both side by side and XYZ wins in every category. Link to XYZ: bit.ly/fake123",
                "ground_truth": {"sentiment": "negative", "fakeness": 0.85, "pii": False},
            },
            {
                "id": 7,
                "text": "It's fine. Does what it says. Nothing special but nothing wrong with it either. I use it maybe twice a week.",
                "ground_truth": {"sentiment": "neutral", "fakeness": 0.1, "pii": False},
            },
            {
                "id": 8,
                "text": "BEST. PURCHASE. EVER. I bought 5 for all my friends and family! Changed my life completely!! Can't imagine living without this incredible product!!",
                "ground_truth": {"sentiment": "positive", "fakeness": 0.85, "pii": False},
            },
            {
                "id": 9,
                "text": "Received this as a gift from my husband for our anniversary. The noise level is louder than the 45dB they claim — measured 62dB at 1 meter with my phone. Still using it daily though, it blends well.",
                "ground_truth": {"sentiment": "neutral", "fakeness": 0.05, "pii": False},
            },
            {
                "id": 10,
                "text": "I work at the warehouse and we see these come back all the time. The motor fails after about 3 months. Contact me at fixitjohn@gmail.com if you want repair tips.",
                "ground_truth": {"sentiment": "negative", "fakeness": 0.3, "pii": True},
            },
            {
                "id": 11,
                "text": "Purchased for my son's dorm room. Works great for smoothies but the cord is too short. He had to buy an extension cord from the campus bookstore.",
                "ground_truth": {"sentiment": "positive", "fakeness": 0.1, "pii": False},
            },
            {
                "id": 12,
                "text": "This product literally saved my marriage. My wife and I were fighting every morning about coffee and now we're in bliss. THANK YOU!!!",
                "ground_truth": {"sentiment": "positive", "fakeness": 0.6, "pii": False},
            },
            {
                "id": 13,
                "text": "1 star. Gave me chemical burns on my face — called my dermatologist Dr. Patricia Kwan (555-012-3456) who confirmed it's a reaction to an unlisted ingredient. Filing an FDA complaint.",
                "ground_truth": {"sentiment": "negative", "fakeness": 0.05, "pii": True},
            },
            {
                "id": 14,
                "text": "Verified purchase. This item is exactly as described. Fast shipping. Would purchase again. The quality is premium and the design is elegant. 5/5.",
                "ground_truth": {"sentiment": "positive", "fakeness": 0.8, "pii": False},
            },
            {
                "id": 15,
                "text": "Got this vacuum on sale for $199 (reg $349). Suction is strong on hardwood but weak on thick carpet. The dustbin is smaller than my old Dyson V11. Battery dies after about 25 min not the 40 they claim.",
                "ground_truth": {"sentiment": "neutral", "fakeness": 0.05, "pii": False},
            },
            {
                "id": 16,
                "text": "I ordered this from the seller's website. When it arrived to my apartment 4B at 789 Pine Street it was already open. My neighbor Maria saw the delivery guy just toss it. Unacceptable.",
                "ground_truth": {"sentiment": "negative", "fakeness": 0.1, "pii": True},
            },
            {
                "id": 17,
                "text": "As a professional chef with Michelin experience, I can say this knife set is comparable to $500+ German steel. The edge retention is remarkable. This will be my go-to recommendation for home cooks.",
                "ground_truth": {"sentiment": "positive", "fakeness": 0.4, "pii": False},
            },
            {
                "id": 18,
                "text": "I bought this same item three times under different seller names and they're all identical — same factory, same packaging, just rebranded. It's decent quality for the price but the markup from 'premium' sellers is a scam.",
                "ground_truth": {"sentiment": "neutral", "fakeness": 0.15, "pii": False},
            },
            {
                "id": 19,
                "text": "Perfect gift for my grandmother, Mrs. Helen Kowalski (age 82). She loves it! Easy to use with her arthritis. Shipping to 456 Elm Drive, Apt 2C was fast.",
                "ground_truth": {"sentiment": "positive", "fakeness": 0.15, "pii": True},
            },
            {
                "id": 20,
                "text": "This product has over 4000 five-star reviews so you know it's legit. Don't listen to the haters. The company clearly cares about quality. I recommend checking their other listings too!",
                "ground_truth": {"sentiment": "positive", "fakeness": 0.9, "pii": False},
            },
        ],
    },

    "oracle": {
        "name": "The Oracle",
        "emoji": "\U0001f52e",
        "tagline": "Bug Triage",
        "questions": [
            {
                "name": "priority",
                "type": "choice",
                "instructions": "What priority should this bug report be assigned?",
                "criteria": {
                    "P0": ["Down", "Data loss", "All users", "Security breach", "Cannot operate"],
                    "P1": ["Critical feature broken", "Many users affected", "Revenue impact"],
                    "P2": ["Important feature degraded", "Workaround exists", "Moderate impact"],
                    "P3": ["Minor issue", "Low impact", "Edge case"],
                    "P4": ["Cosmetic", "Nice-to-have", "Polish"],
                },
            },
            {
                "name": "component",
                "type": "choice",
                "instructions": "Which component is this bug report about?",
                "criteria": {
                    "auth": ["Login", "SSO", "Password", "Session", "Token", "OAuth"],
                    "payments": ["Checkout", "Charge", "Payment gateway", "Billing integration"],
                    "api": ["Endpoint", "Rate limit", "Webhook", "REST", "SDK"],
                    "ui": ["Display", "Layout", "Button", "CSS", "Mobile", "Responsive"],
                    "database": ["Query", "Migration", "Replication", "Disk", "Schema"],
                    "infra": ["Deploy", "Kubernetes", "Server", "Memory", "CPU", "DNS", "Email delivery"],
                    "notifications": ["Email", "Push", "SMS", "Alert", "In-app notification"],
                    "other": None,
                },
            },
            {
                "name": "regression",
                "type": "noul",
                "instructions": "Is this a regression (something that previously worked but is now broken due to a recent change)?",
            },
        ],
        "claude_prompt": (
            "Triage the following bug report.\n"
            "Priority levels: P0 (service down/data loss), P1 (critical feature broken), "
            "P2 (important but workaround exists), P3 (minor), P4 (cosmetic)\n"
            "Components: auth, payments, api, ui, database, infra, notifications, other\n"
            "Regression: true if it worked before and broke due to a recent change, false otherwise\n\n"
            "Bug report: \"{text}\"\n\n"
            "Return ONLY valid JSON:\n"
            '{"priority": "<P0-P4>", "priority_confidence": <0.0-1.0>, '
            '"component": "<component>", "component_confidence": <0.0-1.0>, '
            '"regression": <true|false>, "regression_confidence": <0.0-1.0>}'
        ),
        "scoring": {"priority": "within_one", "component": "exact", "regression": "exact"},
        "cases": [
            {
                "id": 1,
                "text": "After deploying v2.3.1, none of our EU customers can check out. Payment gateway returns 502. Was fine on v2.3.0.",
                "ground_truth": {"priority": "P0", "component": "payments", "regression": True},
            },
            {
                "id": 2,
                "text": "The loading spinner is blue instead of our brand purple. It's been like this since we launched.",
                "ground_truth": {"priority": "P4", "component": "ui", "regression": False},
            },
            {
                "id": 3,
                "text": "Users report 500 errors when trying to log in with SSO since yesterday's deploy. Regular login still works.",
                "ground_truth": {"priority": "P1", "component": "auth", "regression": True},
            },
            {
                "id": 4,
                "text": "The API rate limiter is letting through 2x the configured threshold. Has been this way since we first checked.",
                "ground_truth": {"priority": "P2", "component": "api", "regression": False},
            },
            {
                "id": 5,
                "text": "Push notifications are arriving 6-8 hours late for Android users. iOS is fine. Started after the Firebase SDK update on Monday.",
                "ground_truth": {"priority": "P2", "component": "notifications", "regression": True},
            },
            {
                "id": 6,
                "text": "The database is at 94% disk usage and growing. Query times have doubled this week. We've got maybe 3 days before it hits 100%.",
                "ground_truth": {"priority": "P1", "component": "database", "regression": False},
            },
            {
                "id": 7,
                "text": "The forgot-password flow sends the reset link but the link returns a 404. No recent changes to auth service.",
                "ground_truth": {"priority": "P1", "component": "auth", "regression": False},
            },
            {
                "id": 8,
                "text": "Tooltips on the dashboard cards overlap with the header when you scroll. Minor visual bug, been there since the redesign 3 months ago.",
                "ground_truth": {"priority": "P3", "component": "ui", "regression": False},
            },
            {
                "id": 9,
                "text": "Production database replica is 45 minutes behind primary. Reads are returning stale data. Replication lag started after last night's infra maintenance.",
                "ground_truth": {"priority": "P0", "component": "database", "regression": True},
            },
            {
                "id": 10,
                "text": "The 'order shipped' email includes the customer's full credit card number instead of the last 4 digits. We think it changed when we updated the email templates two sprints ago.",
                "ground_truth": {"priority": "P0", "component": "notifications", "regression": True},
            },
            {
                "id": 11,
                "text": "Mobile app crashes on startup for devices running Android 14. Works fine on 13 and below. We only started getting reports after Android 14 rolled out widely.",
                "ground_truth": {"priority": "P1", "component": "ui", "regression": False},
            },
            {
                "id": 12,
                "text": "Webhook delivery retries are not backing off exponentially — they hammer the consumer's endpoint every 2 seconds until timeout. Consumers are complaining.",
                "ground_truth": {"priority": "P2", "component": "api", "regression": False},
            },
            {
                "id": 13,
                "text": "Payment processing latency jumped from ~200ms to ~3 seconds after we migrated to the new payment provider last week. Transactions complete but the UX is painful.",
                "ground_truth": {"priority": "P2", "component": "payments", "regression": True},
            },
            {
                "id": 14,
                "text": "Our Kubernetes pods are OOMKilling every 4-6 hours. Memory leak introduced somewhere. Started after the v3.1 release.",
                "ground_truth": {"priority": "P1", "component": "infra", "regression": True},
            },
            {
                "id": 15,
                "text": "Our onboarding docs still reference the old API endpoint that was deprecated last year. New developers keep hitting 410 Gone errors following the tutorial.",
                "ground_truth": {"priority": "P3", "component": "other", "regression": False},
            },
            {
                "id": 16,
                "text": "Authentication tokens are not being revoked on password change. Old sessions stay active indefinitely after a password reset.",
                "ground_truth": {"priority": "P1", "component": "auth", "regression": False},
            },
            {
                "id": 17,
                "text": "The search API returns 0 results for queries containing special characters like 'AT&T' or 'M&M's'. Always been this way.",
                "ground_truth": {"priority": "P3", "component": "api", "regression": False},
            },
            {
                "id": 18,
                "text": "Users in Japan are seeing prices in USD instead of JPY since the localization update. We have 50K+ Japanese users.",
                "ground_truth": {"priority": "P1", "component": "ui", "regression": True},
            },
            {
                "id": 19,
                "text": "Grafana dashboards show a gap in metrics between 2am-4am UTC every night. The monitoring agent seems to pause during the backup window.",
                "ground_truth": {"priority": "P3", "component": "infra", "regression": False},
            },
            {
                "id": 20,
                "text": "All outbound emails are landing in spam since we rotated our DKIM keys yesterday. Open rates dropped from 35% to 2% overnight.",
                "ground_truth": {"priority": "P1", "component": "infra", "regression": True},
            },
        ],
    },

    "bartender": {
        "name": "The Bartender",
        "emoji": "\U0001f378",
        "tagline": "Multi-Axis Content Moderation",
        "questions": [
            {
                "name": "toxic",
                "type": "noul",
                "instructions": "Is this user-generated comment toxic or harmful and requiring moderation?",
            },
            {
                "name": "category",
                "type": "choice",
                "instructions": "What category does this comment fall into?",
                "criteria": {
                    "hate_speech": ["Slur", "Racism", "Sexism", "Bigotry", "Dehumanizing"],
                    "harassment": ["Personal attack", "Bullying", "Insult", "Intimidation"],
                    "threat": ["Violence", "Harm", "Doxxing", "Physical threat"],
                    "sexual": ["Explicit", "Unsolicited", "Grooming", "Objectifying"],
                    "self_harm": ["Suicide", "Self-injury", "Eating disorder", "Dangerous behavior"],
                    "spam": ["Promotion", "Scam", "Bot", "Brigading", "Mass report"],
                    "clean": None,
                },
            },
            {
                "name": "severity",
                "type": "score",
                "instructions": "How severe is this content in terms of potential harm?",
                "criteria": [
                    "Harmless — no moderation needed",
                    "Mildly concerning — borderline, monitor",
                    "Moderate — should be reviewed",
                    "Severe — should be removed",
                    "Extreme — immediate action, possible escalation to law enforcement",
                ],
            },
        ],
        "claude_prompt": (
            "Moderate the following user-generated comment.\n"
            "1. Toxic: Is this comment toxic/harmful and requiring moderation? (true/false)\n"
            "2. Category: hate_speech, harassment, threat, sexual, self_harm, spam, or clean\n"
            "3. Severity: 0.0 (harmless) to 1.0 (extreme, needs immediate action)\n\n"
            "Comment: \"{text}\"\n\n"
            "Return ONLY valid JSON:\n"
            '{"toxic": <true|false>, "toxic_confidence": <0.0-1.0>, '
            '"category": "<category>", "category_confidence": <0.0-1.0>, '
            '"severity": <0.0-1.0>, "severity_confidence": <0.0-1.0>}'
        ),
        "scoring": {"toxic": "exact", "category": "exact", "severity": "continuous"},
        "cases": [
            {
                "id": 1,
                "text": "I hope your team loses so badly they disband the franchise forever lol",
                "ground_truth": {"toxic": False, "category": "clean", "severity": 0.1},
            },
            {
                "id": 2,
                "text": "People like you shouldn't be allowed to have opinions. Crawl back to your hole.",
                "ground_truth": {"toxic": True, "category": "harassment", "severity": 0.8},
            },
            {
                "id": 3,
                "text": "kys lol ratio + didn't ask + L + maidenless",
                "ground_truth": {"toxic": True, "category": "harassment", "severity": 0.6},
            },
            {
                "id": 4,
                "text": "Just mass-reported this guy's account from 12 alts \U0001f602",
                "ground_truth": {"toxic": True, "category": "spam", "severity": 0.5},
            },
            {
                "id": 5,
                "text": "As a cancer survivor, I can joke about dying — it's MY coping mechanism",
                "ground_truth": {"toxic": False, "category": "clean", "severity": 0.0},
            },
            {
                "id": 6,
                "text": "I swear this game is rigged. I've lost 20 times in a row. The devs are trolling us.",
                "ground_truth": {"toxic": False, "category": "clean", "severity": 0.1},
            },
            {
                "id": 7,
                "text": "Women shouldn't be in competitive gaming. They just don't have the reaction time. It's biology.",
                "ground_truth": {"toxic": True, "category": "hate_speech", "severity": 0.7},
            },
            {
                "id": 8,
                "text": "lmaooo you're so bad at this game, uninstall \U0001f62d\U0001f62d",
                "ground_truth": {"toxic": False, "category": "clean", "severity": 0.15},
            },
            {
                "id": 9,
                "text": "If I ever see you in real life, you better run. That's not a joke.",
                "ground_truth": {"toxic": True, "category": "threat", "severity": 0.9},
            },
            {
                "id": 10,
                "text": "God I hate Mondays. I hate this job. I hate everything about this timeline.",
                "ground_truth": {"toxic": False, "category": "clean", "severity": 0.0},
            },
            {
                "id": 11,
                "text": "Those people from the east side always bring crime. We need to keep them out of our community.",
                "ground_truth": {"toxic": True, "category": "hate_speech", "severity": 0.6},
            },
            {
                "id": 12,
                "text": "I'm going to end it all tonight. Nobody cares anyway. Maybe then they'll notice.",
                "ground_truth": {"toxic": True, "category": "self_harm", "severity": 0.9},
            },
            {
                "id": 13,
                "text": "Subscribe to my YouTube channel for more content! Link in bio! Like and share!",
                "ground_truth": {"toxic": True, "category": "spam", "severity": 0.2},
            },
            {
                "id": 14,
                "text": "Your cooking videos are terrible. Literally anyone could make better content with their eyes closed. How do you even have subscribers?",
                "ground_truth": {"toxic": False, "category": "clean", "severity": 0.25},
            },
            {
                "id": 15,
                "text": "Serious question: is it normal to think about jumping off bridges? Asking for a friend ha ha",
                "ground_truth": {"toxic": True, "category": "self_harm", "severity": 0.7},
            },
            {
                "id": 16,
                "text": "I'm going to DESTROY you in this debate. Your arguments are pathetically weak and everyone can see it.",
                "ground_truth": {"toxic": False, "category": "clean", "severity": 0.2},
            },
            {
                "id": 17,
                "text": "Send nudes or I'll share the screenshots I have of you from last time",
                "ground_truth": {"toxic": True, "category": "sexual", "severity": 0.95},
            },
            {
                "id": 18,
                "text": "Men are all trash. Every single one. No exceptions.",
                "ground_truth": {"toxic": True, "category": "hate_speech", "severity": 0.5},
            },
            {
                "id": 19,
                "text": "FIRST!!!! Also this video is mid. The part at 3:42 was decent though.",
                "ground_truth": {"toxic": False, "category": "clean", "severity": 0.0},
            },
            {
                "id": 20,
                "text": "I found this user's address and workplace. Everyone should pay them a visit and teach them a lesson about running their mouth online.",
                "ground_truth": {"toxic": True, "category": "threat", "severity": 0.95},
            },
        ],
    },

    "customs_agent": {
        "name": "The Customs Agent",
        "emoji": "\U0001f6c2",
        "tagline": "Contract Clause Classification",
        "questions": [
            {
                "name": "clause_type",
                "type": "choice",
                "instructions": "What type of contract clause is this?",
                "criteria": {
                    "liability_cap": ["Limitation of liability", "Damages cap", "Exclusion of damages"],
                    "indemnification": ["Indemnify", "Hold harmless", "Defend"],
                    "termination": ["Terminate", "Cancellation", "End of agreement", "Notice period"],
                    "ip_assignment": ["Intellectual property", "Assigns rights", "Work for hire", "Ownership"],
                    "non_compete": ["Non-compete", "Non-solicitation", "Restrictive covenant"],
                    "confidentiality": ["Confidential", "NDA", "Trade secret", "Non-disclosure"],
                    "payment_terms": ["Payment", "Invoice", "Net terms", "Late fees"],
                    "force_majeure": ["Force majeure", "Act of God", "Unforeseeable", "Beyond control"],
                    "other": None,
                },
            },
            {
                "name": "risk",
                "type": "score",
                "instructions": "How risky is this clause from the perspective of your company signing this contract?",
                "criteria": [
                    "No risk — standard, fair, balanced clause",
                    "Low risk — slightly one-sided but acceptable",
                    "Moderate risk — notable concerns, review recommended",
                    "High risk — significantly one-sided, negotiate before signing",
                    "Extreme risk — dangerous, do not sign without legal counsel",
                ],
            },
            {
                "name": "needs_lawyer",
                "type": "noul",
                "instructions": "Should a lawyer review this clause before signing?",
            },
        ],
        "claude_prompt": (
            "Classify the following contract clause excerpt.\n"
            "Evaluate from the perspective of YOUR COMPANY signing this contract.\n\n"
            "Clause types: liability_cap, indemnification, termination, ip_assignment, "
            "non_compete, confidentiality, payment_terms, force_majeure, other\n"
            "Risk: 0.0 (no risk, standard) to 1.0 (extreme risk, do not sign)\n"
            "Needs lawyer: true if legal review is recommended before signing\n\n"
            "Clause: \"{text}\"\n\n"
            "Return ONLY valid JSON:\n"
            '{"clause_type": "<type>", "clause_type_confidence": <0.0-1.0>, '
            '"risk": <0.0-1.0>, "risk_confidence": <0.0-1.0>, '
            '"needs_lawyer": <true|false>, "needs_lawyer_confidence": <0.0-1.0>}'
        ),
        "scoring": {"clause_type": "exact", "risk": "continuous", "needs_lawyer": "exact"},
        "cases": [
            {
                "id": 1,
                "text": "Contractor assigns all intellectual property created during the engagement, including any derivative works, to Company in perpetuity.",
                "ground_truth": {"clause_type": "ip_assignment", "risk": 0.9, "needs_lawyer": True},
            },
            {
                "id": 2,
                "text": "Either party may terminate this agreement with 30 days written notice.",
                "ground_truth": {"clause_type": "termination", "risk": 0.1, "needs_lawyer": False},
            },
            {
                "id": 3,
                "text": "Company shall not be liable for any indirect, incidental, or consequential damages, regardless of the cause of action or theory of liability.",
                "ground_truth": {"clause_type": "liability_cap", "risk": 0.8, "needs_lawyer": True},
            },
            {
                "id": 4,
                "text": "Contractor agrees not to engage in any business activity that competes with Company, directly or indirectly, for a period of 24 months following termination, within a 100-mile radius of any Company office.",
                "ground_truth": {"clause_type": "non_compete", "risk": 0.85, "needs_lawyer": True},
            },
            {
                "id": 5,
                "text": "All confidential information shall be returned or destroyed within 30 days of agreement termination.",
                "ground_truth": {"clause_type": "confidentiality", "risk": 0.2, "needs_lawyer": False},
            },
            {
                "id": 6,
                "text": "Contractor shall indemnify, defend, and hold harmless Company from any and all claims, damages, losses, and expenses, including attorney's fees, arising from Contractor's performance of services.",
                "ground_truth": {"clause_type": "indemnification", "risk": 0.7, "needs_lawyer": True},
            },
            {
                "id": 7,
                "text": "Payment shall be made within 60 days of invoice receipt. Late payments shall accrue interest at the rate of 1.5% per month.",
                "ground_truth": {"clause_type": "payment_terms", "risk": 0.4, "needs_lawyer": False},
            },
            {
                "id": 8,
                "text": "Neither party shall be liable for delays caused by events beyond reasonable control, including but not limited to natural disasters, war, pandemic, or government action.",
                "ground_truth": {"clause_type": "force_majeure", "risk": 0.1, "needs_lawyer": False},
            },
            {
                "id": 9,
                "text": "Company retains the right to modify the terms of this agreement at any time with 5 business days' written notice. Contractor's continued performance after such notice constitutes acceptance.",
                "ground_truth": {"clause_type": "other", "risk": 0.9, "needs_lawyer": True},
            },
            {
                "id": 10,
                "text": "Contractor's total liability under this agreement shall not exceed the fees paid to Contractor in the 12 months preceding the claim.",
                "ground_truth": {"clause_type": "liability_cap", "risk": 0.3, "needs_lawyer": False},
            },
            {
                "id": 11,
                "text": "Upon termination for cause, all licenses granted hereunder shall immediately terminate. Upon termination for convenience, licenses shall survive for the remainder of the originally contemplated term.",
                "ground_truth": {"clause_type": "termination", "risk": 0.3, "needs_lawyer": False},
            },
            {
                "id": 12,
                "text": "Contractor shall not, for a period of 12 months, solicit or hire any employee of Company with whom Contractor had material contact during the engagement.",
                "ground_truth": {"clause_type": "non_compete", "risk": 0.4, "needs_lawyer": False},
            },
            {
                "id": 13,
                "text": "Company may assign this agreement to any successor entity without consent. Contractor may not assign without prior written consent, which shall not be unreasonably withheld.",
                "ground_truth": {"clause_type": "other", "risk": 0.5, "needs_lawyer": True},
            },
            {
                "id": 14,
                "text": "Any intellectual property that Contractor develops independently, outside the scope of this agreement, and without use of Company's resources, shall remain the sole property of Contractor.",
                "ground_truth": {"clause_type": "ip_assignment", "risk": 0.15, "needs_lawyer": False},
            },
            {
                "id": 15,
                "text": "Contractor agrees to keep all Company trade secrets, customer lists, and technical documentation strictly confidential for 5 years after termination. Any breach shall result in liquidated damages of $500,000.",
                "ground_truth": {"clause_type": "confidentiality", "risk": 0.7, "needs_lawyer": True},
            },
            {
                "id": 16,
                "text": "All disputes shall be resolved through binding arbitration in Company's home jurisdiction. Each party shall bear its own legal costs.",
                "ground_truth": {"clause_type": "other", "risk": 0.6, "needs_lawyer": True},
            },
            {
                "id": 17,
                "text": "Payment of 50% of project fees is due upon execution. The remaining 50% is due upon delivery. Company may withhold final payment for up to 90 days pending quality review.",
                "ground_truth": {"clause_type": "payment_terms", "risk": 0.6, "needs_lawyer": True},
            },
            {
                "id": 18,
                "text": "In the event of a force majeure lasting more than 180 days, either party may terminate this agreement immediately. All work completed to date shall be compensated on a pro-rata basis.",
                "ground_truth": {"clause_type": "force_majeure", "risk": 0.15, "needs_lawyer": False},
            },
            {
                "id": 19,
                "text": "Contractor shall indemnify Company against all third-party intellectual property infringement claims related to the deliverables, including payment of any resulting damages, settlements, and legal fees.",
                "ground_truth": {"clause_type": "indemnification", "risk": 0.8, "needs_lawyer": True},
            },
            {
                "id": 20,
                "text": "Company grants Contractor a non-exclusive, revocable license to use Company's branding and trademarks solely for performing services under this agreement. Company may revoke this license at any time for any reason.",
                "ground_truth": {"clause_type": "other", "risk": 0.3, "needs_lawyer": False},
            },
        ],
    },
}

PRIORITY_ORDER = ["P0", "P1", "P2", "P3", "P4"]
