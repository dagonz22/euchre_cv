"""
main.py — FastAPI backend for EuchreCV.

Endpoints:
    POST /detect        — accepts a webcam frame, returns detected card
    GET  /health        — simple health check

Run locally:
    pip install fastapi uvicorn python-multipart
    uvicorn main:app --reload --port 8000

Vue connects to http://localhost:8000 during development.
"""

import io
import cv2
import base64
import numpy as np
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ultralytics import YOLO
from huggingface_hub import hf_hub_download

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="EuchreCV API")

# Allow requests from Vue dev server and your deployed frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",       # Vite dev server
        "https://euchre.dagonz.org",  # replace with your actual domain
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Load model once at startup
# ---------------------------------------------------------------------------

print("Loading YOLO model...")
model_path = hf_hub_download(
    repo_id="mustafakemal0146/playing-cards-yolov8",
    filename="playing_cards_model_0_playing-cards-colab.pt"
)
model = YOLO(model_path)
print(f"Model loaded. Classes: {model.names}")

# ---------------------------------------------------------------------------
# Card parsing (same logic as infer.py)
# ---------------------------------------------------------------------------

EUCHRE_RANKS = {'9', '10', 'J', 'Q', 'K', 'A'}
RANK_MAP = {'9': 'Nine', '10': 'Ten', 'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'}
SUIT_MAP = {'S': 'Spades', 'H': 'Hearts', 'C': 'Clubs', 'D': 'Diamonds'}

CONFIDENCE_THRESHOLD = 0.80

def parse_label(label: str) -> dict | None:
    label = label.strip()
    if len(label) == 2:
        rank, suit = label[0], label[1]
    elif len(label) == 3:
        rank, suit = label[:2], label[2]
    else:
        return None
    if rank not in EUCHRE_RANKS or suit not in SUIT_MAP:
        return None
    return {'rank': RANK_MAP[rank], 'suit': SUIT_MAP[suit]}

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class DetectRequest(BaseModel):
    # Base64-encoded JPEG frame from the webcam
    frame: str

class DetectedCard(BaseModel):
    rank: str
    suit: str
    confidence: float

class DetectResponse(BaseModel):
    card: DetectedCard | None  # None if no valid euchre card detected

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect", response_model=DetectResponse)
def detect(body: DetectRequest):
    # Decode base64 frame
    try:
        image_bytes = base64.b64decode(body.frame)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {e}")

    # Run YOLO inference
    results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)

    # Find best valid euchre card detection
    best_card = None
    best_conf = 0.0

    for r in results:
        for box in r.boxes:
            label = model.names[int(box.cls[0])]
            conf  = float(box.conf[0])
            card  = parse_label(label)

            if card and conf > best_conf:
                best_conf = conf
                best_card = card

    if best_card:
        return DetectResponse(
            card=DetectedCard(
                rank=best_card['rank'],
                suit=best_card['suit'],
                confidence=round(best_conf * 100, 1),
            )
        )

    return DetectResponse(card=None)