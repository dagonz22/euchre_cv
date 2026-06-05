import cv2
from huggingface_hub import hf_hub_download
from ultralytics import YOLO

model_path = hf_hub_download(
    repo_id="mustafakemal0146/playing-cards-yolov8",
    filename="playing_cards_model_0_playing-cards-colab.pt"
)
model = YOLO(model_path)

# Print class names so we can verify label format
print("Model classes:", model.names)

# Euchre-valid ranks — filters out 2-8
EUCHRE_RANKS = {'9', '10', 'J', 'Q', 'K', 'A'}

# Map short labels to card.py conventions
RANK_MAP = {'9': 'Nine', '10': 'Ten', 'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'}
SUIT_MAP = {'S': 'Spades', 'H': 'Hearts', 'C': 'Clubs', 'D': 'Diamonds'}

def parse_label(label):
    """
    Parse a model class label into rank/suit.
    Handles formats like '9S', '10H', 'JC', 'QD', 'KH', 'AS'.
    Returns {'rank': ..., 'suit': ...} or None if not a valid euchre card.
    """
    label = label.strip()
    if len(label) == 2:
        rank, suit = label[0], label[1]
    elif len(label) == 3:  # e.g. '10S', '10H'
        rank, suit = label[:2], label[2]
    else:
        return None
    if rank not in EUCHRE_RANKS or suit not in SUIT_MAP:
        return None
    return {'rank': RANK_MAP[rank], 'suit': SUIT_MAP[suit]}

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: could not open webcam.")
    exit(1)

print("Camera open. Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.75, verbose=False)

    for r in results:
        for box in r.boxes:
            label = model.names[int(box.cls[0])]
            conf  = float(box.conf[0])
            card  = parse_label(label)

            if card:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"{card['rank']} of {card['suit']} {conf:.0%}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2
                )
            else:
                # Show unfiltered label in grey so you can see what the model outputs
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (128, 128, 128), 1)
                cv2.putText(
                    frame,
                    f"{label} {conf:.0%}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (128, 128, 128), 1
                )

    cv2.imshow('Euchre CV', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()