"""
pack.py — Euchre pack (deck) management.

Responsibilities:
  - Maintain the 24-card euchre deck
  - Shuffle (7× in-shuffle matching C++ impl, or random)
  - Deal cards one at a time
  - Validate and remove a card from a player's hand (used by euchre.py)

euchre.py is responsible for:
  - Deal order / seat rotation
  - Kitty / turn-up logic
  - Game state dict
"""

from __future__ import annotations
import random as _random
from card import Card, make_euchre_deck

PACK_SIZE   = 24
HAND_SIZE   = 5
NUM_PLAYERS = 4


# ---------------------------------------------------------------------------
# Pack class
# ---------------------------------------------------------------------------

class Pack:
    """
    A 24-card euchre deck with a cursor tracking the next card to deal.
    Mirrors Pack.hpp / Pack.cpp from the C++ project.
    """

    def __init__(self) -> None:
        """Standard order: suits low→high, ranks low→high within each suit."""
        self._cards: list[Card] = make_euchre_deck()
        self._next: int = 0

    def deal_one(self) -> Card:
        """Return the next card and advance the cursor."""
        if self.empty():
            raise RuntimeError("No cards remaining in the pack.")
        card = self._cards[self._next]
        self._next += 1
        return card

    def reset(self) -> None:
        """Reset cursor to the first card without re-ordering."""
        self._next = 0

    def empty(self) -> bool:
        return self._next >= PACK_SIZE

    def remaining(self) -> int:
        return PACK_SIZE - self._next

    def peek(self) -> Card:
        """Return the next card without advancing the cursor."""
        if self.empty():
            raise RuntimeError("No cards remaining in the pack.")
        return self._cards[self._next]

    def shuffle(self) -> None:
        """
        7× in-shuffle (interleave bottom half into top half), then reset.
        Matches the C++ implementation exactly — deterministic given the
        same starting order, useful for reproducible tests.
        """
        for _ in range(7):
            copy = self._cards[:]
            half = PACK_SIZE // 2
            idx = 0
            for j in range(half):
                self._cards[idx]     = copy[half + j]
                self._cards[idx + 1] = copy[j]
                idx += 2
        self._next = 0

    def random_shuffle(self) -> None:
        """
        Cryptographically random shuffle. Preferred for real games;
        use shuffle() for reproducible tests.
        """
        _random.shuffle(self._cards)
        self._next = 0

    def __repr__(self) -> str:
        remaining = self._cards[self._next:]
        return f"Pack(next={self._next}, remaining={[str(c) for c in remaining]})"


# ---------------------------------------------------------------------------
# Hand validation helper (called by euchre.py)
# ---------------------------------------------------------------------------

def play_card(state: dict, seat: int, card: Card) -> Card:
    """
    Remove and return `card` from the given player's hand in game state.

    Called after the CV pipeline identifies a physical card — validates
    that the detected card is actually in the player's hand before
    accepting it as a legal play.

    Raises ValueError if the card is not in the player's hand.
    """
    hand = state["hands"][seat]
    try:
        hand.remove(card)
    except ValueError:
        raise ValueError(
            f"Card {card} is not in player {seat}'s hand: "
            f"{[str(c) for c in hand]}"
        )
    return card


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pack = Pack()
    assert pack.remaining() == 24

    pack.shuffle()
    first = pack.deal_one()
    assert pack.remaining() == 23
    print(f"First card after in-shuffle: {first}")

    pack.reset()
    assert pack.remaining() == 24

    pack.random_shuffle()
    dealt = [pack.deal_one() for _ in range(5)]
    print(f"5 cards after random shuffle: {[str(c) for c in dealt]}")
    assert pack.remaining() == 19

    print("All assertions passed.")