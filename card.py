"""
card.py — Euchre card representation and logic.

Mirrors the C++ Card/Rank/Suit implementation, trimmed to the 24-card
euchre deck (Nine through Ace, all four suits).

CV INTEGRATION NOTES
--------------------
Two helpers exist for the computer-vision pipeline:

  Card.cv_label()   → canonical folder/class name used when building the
                       training dataset, e.g. "jack_spades".
                       ImageFolder(root) expects one sub-folder per label.

  Card.from_cv_label(label)  → reconstructs a Card from the string the
                                model predicts, e.g. "jack_spades" → Card.

The model always predicts physical rank+suit.  Bower logic (right/left)
lives here in the game layer — never in the model.

CLASS LABEL LIST (24 labels, one per training folder)
    nine_spades     nine_hearts     nine_clubs     nine_diamonds
    ten_spades      ten_hearts      ten_clubs      ten_diamonds
    jack_spades     jack_hearts     jack_clubs     jack_diamonds
    queen_spades    queen_hearts    queen_clubs    queen_diamonds
    king_spades     king_hearts     king_clubs     king_diamonds
    ace_spades      ace_hearts      ace_clubs      ace_diamonds
"""

from __future__ import annotations
from enum import IntEnum
from functools import total_ordering


# ---------------------------------------------------------------------------
# Rank
# ---------------------------------------------------------------------------

class Rank(IntEnum):
    NINE  = 0
    TEN   = 1
    JACK  = 2
    QUEEN = 3
    KING  = 4
    ACE   = 5

_RANK_NAMES: dict[Rank, str] = {
    Rank.NINE:  "Nine",
    Rank.TEN:   "Ten",
    Rank.JACK:  "Jack",
    Rank.QUEEN: "Queen",
    Rank.KING:  "King",
    Rank.ACE:   "Ace",
}

# Short lowercase token used in CV labels ("nine", "jack", …)
_RANK_CV_TOKEN: dict[Rank, str] = {
    Rank.NINE:  "nine",
    Rank.TEN:   "ten",
    Rank.JACK:  "jack",
    Rank.QUEEN: "queen",
    Rank.KING:  "king",
    Rank.ACE:   "ace",
}

_STR_TO_RANK: dict[str, Rank] = {v: k for k, v in _RANK_NAMES.items()}
_CV_TO_RANK:  dict[str, Rank] = {v: k for k, v in _RANK_CV_TOKEN.items()}


def string_to_rank(s: str) -> Rank:
    """'Nine' → Rank.NINE, etc."""
    try:
        return _STR_TO_RANK[s]
    except KeyError:
        raise ValueError(f"Invalid rank string: {s!r}")


# ---------------------------------------------------------------------------
# Suit
# ---------------------------------------------------------------------------

class Suit(IntEnum):
    SPADES   = 0
    HEARTS   = 1
    CLUBS    = 2
    DIAMONDS = 3

_SUIT_NAMES: dict[Suit, str] = {
    Suit.SPADES:   "Spades",
    Suit.HEARTS:   "Hearts",
    Suit.CLUBS:    "Clubs",
    Suit.DIAMONDS: "Diamonds",
}

_SUIT_CV_TOKEN: dict[Suit, str] = {
    Suit.SPADES:   "spades",
    Suit.HEARTS:   "hearts",
    Suit.CLUBS:    "clubs",
    Suit.DIAMONDS: "diamonds",
}

_STR_TO_SUIT: dict[str, Suit] = {v: k for k, v in _SUIT_NAMES.items()}
_CV_TO_SUIT:  dict[str, Suit] = {v: k for k, v in _SUIT_CV_TOKEN.items()}


def string_to_suit(s: str) -> Suit:
    """'Spades' → Suit.SPADES, etc."""
    try:
        return _STR_TO_SUIT[s]
    except KeyError:
        raise ValueError(f"Invalid suit string: {s!r}")


def suit_next(suit: Suit) -> Suit:
    """Return the suit of the same color (used for left-bower logic)."""
    partner = {
        Suit.SPADES:   Suit.CLUBS,
        Suit.CLUBS:    Suit.SPADES,
        Suit.HEARTS:   Suit.DIAMONDS,
        Suit.DIAMONDS: Suit.HEARTS,
    }
    return partner[suit]


# ---------------------------------------------------------------------------
# Card
# ---------------------------------------------------------------------------

@total_ordering          # gives us all comparisons from __eq__ + __lt__
class Card:
    """
    Represents one euchre card.

    Suit-ordering tiebreaker (matches C++ impl): Diamonds > Clubs > Hearts > Spades
    """

    # Tiebreaker weight when ranks are equal (higher = wins tie)
    _SUIT_ORDER = {
        Suit.SPADES:   0,
        Suit.HEARTS:   1,
        Suit.CLUBS:    2,
        Suit.DIAMONDS: 3,
    }

    def __init__(self, rank: Rank = Rank.NINE, suit: Suit = Suit.SPADES) -> None:
        self.rank = rank
        self.suit = suit

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_rank(self) -> Rank:
        return self.rank

    def get_suit(self, trump: Suit | None = None) -> Suit:
        """
        If trump is given, the left bower is treated as belonging to the
        trump suit (mirrors Card::get_suit(Suit trump) in C++).
        """
        if trump is not None and self.is_left_bower(trump):
            return trump
        return self.suit

    # ------------------------------------------------------------------
    # Card predicates
    # ------------------------------------------------------------------

    def is_face_or_ace(self) -> bool:
        return self.rank in (Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE)

    def is_right_bower(self, trump: Suit) -> bool:
        """Jack of the trump suit."""
        return self.rank == Rank.JACK and self.suit == trump

    def is_left_bower(self, trump: Suit) -> bool:
        """Jack of the same-color suit as trump."""
        return self.rank == Rank.JACK and self.suit == suit_next(trump)

    def is_trump(self, trump: Suit) -> bool:
        return self.suit == trump or self.is_left_bower(trump)

    # ------------------------------------------------------------------
    # CV integration
    # ------------------------------------------------------------------

    def cv_label(self) -> str:
        """
        Canonical class label for dataset folders and model output.
        Example: Card(Rank.JACK, Suit.SPADES).cv_label() == 'jack_spades'

        Use this as the folder name when collecting training images:
            data/raw/jack_spades/img_001.jpg
        """
        return f"{_RANK_CV_TOKEN[self.rank]}_{_SUIT_CV_TOKEN[self.suit]}"

    @classmethod
    def from_cv_label(cls, label: str) -> "Card":
        """
        Reconstruct a Card from a model prediction string.
        Example: Card.from_cv_label('jack_spades') → Card(JACK, SPADES)

        Raises ValueError if the label is not a valid euchre card.
        """
        try:
            rank_token, suit_token = label.split("_", 1)
            rank = _CV_TO_RANK[rank_token]
            suit = _CV_TO_SUIT[suit_token]
        except (ValueError, KeyError):
            raise ValueError(f"Invalid CV label: {label!r}")
        return cls(rank, suit)

    @staticmethod
    def all_cv_labels() -> list[str]:
        """
        Return the full sorted list of 24 class labels.
        Useful for model construction: num_classes = len(Card.all_cv_labels())
        and for mapping model output indices back to labels.
        """
        labels = []
        for rank in Rank:
            for suit in Suit:
                labels.append(f"{_RANK_CV_TOKEN[rank]}_{_SUIT_CV_TOKEN[suit]}")
        return labels

    # ------------------------------------------------------------------
    # Comparison operators (no trump — mirrors C++ operator< etc.)
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other: "Card") -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        if self.rank != other.rank:
            return self.rank < other.rank
        # Same rank: tiebreak by suit (Diamonds > Clubs > Hearts > Spades)
        return self._SUIT_ORDER[self.suit] < self._SUIT_ORDER[other.suit]

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))

    # ------------------------------------------------------------------
    # String I/O
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """'Jack of Spades'"""
        return f"{_RANK_NAMES[self.rank]} of {_SUIT_NAMES[self.suit]}"

    def __repr__(self) -> str:
        return f"Card({self.rank.name}, {self.suit.name})"

    @classmethod
    def from_string(cls, s: str) -> "Card":
        """
        Parse 'Jack of Spades' → Card(JACK, SPADES).
        Mirrors the C++ istream >> operator.
        """
        parts = s.split()
        if len(parts) != 3 or parts[1].lower() != "of":
            raise ValueError(f"Cannot parse card: {s!r}")
        return cls(string_to_rank(parts[0]), string_to_suit(parts[2]))


# ---------------------------------------------------------------------------
# Trump-aware comparison functions
# ---------------------------------------------------------------------------

def card_less(a: Card, b: Card, trump: Suit, led_card: Card | None = None) -> bool:
    """
    Return True if card `a` is lower value than card `b`.

    If led_card is provided, uses both trump and led suit to determine
    order (trick-taking context).  Otherwise uses only trump.

    Mirrors both overloads of Card_less() from C++.
    """
    if led_card is not None:
        return _card_less_led(a, b, led_card, trump)
    return _card_less_trump(a, b, trump)


def _card_less_trump(a: Card, b: Card, trump: Suit) -> bool:
    a_trump = a.is_trump(trump)
    b_trump = b.is_trump(trump)

    if a_trump and b_trump:
        if a.is_right_bower(trump):
            return False
        if b.is_right_bower(trump):
            return True
        if a.is_left_bower(trump):
            return False
        if b.is_left_bower(trump):
            return True
        return a < b

    if a_trump or b_trump:
        return b_trump   # b is trump → a loses; a is trump → a wins (False)

    return a < b


def _card_less_led(a: Card, b: Card, led_card: Card, trump: Suit) -> bool:
    a_trump = a.is_trump(trump)
    b_trump = b.is_trump(trump)

    # If either or both are trump, defer to trump-only ordering
    if a_trump or b_trump:
        return _card_less_trump(a, b, trump)

    led_suit = led_card.get_suit(trump)
    a_led = a.get_suit() == led_suit
    b_led = b.get_suit() == led_suit

    if a_led and b_led:
        return a < b
    if a_led or b_led:
        return b_led   # b follows lead → a loses; a follows lead → a wins

    return a < b


# ---------------------------------------------------------------------------
# Deck helpers
# ---------------------------------------------------------------------------

def make_euchre_deck() -> list[Card]:
    """Return all 24 cards in a standard euchre deck (unshuffled)."""
    return [Card(rank, suit) for suit in Suit for rank in Rank]


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import random

    deck = make_euchre_deck()
    assert len(deck) == 24

    trump = Suit.SPADES
    jack_spades   = Card(Rank.JACK, Suit.SPADES)
    jack_clubs    = Card(Rank.JACK, Suit.CLUBS)
    ace_spades    = Card(Rank.ACE,  Suit.SPADES)
    nine_hearts   = Card(Rank.NINE, Suit.HEARTS)

    assert jack_spades.is_right_bower(trump)
    assert jack_clubs.is_left_bower(trump)
    assert jack_clubs.get_suit(trump) == Suit.SPADES   # left bower acts as trump suit
    assert not nine_hearts.is_trump(trump)

    assert card_less(ace_spades, jack_spades, trump)   # right bower beats ace of trump
    assert card_less(jack_clubs, jack_spades, trump)   # right bower beats left bower
    assert not card_less(jack_spades, ace_spades, trump)

    # CV label round-trip
    label = jack_spades.cv_label()
    assert label == "jack_spades"
    assert Card.from_cv_label(label) == jack_spades

    all_labels = Card.all_cv_labels()
    assert len(all_labels) == 24
    print("All 24 CV class labels:")
    for lbl in all_labels:
        print(" ", lbl)

    random.shuffle(deck)
    print(f"\nShuffled deck sample: {deck[:5]}")
    print("All assertions passed.")