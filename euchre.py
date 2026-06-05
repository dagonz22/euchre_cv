"""
euchre.py — Euchre game orchestration.

Responsible for:
  - Game state (scores, dealer rotation, hand/trick tracking)
  - Trump selection (two-round make_trump)
  - Trick play (lead_card, play_card, trick winner)
  - Scoring (euchre, march, normal)
  - Emitting structured events for the web frontend (no print statements)

NOT responsible for:
  - Card representation  → card.py
  - Deck/deal            → pack.py
  - CV card detection    → infer.py (future)

SEAT LAYOUT
-----------
  Seats 0 and 2 are one team (Team A).
  Seats 1 and 3 are the other team (Team B).
  Deal rotates clockwise: dealer increments each hand.

EVENT LOG
---------
  Every state change appends a dict to game["log"].
  The web layer reads this log to drive the UI — no side effects here.
  Event types: "deal", "turn_up", "order_up", "pass", "lead",
               "play", "trick_won", "hand_scored", "game_over"
"""

from __future__ import annotations
from card import Card, Suit, Rank, card_less
from pack import Pack, HAND_SIZE, NUM_PLAYERS, play_card


# ---------------------------------------------------------------------------
# Seating helpers (mirrors C++ teammate / leftNeighbor / rightNeighbor)
# ---------------------------------------------------------------------------

def left_neighbor(seat: int) -> int:
    return (seat + 1) % NUM_PLAYERS

def right_neighbor(seat: int) -> int:
    return (seat - 1) % NUM_PLAYERS

def teammate(seat: int) -> int:
    return (seat + 2) % NUM_PLAYERS

def team_of(seat: int) -> int:
    """0 and 2 → team 0;  1 and 3 → team 1."""
    return seat % 2


# ---------------------------------------------------------------------------
# Game state factory
# ---------------------------------------------------------------------------

def new_game_state(player_names: list[str], points_to_win: int = 10) -> dict:
    """
    Create a fresh game state ready for the first hand.

    Parameters
    ----------
    player_names  : list of 4 names, in seat order [0, 1, 2, 3]
    points_to_win : first team to reach this wins (standard: 10)

    Returns a mutable dict that is threaded through all game functions.
    """
    if len(player_names) != NUM_PLAYERS:
        raise ValueError("Exactly 4 player names required.")

    return {
        "players":        player_names,          # index → name
        "scores":         [0, 0],                # team 0, team 1
        "points_to_win":  points_to_win,
        "dealer":         0,                     # seat index, rotates each hand
        "hand_number":    0,
        # Populated by start_hand():
        "hands":          {},                    # seat → [Card, ...]
        "kitty":          None,                  # turn-up card
        "trump":          None,                  # Suit once chosen
        "trump_caller":   None,                  # seat that ordered up
        # Trick tracking (populated during play):
        "tricks":         [0, 0],                # team trick counts this hand
        "current_trick":  [],                    # list of (seat, Card) in play order
        "trick_leader":   None,                  # seat that leads current trick
        # Structured event log for the web layer:
        "log":            [],
        "phase":          "pregame",             # pregame | deal | trump | play | scoring | gameover
    }


# ---------------------------------------------------------------------------
# Phase 1 — Deal
# ---------------------------------------------------------------------------

def start_hand(state: dict) -> None:
    """
    Shuffle and deal a new hand. Populates state["hands"] and state["kitty"].
    Resets per-hand tracking fields.
    """
    dealer = state["dealer"]

    pack = Pack()
    pack.random_shuffle()

    # Deal order: left of dealer going clockwise
    order = [(dealer + 1 + i) % NUM_PLAYERS for i in range(NUM_PLAYERS)]
    hands: dict[int, list[Card]] = {i: [] for i in range(NUM_PLAYERS)}
    for _ in range(HAND_SIZE):
        for seat in order:
            hands[seat].append(pack.deal_one())
    kitty = pack.deal_one()

    state["hands"]         = hands
    state["kitty"]         = kitty
    state["trump"]         = None
    state["trump_caller"]  = None
    state["tricks"]        = [0, 0]
    state["current_trick"] = []
    state["trick_leader"]  = left_neighbor(dealer)
    state["phase"]         = "trump"

    state["log"].append({
        "event":       "deal",
        "hand":        state["hand_number"],
        "dealer":      dealer,
        "dealer_name": state["players"][dealer],
        # Each player's hand as cv_labels — the UI shows these as
        # "pull these cards from your physical deck"
        "hands": {
            seat: [c.cv_label() for c in cards]
            for seat, cards in state["hands"].items()
        },
        "kitty":     state["kitty"].cv_label(),
        "kitty_str": str(state["kitty"]),
    })


# ---------------------------------------------------------------------------
# Phase 2 — Trump selection
# ---------------------------------------------------------------------------

def make_trump(state: dict, seat: int, order_up: bool,
               called_suit: Suit | None = None) -> dict:
    """
    Record a player's trump-selection decision.

    Round 1: players say order_up=True/False for the turn-up suit.
             If the dealer is ordered up they add the kitty card (handled
             separately by dealer_swap()).
    Round 2: players name a suit (called_suit) or pass (order_up=False).
             The dealer is forced to pick in round 2 (stick the dealer).

    Returns a response dict:
        {"accepted": bool, "trump": Suit or None, "caller": int or None}

    The caller is responsible for iterating seats and calling this in order.
    See trump_selection_order() for the seat sequence.
    """
    if state["phase"] != "trump":
        raise RuntimeError("Not in trump selection phase.")

    upcard = state["kitty"]

    if order_up:
        # Round 1: suit is the upcard's suit.
        # Round 2: suit is whatever the player named.
        trump = upcard.get_suit() if called_suit is None else called_suit
        state["trump"]        = trump
        state["trump_caller"] = seat
        state["phase"]        = "play"

        state["log"].append({
            "event":  "order_up",
            "seat":   seat,
            "name":   state["players"][seat],
            "trump":  trump.name,
            "upcard": str(upcard),
        })
        return {"accepted": True, "trump": trump, "caller": seat}

    else:
        state["log"].append({
            "event": "pass",
            "seat":  seat,
            "name":  state["players"][seat],
        })
        return {"accepted": False, "trump": None, "caller": None}


def trump_selection_order(dealer: int) -> list[tuple[int, int]]:
    """
    Return [(seat, round), ...] in the order trump offers are made.
    Round 1: upcard suit; round 2: player names a suit.
    Dealer is last in each round (and is forced in round 2).
    """
    seats = [left_neighbor(dealer), teammate(dealer),
             right_neighbor(dealer), dealer]
    return [(s, 1) for s in seats] + [(s, 2) for s in seats]


def dealer_swap(state: dict, discard: Card) -> None:
    """
    After the dealer is ordered up in round 1, they add the kitty card
    to their hand and discard one card.

    discard: the Card the dealer chooses to throw away
    """
    dealer = state["dealer"]
    state["hands"][dealer].append(state["kitty"])
    play_card(state, seat=dealer, card=discard)

    state["log"].append({
        "event":   "dealer_swap",
        "seat":    dealer,
        "name":    state["players"][dealer],
        "added":   str(state["kitty"]),
        "discard": str(discard),
    })


# ---------------------------------------------------------------------------
# Phase 3 — Trick play
# ---------------------------------------------------------------------------

def lead_card(state: dict, seat: int, card: Card) -> None:
    """
    The trick leader plays the opening card of a trick.
    Removes the card from their hand and starts state["current_trick"].
    """
    if state["phase"] != "play":
        raise RuntimeError("Not in play phase.")
    if state["trick_leader"] != seat:
        raise ValueError(f"Seat {seat} is not the trick leader.")

    play_card(state, seat=seat, card=card)
    state["current_trick"] = [(seat, card)]

    state["log"].append({
        "event": "lead",
        "seat":  seat,
        "name":  state["players"][seat],
        "card":  str(card),
        "label": card.cv_label(),
    })


def play_card_to_trick(state: dict, seat: int, card: Card) -> dict | None:
    """
    A non-leader player plays a card to the current trick.
    Returns trick result dict if the trick is now complete, else None.

    Trick result: {"winner": seat, "team": 0|1, "cards": [(seat, str), ...]}
    """
    if state["phase"] != "play":
        raise RuntimeError("Not in play phase.")

    play_card(state, seat=seat, card=card)
    state["current_trick"].append((seat, card))

    state["log"].append({
        "event": "play",
        "seat":  seat,
        "name":  state["players"][seat],
        "card":  str(card),
        "label": card.cv_label(),
    })

    if len(state["current_trick"]) == NUM_PLAYERS:
        return _resolve_trick(state)
    return None


def _resolve_trick(state: dict) -> dict:
    """Determine trick winner, update trick counts, advance leader."""
    trump    = state["trump"]
    trick    = state["current_trick"]
    led_card = trick[0][1]

    winner_seat, winner_card = trick[0]
    for seat, card in trick[1:]:
        if card_less(winner_card, card, trump, led_card=led_card):
            winner_seat, winner_card = seat, card

    winning_team = team_of(winner_seat)
    state["tricks"][winning_team] += 1
    state["trick_leader"] = winner_seat
    state["current_trick"] = []

    result = {
        "event":        "trick_won",
        "winner":       winner_seat,
        "winner_name":  state["players"][winner_seat],
        "team":         winning_team,
        "cards":        [(s, str(c)) for s, c in trick],
        "trick_counts": state["tricks"][:],
    }
    state["log"].append(result)
    return result


# ---------------------------------------------------------------------------
# Phase 4 — Scoring
# ---------------------------------------------------------------------------

def score_hand(state: dict) -> dict:
    """
    Score the completed hand. Updates state["scores"] and rotates the dealer.

    Returns a scoring event dict with keys:
        winning_team, points_awarded, reason ("march"|"euchre"|"normal"),
        scores, game_over, winner_team (if game_over)
    """
    tricks      = state["tricks"]
    caller      = state["trump_caller"]
    caller_team = team_of(caller)

    winning_team = 0 if tricks[0] > tricks[1] else 1

    if winning_team == caller_team:
        if tricks[winning_team] == 5:
            points = 2
            reason = "march"
        else:
            points = 1
            reason = "normal"
    else:
        points = 2
        reason = "euchre"

    state["scores"][winning_team] += points

    pts_to_win = state["points_to_win"]
    game_over  = any(s >= pts_to_win for s in state["scores"])

    event = {
        "event":        "hand_scored",
        "hand":         state["hand_number"],
        "tricks":       tricks[:],
        "winning_team": winning_team,
        "caller":       caller,
        "caller_team":  caller_team,
        "points":       points,
        "reason":       reason,
        "scores":       state["scores"][:],
        "game_over":    game_over,
    }

    if game_over:
        winner = 0 if state["scores"][0] >= pts_to_win else 1
        event["winner_team"]  = winner
        event["winner_names"] = [
            state["players"][s] for s in range(NUM_PLAYERS) if team_of(s) == winner
        ]
        state["phase"] = "gameover"
        state["log"].append(event)
        state["log"].append({"event": "game_over", **event})
    else:
        state["dealer"]      = left_neighbor(state["dealer"])
        state["hand_number"] += 1
        state["phase"]       = "pregame"
        state["log"].append(event)

    return event


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    names = ["Alice", "Bob", "Carol", "Dave"]
    state = new_game_state(names, points_to_win=10)

    start_hand(state)

    print(f"Hand {state['hand_number']} — dealer: {names[state['dealer']]}")
    print(f"Kitty: {state['kitty']}")

    for seat in range(NUM_PLAYERS):
        hand_str = ", ".join(str(c) for c in state["hands"][seat])
        print(f"  {names[seat]:6s}: {hand_str}")

    # Simulate round-1 trump: first player to act orders up
    order = trump_selection_order(state["dealer"])
    first_seat, _ = order[0]
    result = make_trump(state, first_seat, order_up=True)
    print(f"\n{names[first_seat]} orders up {result['trump'].name}")

    events = [e["event"] for e in state["log"]]
    assert "deal" in events
    assert "order_up" in events
    print(f"Log events: {events}")
    print("Smoke test passed.")