"""
train.py — Train a MobileNetV2 card classifier.

Works with any number of classes in data/raw/ including no_card.
Run with 2-3 classes to test the pipeline, then again with all 25.

Usage:
    python train.py

Output:
    models/card_model.pth      — best weights by val accuracy
    models/class_names.txt     — class label order (needed for inference)
"""

import os
import torch
from torchvision import datasets, transforms, models
from torch import nn
from torch.utils.data import DataLoader, random_split

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATA_DIR   = "data/raw"
MODEL_DIR  = "models"
EPOCHS     = 25
BATCH_SIZE = 32
LR         = 1e-5
VAL_SPLIT  = 0.2
IMG_SIZE   = 224

os.makedirs(MODEL_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
    transforms.RandomPerspective(distortion_scale=0.2, p=0.5),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

val_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

full_dataset = datasets.ImageFolder(DATA_DIR, transform=train_transform)
num_classes  = len(full_dataset.classes)

print(f"\n{'='*40}")
print(f"Classes ({num_classes}): {full_dataset.classes}")
print(f"Total images: {len(full_dataset)}")

val_size   = int(len(full_dataset) * VAL_SPLIT)
train_size = len(full_dataset) - val_size
train_ds, val_ds = random_split(full_dataset, [train_size, val_size])

val_ds.dataset = datasets.ImageFolder(DATA_DIR, transform=val_transform)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=0)
val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

print(f"Train: {train_size} | Val: {val_size}")
print(f"no_card class: {'yes' if 'no_card' in full_dataset.classes else 'no — add before full training'}")
print(f"{'='*40}\n")

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
model.classifier[1] = nn.Linear(1280, num_classes)

optimizer = torch.optim.Adam(model.parameters(), lr=LR)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=8, gamma=0.5)
criterion = nn.CrossEntropyLoss()

device = (
    "mps"   if torch.backends.mps.is_available()
    else "cuda" if torch.cuda.is_available()
    else "cpu"
)
print(f"Using device: {device}\n")
model = model.to(device)

# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------

best_val_acc = 0.0

for epoch in range(EPOCHS):
    model.train()
    train_loss, train_correct, train_total = 0.0, 0, 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss    = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        train_loss    += loss.item() * images.size(0)
        preds          = outputs.argmax(dim=1)
        train_correct += (preds == labels).sum().item()
        train_total   += images.size(0)

    train_acc  = train_correct / train_total
    train_loss = train_loss / train_total

    model.eval()
    val_correct, val_total = 0, 0

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            preds   = outputs.argmax(dim=1)
            val_correct += (preds == labels).sum().item()
            val_total   += images.size(0)

    val_acc = val_correct / val_total if val_total > 0 else 0.0
    scheduler.step()

    marker = " ← best" if val_acc > best_val_acc else ""
    print(f"Epoch {epoch+1:02d}/{EPOCHS}  "
          f"loss: {train_loss:.4f}  "
          f"train_acc: {train_acc:.1%}  "
          f"val_acc: {val_acc:.1%}{marker}")

    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), os.path.join(MODEL_DIR, "card_model.pth"))

# ---------------------------------------------------------------------------
# Save class names (25 total: 24 cards + no_card)
# ---------------------------------------------------------------------------

with open(os.path.join(MODEL_DIR, "class_names.txt"), "w") as f:
    for name in full_dataset.classes:
        f.write(name + "\n")

print(f"\n{'='*40}")
print(f"Best val accuracy: {best_val_acc:.1%}")
print(f"Saved model  → {MODEL_DIR}/card_model.pth")
print(f"Saved labels → {MODEL_DIR}/class_names.txt")
print(f"{'='*40}\n")

if best_val_acc < 0.80:
    print("⚠  Below 80% — check your images:")
    print("   - Is the rank clearly visible and filling the frame?")
    print("   - Do you have both flat background AND scene shots?")
    print("   - Try bumping EPOCHS to 35")
elif best_val_acc < 0.90:
    print("✓  Decent — will improve as you add more card classes.")
else:
    print("✓  Good accuracy. Ready to collect more cards and retrain.")