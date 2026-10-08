"""
generate_data.py
Generates 1000 realistic synthetic social media posts across 5 platforms.
Run once: python generate_data.py
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

# ── Platforms & usernames ──────────────────────────────────────────────
PLATFORMS = {
    "Twitter": [
        "@techie_sam", "@daily_john", "@sara_codes", "@foodlover_tia", "@sports_raj",
        "@news_priya", "@dev_arjun", "@travel_neha", "@health_mike", "@startup_vik",
        "@political_eye", "@music_fan99", "@movie_buff_k", "@fitness_guru", "@eco_watch",
        "@comedy_central", "@bookworm_z", "@gamer_pro", "@art_lover_m", "@crypto_watch",
    ],
    "Reddit": [
        "u/techreview_pro", "u/daily_rants", "u/just_browsing", "u/critic_x", "u/coder_life",
        "u/gadget_nerd", "u/neutral_views", "u/book_club", "u/everyday_guy", "u/movie_lover",
        "u/science_geek", "u/history_buff", "u/gaming_life", "u/food_talk", "u/travel_diary",
        "u/finance_guru", "u/fitness_nerd", "u/music_theory", "u/art_discuss", "u/philosophy_q",
    ],
    "Instagram": [
        "@foodie_kai", "@travel_vibes", "@fitness_raj", "@daily_moods", "@techgirl_p",
        "@lifestyle_n", "@naturelover", "@student_life", "@fashionista_z", "@chef_arjun",
        "@beauty_glam", "@adventure_k", "@home_decor_r", "@pet_lovers", "@yoga_daily",
        "@street_style", "@sunset_views", "@coffee_addict", "@gym_life", "@art_studio",
    ],
    "Facebook": [
        "@john.smith", "@priya.patel", "@community.page", "@ramesh.kumar", "@anjali.mehta",
        "@tech.updates", "@sports.fans", "@parent.life", "@review.hub", "@news.today",
        "@local.events", "@cooking.tips", "@travel.group", "@health.tips", "@career.advice",
        "@family.moments", "@pets.corner", "@business.talk", "@education.hub", "@culture.page",
    ],
    "YouTube": [
        "@techreviewer", "@gaming_hero", "@cooking_sneha", "@fitness_guru", "@movie_critic",
        "@tech_help", "@travel_vlog", "@music_lover", "@product_review", "@comedy_show",
        "@science_explain", "@history_now", "@diy_projects", "@beauty_tips", "@finance_101",
        "@language_learn", "@news_analysis", "@sports_recap", "@art_tutorials", "@book_review",
    ],
}

# ── Post templates by sentiment ────────────────────────────────────────
POSITIVE_POSTS = [
    # Twitter
    "Just had the most incredible experience at {place}! Absolutely loved every moment of it",
    "Cannot believe how amazing {product} is. Best purchase I have made this year hands down!",
    "So proud of {achievement}! Hard work really does pay off in the end",
    "This {event} was absolutely phenomenal. The energy and atmosphere were unreal!",
    "Finally visited {place} and it exceeded every single expectation I had. Stunning!",
    "Huge shoutout to {person} for being so incredibly helpful and kind. You made my day!",
    "Just finished {book} and it is genuinely one of the best things I have ever read",
    "This new {product} update is exactly what we needed. Such a massive improvement!",
    "Woke up feeling incredibly grateful today. Life is truly beautiful when you appreciate it",
    "Just got promoted at work! Years of hard work finally recognized. Feeling on top of the world!",
    "The sunset tonight was absolutely breathtaking. Nature never fails to amaze me",
    "Had the best workout session today. Feeling strong motivated and unstoppable!",
    "My team won the championship today! Years of training finally paid off. So proud!",
    "Just launched my small business and the response has been overwhelmingly positive. Thank you all!",
    "Reunited with old friends after 5 years. Some bonds truly never break. Feeling so happy!",
    "This {food} recipe turned out absolutely perfect. The whole family loved it!",
    "Got accepted into my dream university! All those late nights studying were worth it!",
    "The concert last night was absolutely electrifying. Best live performance I have ever seen!",
    "Adopted a puppy today and my heart has never been this full of joy and love",
    "Just completed my first marathon! Never thought I could do it but here we are!",
]

NEGATIVE_POSTS = [
    "Absolutely terrible experience at {place}. Never going back there again. Avoid at all costs!",
    "This {product} is complete garbage. Stopped working after just two days. Total waste of money!",
    "Worst customer service I have ever experienced in my life. Completely ignored and disrespected.",
    "Cannot believe how badly {company} has gone downhill. Used to love them but not anymore.",
    "Third time my order arrived damaged. This company clearly does not care about its customers.",
    "So frustrated with {product} right now. Constant crashes terrible performance and no support.",
    "The traffic today was absolutely horrific. Took me 3 hours to travel just 15 kilometers.",
    "Failed my exam after weeks of preparation. Feeling completely devastated and hopeless right now.",
    "My flight got cancelled with zero notice and no compensation offered. Absolutely disgraceful!",
    "This movie was one of the worst things I have ever watched. Complete waste of two hours.",
    "Internet has been down for 6 hours and customer support keeps putting me on hold. Unacceptable!",
    "Ordered food an hour ago and it still has not arrived. Completely cold when it finally came.",
    "Got scammed online today. Lost a significant amount of money. Feeling so stupid and angry.",
    "This new software update completely ruined everything that was working perfectly before.",
    "Terrible weather ruined our entire outdoor event after months of careful planning.",
    "My landlord is refusing to fix the heating in winter. This is completely unacceptable behavior.",
    "Lost all my work because the app crashed without saving. No autosave feature is inexcusable.",
    "The new management has completely destroyed the company culture. Everyone is miserable now.",
    "Received my package completely destroyed. The packaging was absolutely appalling.",
    "This subscription service charged me twice and refuses to issue a refund. Total scam!",
]

NEUTRAL_POSTS = [
    "Just finished watching {show}. It was okay I guess. Nothing special but not terrible either.",
    "Tried the new {food} place downtown. Decent enough but nothing to write home about really.",
    "The weather today is pretty average. Not great not terrible. Just a regular day.",
    "Read through the new policy update. Some changes seem okay others not so much.",
    "New {product} arrived today. Setting it up now. Will share thoughts once I have used it more.",
    "Monday again. Another week another set of meetings and deadlines to deal with.",
    "The movie was alright. Had some good moments but the ending felt a bit rushed overall.",
    "Attended the workshop today. Learned a few things but mostly stuff I already knew.",
    "New software update installed. Interface looks different. Will take some getting used to.",
    "The restaurant was fine. Service was average and food was neither great nor bad.",
    "Finished the quarterly report. Same numbers as last quarter more or less. Nothing surprising.",
    "Commute was about the same as usual today. Nothing particularly good or bad happened.",
    "Checked out the new app everyone is talking about. It is functional but nothing revolutionary.",
    "The meeting ran a bit long but we covered everything on the agenda at least.",
    "Tried a new workout routine today. It was okay. Might stick with it for a week and see.",
    "Read the book everyone recommended. It was fine. Decent writing but the story was predictable.",
    "New phone update came through. Changed a few things. Some better some worse overall.",
    "The conference was informative. Met some people exchanged cards. Standard industry event.",
    "Ordered from a new restaurant. Food arrived on time and was acceptable. Nothing memorable.",
    "Checked out the new park that opened nearby. It is nice enough. Good for a short walk.",
]

# ── Topics to fill placeholders ────────────────────────────────────────
PLACES    = ["that new Italian restaurant", "the local coffee shop", "the mountain trail", "that rooftop bar", "the new shopping mall", "the beach resort", "the art gallery", "that cozy bookstore"]
PRODUCTS  = ["iPhone 16", "Samsung Galaxy S24", "MacBook Pro", "this budget laptop", "the new smartwatch", "these wireless earbuds", "this coffee maker", "the new gaming console"]
EVENTS    = ["music festival", "tech conference", "cricket match", "football final", "comedy show", "art exhibition", "food festival", "startup pitch event"]
FOODS     = ["pasta", "biryani", "sushi", "tacos", "pizza", "burger", "noodle soup", "chocolate cake"]
SHOWS     = ["that Netflix series", "the new web show", "that documentary", "the anime everyone recommended", "that crime thriller show"]
PERSONS   = ["my colleague", "the customer support agent", "my professor", "my team lead", "the delivery person"]
BOOKS     = ["that self-help book", "the sci-fi novel everyone recommended", "that thriller", "the biography"]
ACHIEVEMENTS = ["completing my certification", "finishing the project on time", "getting a perfect score", "running my first half-marathon"]
COMPANIES  = ["this telecom provider", "that food delivery app", "this e-commerce site", "that streaming platform"]

def fill_template(template):
    return (template
        .replace("{place}",       random.choice(PLACES))
        .replace("{product}",     random.choice(PRODUCTS))
        .replace("{event}",       random.choice(EVENTS))
        .replace("{food}",        random.choice(FOODS))
        .replace("{show}",        random.choice(SHOWS))
        .replace("{person}",      random.choice(PERSONS))
        .replace("{book}",        random.choice(BOOKS))
        .replace("{achievement}", random.choice(ACHIEVEMENTS))
        .replace("{company}",     random.choice(COMPANIES))
    )

# ── Date range ─────────────────────────────────────────────────────────
START_DATE = datetime(2024, 1, 1, 8, 0, 0)

def random_timestamp(index):
    offset = timedelta(hours=index * 2.5)
    dt = START_DATE + offset
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# ── Generate posts ─────────────────────────────────────────────────────
def generate_posts(total=1000):
    posts = []
    platforms = list(PLATFORMS.keys())

    # Sentiment distribution: 45% positive, 30% neutral, 25% negative
    sentiments = (
        ["positive"] * 450 +
        ["neutral"]  * 300 +
        ["negative"] * 250
    )
    random.shuffle(sentiments)

    per_platform = total // len(platforms)  # 200 per platform

    idx = 1
    for platform in platforms:
        usernames = PLATFORMS[platform]
        platform_sentiments = sentiments[(idx - 1) % len(sentiments):(idx - 1 + per_platform) % len(sentiments) or per_platform]

        for i in range(per_platform):
            sentiment = sentiments[idx % len(sentiments)]
            if sentiment == "positive":
                text = fill_template(random.choice(POSITIVE_POSTS))
            elif sentiment == "negative":
                text = fill_template(random.choice(NEGATIVE_POSTS))
            else:
                text = fill_template(random.choice(NEUTRAL_POSTS))

            username = random.choice(usernames)
            likes    = random.randint(5, 8000)
            shares   = random.randint(0, likes // 3 + 1)
            ts       = random_timestamp(idx)

            posts.append({
                "id":        idx,
                "platform":  platform,
                "username":  username,
                "text":      text,
                "timestamp": ts,
                "likes":     likes,
                "shares":    shares,
            })
            idx += 1

    return posts

# ── Write CSV ──────────────────────────────────────────────────────────
def write_csv(posts, path="data/sample_posts.csv"):
    fieldnames = ["id", "platform", "username", "text", "timestamp", "likes", "shares"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts)
    print(f"Written {len(posts)} posts to {path}")
    import os
    size = os.path.getsize(path)
    print(f"File size: {size:,} bytes ({size/1024:.1f} KB)")

if __name__ == "__main__":
    posts = generate_posts(1000)
    write_csv(posts)
