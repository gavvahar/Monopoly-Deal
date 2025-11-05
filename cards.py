"""
Monopoly Deal card definitions and deck builder.
"""

from collections import Counter
import random

ALL_PROPERTY_COLORS = [
    "Lexus",
    "Tesla",
    "Rivian",
    "Chevelote",
    "Nissan",
    "Ford",
    "Benz",
    "Lamborghini",
    "McLaren",
    "Bugatti",
]

PROPERTY_SET_DEFINITIONS = {
    "Lexus": [
        ("Lexus IS 500 F SPORT", 1),
        ("Lexus RX 500h F SPORT", 1),
    ],
    "Tesla": [
        ("Tesla Model 3 Performance", 1),
        ("Tesla Model Y Performance", 1),
        ("Tesla Model S Plaid", 1),
    ],
    "Rivian": [
        ("Rivian R1T Adventure", 2),
        ("Rivian R1S Launch Edition", 2),
        ("Rivian Electric Delivery Van", 2),
    ],
    "Chevelote": [
        ("Chevelote Corvette Z06", 2),
        ("Chevelote Camaro ZL1", 2),
        ("Chevelote Silverado Trail Boss", 2),
    ],
    "Nissan": [
        ("Nissan Skyline GT-R (R34 Paul Walker)", 3),
        ("Nissan GT-R (R35)", 3),
        ("Nissan 370Z Nismo", 3),
    ],
    "Ford": [
        ("Ford Mustang Shelby GT500 (1967)", 3),
        ("Ford GT Heritage Edition", 3),
        ("Ford F-150 Raptor", 3),
    ],
    "Benz": [
        ("Mercedes-AMG GT Black Series", 4),
        ("Mercedes-Benz G63 AMG", 4),
        ("Mercedes-Maybach S 680", 4),
    ],
    "Lamborghini": [
        ("Lamborghini Sesto Elemento", 4),
        ("Lamborghini Aventador SVJ", 4),
    ],
    "McLaren": [
        ("McLaren F1", 2),
        ("McLaren P1", 2),
        ("McLaren 720S", 2),
        ("McLaren 765LT", 2),
    ],
    "Bugatti": [
        ("Bugatti Veyron 16.4", 2),
        ("Bugatti Chiron Super Sport", 2),
    ],
}

PROPERTY_WILD_DEFINITIONS = [
    {
        "name": "Wild Lexus/Tesla",
        "colors": ("Lexus", "Tesla"),
        "value": 4,
        "count": 1,
    },
    {
        "name": "Wild Rivian/Chevelote",
        "colors": ("Rivian", "Chevelote"),
        "value": 2,
        "count": 2,
    },
    {
        "name": "Wild Nissan/Ford",
        "colors": ("Nissan", "Ford"),
        "value": 3,
        "count": 2,
    },
    {
        "name": "Wild Benz/Lamborghini",
        "colors": ("Benz", "Lamborghini"),
        "value": 4,
        "count": 2,
    },
    {
        "name": "Wild Tesla/McLaren",
        "colors": ("Tesla", "McLaren"),
        "value": 4,
        "count": 1,
    },
    {
        "name": "Wild McLaren",
        "colors": ("McLaren",),
        "value": 2,
        "count": 2,
    },
    {
        "name": "Wild McLaren/Bugatti",
        "colors": ("McLaren", "Bugatti"),
        "value": 2,
        "count": 1,
    },
    {
        "name": "Wild Bugatti",
        "colors": ("Bugatti",),
        "value": 2,
        "count": 1,
    },
    {
        "name": "Wild Garage Pass (Any Collection)",
        "colors": tuple(ALL_PROPERTY_COLORS),
        "value": 0,
        "count": 2,
    },
]

MONEY_CARD_DEFINITIONS = {
    "1M": {"count": 6, "value": 1, "type": "money"},
    "2M": {"count": 5, "value": 2, "type": "money"},
    "3M": {"count": 3, "value": 3, "type": "money"},
    "4M": {"count": 3, "value": 4, "type": "money"},
    "5M": {"count": 2, "value": 5, "type": "money"},
    "10M": {"count": 1, "value": 10, "type": "money"},
}

ACTION_CARD_DEFINITIONS = {
    "Garage Takeover": {"count": 2, "value": 5, "type": "action"},
    "Sneak Swap": {"count": 2, "value": 3, "type": "action"},
    "Tow Trade": {"count": 4, "value": 3, "type": "action"},
    "Repo Notice": {"count": 3, "value": 3, "type": "action"},
    "Track Day Fees": {"count": 3, "value": 2, "type": "action"},
    "Green Light": {"count": 8, "value": 1, "type": "action"},
    "Turbo Charge": {"count": 2, "value": 1, "type": "action"},
    "Garage Upgrade": {"count": 3, "value": 3, "type": "action"},
    "Luxury Showroom": {"count": 2, "value": 4, "type": "action"},
    "Cut the Engine": {"count": 3, "value": 4, "type": "action"},
    "Pit Crew Bonus": {"count": 1, "value": 2, "type": "action"},
    "Midnight Run": {"count": 1, "value": 3, "type": "action"},
    "Collector's Auction": {"count": 1, "value": 4, "type": "action"},
}

RENT_CARD_DEFINITIONS = {
    "Rent Lexus/Tesla": {"count": 2, "value": 1, "type": "rent"},
    "Rent Rivian/Chevelote": {"count": 2, "value": 1, "type": "rent"},
    "Rent Nissan/Ford": {"count": 2, "value": 1, "type": "rent"},
    "Rent Benz/Lamborghini": {"count": 2, "value": 1, "type": "rent"},
    "Rent McLaren/Bugatti": {"count": 2, "value": 1, "type": "rent"},
    "Rent Wild (Any Collection)": {"count": 3, "value": 3, "type": "rent"},
}


def money_cards():
    """Return dictionary of money cards."""
    return {name: dict(data) for name, data in MONEY_CARD_DEFINITIONS.items()}


def property_cards():
    """Return dictionary of property cards keyed by card name."""
    cards = {}
    for color, entries in PROPERTY_SET_DEFINITIONS.items():
        for name, value in entries:
            cards[name] = {
                "count": 1,
                "value": value,
                "type": "property",
                "color": color,
            }
    return cards


def property_wilds():
    """Return dictionary of property wild cards keyed by card name."""
    cards = {}
    for wild in PROPERTY_WILD_DEFINITIONS:
        cards[wild["name"]] = {
            "count": wild["count"],
            "value": wild["value"],
            "type": "wild",
            "colors": list(wild["colors"]),
        }
    return cards


def action_cards():
    """Return dictionary of action cards."""
    return {name: dict(data) for name, data in ACTION_CARD_DEFINITIONS.items()}


def rent_cards():
    """Return dictionary of rent cards."""
    return {name: dict(data) for name, data in RENT_CARD_DEFINITIONS.items()}


def _expand_group(deck, definitions):
    for name, data in definitions.items():
        count = data["count"]
        template = {k: v for k, v in data.items() if k != "count"}
        template["name"] = name
        for _ in range(count):
            card = dict(template)
            if "colors" in template:
                card["colors"] = list(template["colors"])
            deck.append(card)


def build_deck():
    """Return the full deck of 110 cards as a list of dicts."""
    deck = []
    for group in (
        money_cards(),
        property_cards(),
        property_wilds(),
        action_cards(),
        rent_cards(),
    ):
        _expand_group(deck, group)
    return deck


def shuffle_deck():
    """Return a shuffled deck."""
    deck = build_deck()
    random.shuffle(deck)
    return deck


if __name__ == "__main__":
    deck_list = build_deck()
    print(f"Total cards: {len(deck_list)}")
    print(Counter(c["type"] for c in deck_list))
