import os
import torch
import torch.nn as nn
import torch.optim as optim
from model import ByteAutoencoder, CHUNK_SIZE

EPOCHS = 40
BATCH_SIZE = 128
LR = 1e-3


def load_training_data(folder="training_data"):
    chunks = []

    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        with open(path, "rb") as f:
            data = f.read()

        for i in range(0, len(data), CHUNK_SIZE):
            chunk = data[i:i + CHUNK_SIZE]
            if len(chunk) < CHUNK_SIZE:
                chunk += b"\x00" * (CHUNK_SIZE - len(chunk))

            chunks.append(list(chunk))

    return torch.tensor(chunks, dtype=torch.float32) / 255.0


def main():
    print("📦 Loading data...")
    data = load_training_data()
    dataset = torch.utils.data.DataLoader(
        data, batch_size=BATCH_SIZE, shuffle=True
    )

    model = ByteAutoencoder()
    optimizer = optim.Adam(model.parameters(), lr=LR)
    loss_fn = nn.MSELoss()

    print("🧠 Training autoencoder...")
    for epoch in range(EPOCHS):
        total_loss = 0.0
        for batch in dataset:
            optimizer.zero_grad()
            output = model(batch)
            loss = loss_fn(output, batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"Epoch {epoch+1}/{EPOCHS} — Loss: {total_loss:.6f}")

    torch.save(model.state_dict(), "autoencoder.pt")
    print("✅ Model saved as autoencoder.pt")


if __name__ == "__main__":
    main()
