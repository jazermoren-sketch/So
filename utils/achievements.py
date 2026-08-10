ACHIEVEMENTS = {

    # الانتصارات
    "win_1": "🥇 أول انتصار",
    "win_5": "🔥 خمس انتصارات",
    "win_10": "🏆 عشر انتصارات",
    "win_25": "👑 ملك UNO",
    "win_50": "🌟 أسطورة UNO",
    "win_100": "💎 سيد UNO",

    # المباريات
    "games_10": "🎮 لعبت 10 مباريات",
    "games_50": "⚡ لعبت 50 مباراة",
    "games_100": "🎯 مخضرم UNO",

    # الذكاء الاصطناعي
    "bot_1": "🤖 هزمت أول بوت",
    "bot_10": "💀 قاتل البوتات",

    # أوراق خاصة
    "wild_10": "🃏 سيد Wild",
    "draw4_10": "☠️ سيد +4",

    # الفوز السريع
    "speed": "⚡ فوز سريع",

    # الفوز المثالي
    "perfect": "👑 فوز مثالي"
}


def check_achievements(stats):

    unlocked = []

    wins = stats.get(
        "wins",
        0
    )

    games = stats.get(
        "games",
        0
    )

    bots = stats.get(
        "bots",
        0
    )

    wild = stats.get(
        "wild",
        0
    )

    draw4 = stats.get(
        "draw4",
        0
    )

    if wins == 1:
        unlocked.append(
            ACHIEVEMENTS["win_1"]
        )

   