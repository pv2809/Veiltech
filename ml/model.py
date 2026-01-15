import torch
import torch.nn as nn

CHUNK_SIZE = 256
LATENT_SIZE = 256   # 🔥 KEY CHANGE (no compression)


class ByteAutoencoder(nn.Module):
    def __init__(self):
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Linear(CHUNK_SIZE, 512),
            nn.ReLU(),
            nn.Linear(512, LATENT_SIZE),
        )

        self.decoder = nn.Sequential(
            nn.Linear(LATENT_SIZE, 512),
            nn.ReLU(),
            nn.Linear(512, CHUNK_SIZE),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))
