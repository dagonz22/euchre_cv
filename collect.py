"""
collect.py — Webcam dataset collection for euchre card CV training.

Usage:
    python collect.py

You will be prompted to enter the card rank and suit, or 'no_card'
for background/empty frame images.
Press SPACE to capture a frame. Stops automatically at 100 images.
Press Q to quit early.

Output structure:
    data/raw/<rank>_<suit>/0000.jpg   ← card classes
    data/raw/no_card/0000.jpg         ← background class

COLLECTION STRATEGY PER CARD (100 images total):
    - First 40: card on flat/blank background, various angles
    - Last 60:  card held naturally toward webcam, room in background
"""

import cv2
import os
import sys
from card import Rank, Suit, Card

TARGET       = 100
NOTIFY_EVERY = 10

RANK_MAP = {
    "Nine":  Rank.NINE,
    "Ten":   Rank.TEN,
    "Jack":  Rank.JACK,
    "Queen": Rank.QUEEN,
    "King":  Rank.KING,
    "Ace":   Rank.ACE,
}

SUIT_MAP = {
    "Spades":   Suit.SPADES,
    "Hearts":   Suit.HEARTS,
    "Clubs":    Suit.CLUBS,
    "Diamonds": Suit.DIAMONDS,
}


def prompt_label() -> tuple[str, str]:
    """
    Interactively prompt for rank and suit or 'no_card'.
    Returns (label, display_name) e.g. ('jack_spades', 'Jack of Spades')
    """
    print("\n=== Euchre Card Dataset Collector ===")
    print("Valid ranks : Nine, Ten, Jack, Queen, King, Ace")
    print("Valid suits : Spades, Hearts, Clubs, Diamonds")
    print("Other       : no_card  (background / empty frame images)")
    print()

    raw = input("Enter rank (or 'no_card'): ").strip()

    if raw.lower() == "no_card":
        return "no_card", "No Card (background)"

    rank_input = raw.capitalize()
    if rank_input not in RANK_MAP:
        print(f"  ✗ '{rank_input}' is not a valid rank. Exiting.")
        sys.exit(1)

    suit_input = input("Enter suit: ").strip().capitalize()
    if suit_input not in SUIT_MAP:
        print(f"  ✗ '{suit_input}' is not a valid suit. Exiting.")
        sys.exit(1)

    card = Card(RANK_MAP[rank_input], SUIT_MAP[suit_input])
    return card.cv_label(), str(card)


def collect(label: str, display_name: str) -> None:
    out_dir  = os.path.join("data", "raw", label)
    os.makedirs(out_dir, exist_ok=True)

    existing = len([f for f in os.listdir(out_dir) if f.endswith(".jpg")])

    if existing >= TARGET:
        print(f"\n  Already have {existing} images for '{label}'. Nothing to do.")
        return

    if existing > 0:
        answer = input(f"\n  Found {existing} existing images. Resume? (y/n): ").strip().lower()
        if answer != 'y':
            print("  Exiting.")
            return
        print(f"  Resuming — {existing} saved, need {TARGET - existing} more.")

    # Remind user of split strategy for card classes
    if label != "no_card":
        print(f"\n  Collection strategy:")
        print(f"    Images  1–40 : card on flat/blank background")
        print(f"    Images 41–100: card held naturally, room in background")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: could not open webcam.")
        sys.exit(1)

    count = existing
    print(f"\n  Controls: SPACE = capture | Q = quit early")
    print(f"  Target: {TARGET} images  |  Notify every: {NOTIFY_EVERY}\n")

    # Milestone reminder for the background/scene switch
    scene_switch = 40
    scene_reminded = count >= scene_switch

    while count < TARGET:
        ret, frame = cap.read()
        if not ret:
            print("Error: failed to read frame.")
            break

        # Remind user to switch to scene shots at image 41
        if label != "no_card" and count == scene_switch and not scene_reminded:
            print(f"\n  ── Switch to scene shots now ──")
            print(f"  Hold the card naturally toward the webcam with your room in the background.")
            scene_reminded = True

        overlay = frame.copy()
        cv2.putText(
            overlay,
            f"{display_name}  [{count}/{TARGET}]",
            (12, 36),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # Show current phase for card classes
        if label != "no_card":
            phase = "Flat background" if count < scene_switch else "Scene / held"
            cv2.putText(
                overlay,
                f"Phase: {phase}",
                (12, 68),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (180, 220, 255),
                1,
                cv2.LINE_AA,
            )

        cv2.putText(
            overlay,
            "SPACE = capture   Q = quit",
            (12, frame.shape[0] - 14),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 200, 200),
            1,
            cv2.LINE_AA,
        )
        cv2.imshow("Card Collector", overlay)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            filename = os.path.join(out_dir, f"{count:04d}.jpg")
            cv2.imwrite(filename, frame)
            count += 1

            if count % NOTIFY_EVERY == 0:
                print(f"  [{count}/{TARGET}] saved — {TARGET - count} remaining")

            if count >= TARGET:
                print(f"\n  ✓ Done! {TARGET} images saved to data/raw/{label}/")
                break

        elif key == ord('q'):
            print(f"\n  Stopped early at {count} images.")
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    label, display_name = prompt_label()
    print(f"\n  ✓ Collecting: {display_name}  (label: {label})")
    collect(label, display_name)


if __name__ == "__main__":
    main()