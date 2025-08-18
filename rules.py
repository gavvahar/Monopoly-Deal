# rules.py
"""
Function-based Monopoly Deal (US) rules.
Import what you need: set sizes, rent, turn limits, builds, JSN stack, etc.
"""

from typing import Dict, List, Tuple, Union

# -------------------- getters for rule data --------------------


def get_set_sizes() -> Dict[str, int]:
    """Return the number of properties required for each color set."""
    return {
        "Brown": 2,
        "Light Blue": 3,
        "Pink": 3,
        "Orange": 3,
        "Red": 3,
        "Yellow": 3,
        "Green": 3,
        "Dark Blue": 2,
        "Railroads": 4,
        "Utilities": 2,
    }


def get_rent_table() -> Dict[str, List[int]]:
    """Return rent values for each color set based on number owned."""
    # Index = number of properties owned (1..set_size)
    return {
        "Brown": [1, 2],
        "Light Blue": [1, 2, 3],
        "Pink": [1, 2, 4],
        "Orange": [1, 3, 5],
        "Red": [2, 3, 6],
        "Yellow": [2, 4, 6],
        "Green": [2, 4, 7],
        "Dark Blue": [3, 8],
        "Railroads": [1, 2, 3, 4],
        "Utilities": [1, 2],
    }


def get_build_eligible_colors() -> List[str]:
    """Return colors eligible for building houses/hotels."""
    # Houses/Hotels only on color sets (not rail/utility)
    return [c for c in get_set_sizes() if c not in {"Railroads", "Utilities"}]


def get_turn_limits() -> Dict[str, int]:
    """Return turn limits for drawing, playing, and hand size."""
    # draw_default=2; if starting hand is 0, draw 5. Max plays=3, hand limit=7.
    return {"draw_default": 2, "draw_if_empty": 5, "max_plays": 3, "hand_limit": 7}


def get_action_kinds() -> Dict[str, str]:
    """Return target semantics for common action cards."""
    # Target semantics for common actions
    return {
        "Sly Deal": "single",
        "Debt Collector": "single",
        "Forced Deal": "single",
        "It’s My Birthday": "all",
        "Deal Breaker": "steal_set",
        # rent cards marked separately via get_rent_card_colors()
    }


def get_rent_card_colors() -> Dict[str, List[str]]:
    """Return mapping of rent cards to color sets."""
    s = list(get_set_sizes().keys())
    return {
        "Rent Brown/Light Blue": ["Brown", "Light Blue"],
        "Rent Pink/Orange": ["Pink", "Orange"],
        "Rent Red/Yellow": ["Red", "Yellow"],
        "Rent Green/Dark Blue": ["Green", "Dark Blue"],
        "Rent Railroad/Utility": ["Railroads", "Utilities"],
        "Rent Wild (Any Color)": s,
    }


def get_rule_flags() -> Dict[str, bool]:
    """Return rule flags for game tweaks."""
    # Tweak as you like (or override in your app)
    return {
        "limit_double_rent_to_one": False,  # True = only 1 Double per rent
        "sly_deal_on_full_sets": False,  # Officially not allowed
        "forced_deal_on_full_sets": False,  # Officially not allowed
    }


def get_build_bonuses() -> Tuple[int, int]:
    """Return house and hotel rent bonuses."""
    # (house_bonus, hotel_bonus)
    return (3, 4)


# -------------------- turn & hand helpers --------------------


def draw_count(hand_size: int) -> int:
    """Return number of cards to draw based on hand size."""
    limits = get_turn_limits()
    return limits["draw_if_empty"] if hand_size == 0 else limits["draw_default"]


def must_discard(hand_size_after_plays: int) -> bool:
    """Return True if player must discard after plays."""
    return hand_size_after_plays > get_turn_limits()["hand_limit"]


# -------------------- property & build rules --------------------


def is_full_set(color: str, owned_in_color: int) -> bool:
    """Return True if player owns a full set of the given color."""
    return owned_in_color >= get_set_sizes()[color]


def can_build_house(
    color: str, owned_in_color: int, has_house: bool, has_hotel: bool
) -> bool:
    """Return True if player can build a house on the set."""
    if color not in get_build_eligible_colors():
        return False
    if not is_full_set(color, owned_in_color):
        return False
    return not (has_house or has_hotel)


def can_build_hotel(
    color: str, owned_in_color: int, has_house: bool, has_hotel: bool
) -> bool:
    """Return True if player can build a hotel on the set."""
    if color not in get_build_eligible_colors():
        return False
    if not is_full_set(color, owned_in_color):
        return False
    return has_house and not has_hotel


# -------------------- rent computation --------------------


def base_rent(color: str, owned_in_color: int) -> int:
    """Return base rent for a color set."""
    sizes, table = get_set_sizes(), get_rent_table()
    owned = max(1, min(owned_in_color, sizes[color]))
    return table[color][owned - 1]


def apply_build_bonuses(
    color: str, owned_in_color: int, has_house: bool, has_hotel: bool, current_rent: int
) -> int:
    """Apply house/hotel bonuses to rent if eligible."""
    if not is_full_set(color, owned_in_color):
        return current_rent
    if color not in get_build_eligible_colors():
        return current_rent
    house_bonus, hotel_bonus = get_build_bonuses()
    if has_house:
        current_rent += house_bonus
    if has_hotel:
        current_rent += hotel_bonus
    return current_rent


def cap_double_rent(double_count: int) -> int:
    """Cap the number of Double the Rent cards applied."""
    if get_rule_flags()["limit_double_rent_to_one"]:
        return min(1, double_count)
    return max(0, int(double_count))


def compute_rent(
    color: str,
    owned_in_color: int,
    has_house: bool = False,
    has_hotel: bool = False,
    double_rent_cards: int = 0,
) -> int:
    """Compute total rent for a set, including bonuses and doubles."""
    rent = base_rent(color, owned_in_color)
    rent = apply_build_bonuses(color, owned_in_color, has_house, has_hotel, rent)
    for _ in range(cap_double_rent(double_rent_cards)):
        rent *= 2
    return rent


# -------------------- action helpers --------------------


def action_targets(card_name: str) -> str:
    """
    Returns: 'single' | 'all' | 'steal_set' | 'rent' | 'none'
    """
    kinds = get_action_kinds()
    if card_name in kinds:
        return kinds[card_name]
    if card_name in get_rent_card_colors():
        return "rent"
    return "none"


def rent_colors_for_card(card_name: str) -> List[str]:
    """Return color sets affected by a rent card."""
    return get_rent_card_colors().get(card_name, [])


def is_double_rent(card_name: str) -> bool:
    """Return True if card is Double the Rent."""
    return card_name == "Double the Rent"


def is_just_say_no(card_name: str) -> bool:
    """Return True if card is Just Say No."""
    return card_name == "Just Say No"


# -------------------- Just Say No stack resolution --------------------


def resolve_just_say_no_stack(responses_in_order: List[str]) -> bool:
    """
    True if the original action takes effect, False if canceled.
    Parity rule: even # of JSN -> action stands; odd -> canceled.
    """
    jsn = sum(1 for c in responses_in_order if c == "Just Say No")
    return (jsn % 2) == 0


# -------------------- payment helpers --------------------


def payment_options_summary(
    bank_total: int, property_values: List[int]
) -> Tuple[int, List[int]]:
    """Return summary of payment options (bank and sorted properties)."""
    return bank_total, sorted(property_values, reverse=True)


def choose_payment(
    amount_due: int, bank_total: int, property_values: List[int]
) -> Dict[str, Union[List[int], int]]:
    """
    Greedy example: use bank first, then largest properties until paid(overpay allowed).
    Replace with UI-driven selection in your app if desired.
    """
    paid = min(bank_total, amount_due)
    remaining = amount_due - paid
    taken: List[int] = []
    for v in sorted(property_values, reverse=True):
        if remaining <= 0:
            break
        taken.append(v)
        remaining -= v
        paid += v
    return {
        "bank_used": min(bank_total, amount_due),
        "properties_taken": taken,
        "total_paid": paid,
    }
