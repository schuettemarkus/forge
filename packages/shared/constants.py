from __future__ import annotations

from typing import List

VERSION = "0.1.0"

IP_BLOCKLIST: List[str] = [
    "disney", "marvel", "dc comics", "batman", "superman", "spider-man",
    "pokemon", "pikachu", "nintendo", "mario", "zelda", "kirby",
    "star wars", "lucasfilm", "mandalorian", "baby yoda", "grogu",
    "harry potter", "hogwarts", "wizarding world",
    "hello kitty", "sanrio", "pusheen",
    "lego", "barbie", "hot wheels", "transformers", "gi joe",
    "my little pony", "care bears", "sesame street",
    "mickey mouse", "frozen", "elsa", "moana", "pixar",
    "nfl", "nba", "mlb", "nhl", "fifa", "mls",
    "coca-cola", "pepsi", "nike", "adidas", "supreme",
    "louis vuitton", "gucci", "chanel", "hermes",
    "apple", "google", "tesla", "ferrari", "lamborghini",
    "fortnite", "minecraft", "roblox", "among us",
    "one piece", "naruto", "dragon ball", "anime",
    "spongebob", "paw patrol", "peppa pig",
]

EXCLUDED_CATEGORIES: List[str] = [
    "firearms", "weapons", "gun accessories", "ammunition",
    "religious", "political", "adult", "drug paraphernalia",
    "tobacco", "vaping", "knives", "brass knuckles",
]

ALLOWED_LICENSES: List[str] = [
    "CC0", "CC-BY", "CC-BY-SA",
    "CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0",
]

# Profit guardrails
MARGIN_FLOOR_PCT = 40
MAX_PRINT_TIME_HOURS_DEFAULT = 6
HIGH_VALUE_PRICE_THRESHOLD_C = 6000  # $60 in cents
RETURN_RATE_PAUSE_PCT = 8

# Marketplace limits
ETSY_TAG_LIMIT = 13
ETSY_TITLE_CHAR_LIMIT = 140

# Printer specs (Bambu P1S)
BUILD_PLATE_MM = (256, 256, 256)
MIN_WALL_THICKNESS_MM = 1.2
OVERHANG_ANGLE_DEG = 45
WASTE_FACTOR = 1.05

# Listing quality
BANNED_LISTING_WORDS: List[str] = [
    "amazing", "perfect", "best", "incredible", "unbelievable",
    "miracle", "revolutionary", "stunning", "breathtaking",
    "game-changer", "must-have", "life-changing",
]
