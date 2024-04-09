import csv
import json
import os

cats = {
    "acg",
    "adv",
    "ai",
    "baby",
    "beauty",
    "cross-platform",
    "dinosaurs",
    "happy diwali",
    "hearing assistance",
    "kids",
    "libraries & demo",
    "lifestyle",
    "parenting"
    "renovate & decorat",
    "rummy",
    "translation",
    "visual assistance",
    "weather",
}

learning = {
    "coaching",
    "language",
    "learning disability",
    "learning",
    "mathematics",
    "physics",
    "piano",
}

social_media = {
    "calling",
    "chat",
    "communication",
    "community",
    "dating",
    "facebook messenger",
    "instant messaging",
    "meeting",
    "messenger",
    "social networking",
    "social",
}

sports = {
    "auto & vehicles",
    "baseball",
    "basketball",
    "bike",
    "hockey",
    "motor assistance",
    "sports",
    "wwe",
}

multimedia = {
    "anime player",
    "anime",
    "art & design",
    "audio",
    "books & reference",
    "cartoon",
    "comics",
    "disney",
    "drawing",
    "events",
    "graphic",
    "hand-drawing",
    "harry potter",
    "hd",
    "hindi video",
    "history",
    "kawaii",
    "live channels",
    "live streaming",
    "live tv",
    "movies",
    "mp3 converter",
    "multi-language",
    "multimedia",
    "music & audio",
    "music sim",
    "music",
    "novel updates",
    "online movie",
    "photo editing",
    "photo editor",
    "photography",
    "sci fi",
    "sci-fi",
    "short video",
    "video calling",
    "video game live streaming",
    "video players & editors",
    "watch live sports",
    "youtube downloader",
}

health = {
    "doctor",
    "health & fitness",
}

office = {
    "app2sd",
    "browser",
    "business",
    "camera",
    "cloud storage",
    "email",
    "file manager",
    "finance",
    "government",
    "management",
    "merge",
    "news & magazines",
    "office",
    "pdf reader",
    "productivity",
    "programming",
    "screen recorder",
    "search",
    "security",
    "text to speech",
    "time management",
    "tool",
    "tools",
    "tps",
    "video",
    "vpn service",
    "vpn",
    "word",
    "wordpress",
}

customization = {
    "customization",
    "download tool",
    "file managers",
    "keyboards",
    "performance",
    "personalisation",
    "personalization",
    "privacy",
    "speed test",
    "video downloader",
    "wallpaper",
}

shopping = {
    "android market",
    "app store",
    "e-commerce",
    "fashion",
    "food & drink",
    "house & home",
    "play store",
    "restaurant",
    "shopping with free shipping",
    "travel & local",
    "vehicle",
}

games = {
    "1 on 1",
    "2048",
    "2d",
    "3 v 3",
    "3d",
    "4x",
    "abstract strategy",
    "abstract",
    "action adventure",
    "action role playing",
    "action role-playing",
    "action rpg",
    "action strategy",
    "action",
    "action-adventure",
    "action-strategy",
    "adventure",
    "ar game",
    "ar",
    "arcade",
    "auto-battle",
    "base building",
    "battle royale",
    "battle",
    "beta",
    "billiards",
    "bingo",
    "blackjack",
    "block",
    "board",
    "brain teaser",
    "brain training",
    "brawler",
    "breeding",
    "brick break",
    "bubble shooter",
    "build & battle",
    "build your village",
    "building",
    "bulletstorm",
    "car",
    "card battler",
    "card game",
    "card",
    "care",
    "casino adventure",
    "casino",
    "casual",
    "checkers",
    "chess",
    "city-building",
    "classic cards",
    "classic",
    "clicker",
    "collectible",
    "collecting",
    "coloring",
    "combat sports",
    "combat",
    "competitive multiplayer",
    "construction",
    "creativity",
    "cricket",
    "criminals",
    "crossword puzzle",
    "crossword",
    "crossword-puzzle",
    "cue",
    "customized character",
    "dash",
    "defence",
    "dentist",
    "domino",
    "drag racing",
    "dress up",
    "dress-up",
    "education",
    "educational games",
    "educational",
    "empire building",
    "endless abyss",
    "endless runner",
    "entertainment",
    "escape",
    "fantasy",
    "farm",
    "farming",
    "fighting",
    "first person",
    "first-person",
    "flight",
    "fps",
    "funny",
    "gacha",
    "game",
    "gaming tools",
    "gardening",
    "garena free fire",
    "go",
    "golf",
    "hack & slash",
    "handicraft",
    "hidden object",
    "horror",
    "hunting",
    "hypercasual",
    "idle rpg",
    "idle",
    "interactive story",
    "io game",
    "io",
    "jigsaw",
    "last card",
    "logic",
    "logo quiz",
    "low poly",
    "ludo",
    "maps & navigation",
    "match 3 adventure",
    "match 3 rpg",
    "match 3",
    "matching",
    "medical",
    "memory",
    "minecraft",
    "minigames",
    "mmorpg",
    "moba",
    "motorcycle",
    "mulitplayer",
    "multi-ending",
    "multi-player",
    "multiplayer battle",
    "multiplayer fps",
    "multiplayer",
    "mutiplayer",
    "offline practice",
    "offline",
    "online",
    "onlne",
    "open world",
    "p v p",
    "pair matching",
    "parking",
    "parkour",
    "party",
    "pet",
    "pixel graphics",
    "pixel",
    "pixelated",
    "platform",
    "platformer",
    "pokemon",
    "poker",
    "pubg india",
    "pubg mobile",
    "pubg",
    "puzzle role-playing",
    "puzzle",
    "puzzle-adventure",
    "pvp",
    "racing",
    "real-time",
    "realistic",
    "rhythm",
    "rhythm-action",
    "robot",
    "roguelike",
    "role playing",
    "role-playing",
    "romance",
    "rpg",
    "run & gun",
    "runner",
    "running",
    "rythm",
    "sandbox",
    "shooter",
    "shooting range",
    "shooting",
    "shopping",
    "simulation",
    "simulations",
    "single player",
    "single-player",
    "slash & kill",
    "slicing",
    "sliding",
    "slots",
    "soccer",
    "solitaire",
    "sonic",
    "stickman",
    "story telling",
    "story",
    "story-telling",
    "strategy",
    "stunt driving",
    "stylised realistic",
    "stylised",
    "stylised-realistic",
    "stylized realistic",
    "stylized",
    "stylized-realistic",
    "super heroes",
    "survival horror",
    "survival",
    "table",
    "tactical shooter",
    "tactical",
    "tactics",
    "tank",
    "third-person shooting",
    "third-person",
    "thriller",
    "tower defense",
    "trivia",
    "truck",
    "turn-based rpg",
    "turn-based",
    "tycoon",
    "vehicle combat",
    "violence",
    "waifu",
    "war",
    "wargame",
    "weapon customization",
    "weapon",
    "word jumble",
    "zombie",
}

app_cats = {}


def create_csv_with_one_hot_encoding(data_dict, output_csv):
    # Get unique values from the dictionary values
    # data_dict = {
    #     k.strip(): data_dict[k] if data_dict[k] is not None else 'other' 
    #     for k in data_dict
    # }
    unique_values = set()
    for vs in data_dict.values():
        for v in vs:
            unique_values.add(v)

    # aggregate similar categories
    unique_values = {
        "games" if v in games else
        "learning" if v in learning else
        "social media" if v in social_media else
        "sports" if v in sports else
        "multimedia" if v in multimedia else
        "health" if v in health else
        "office" if v in office else
        "customization" if v in customization else
        "shopping" if v in shopping else
        v
        for v in unique_values
    }
    unique_values = list(unique_values)

    # Write CSV header
    header = ["Key"] + unique_values
    # from pprint import pprint
    # pprint(unique_values)
    print(f"{len(header)} rows")
    with open(output_csv, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(header)

        # Write rows with one-hot encoding
        lns = 0
        for key in data_dict:
            row = [key] + [1 if data_dict[key] == val else 0 for val in unique_values]
            csv_writer.writerow(row)
            lns += 1
        print(f"Written {lns} lines")


def main():
    BASE = 'data'
    for f_name in [f for f in os.listdir(BASE) if f.startswith('app_cats_')]:
        print(f"{BASE}/{f_name}")
        with open(f"{BASE}/{f_name}") as f:
            data = json.loads(f.read())
            for k in data:
                # print(k, data[k])
                cats = [v.lower() for v in data[k]]
#                if any(c in games for c in cats):
#                    cats.append('game')
#                    cats = [v for v in data[k] if v not in games]

                app_cats[k] = cats 

    create_csv_with_one_hot_encoding(app_cats, "data/new_app_cats.csv")

if __name__ == '__main__':
    main()