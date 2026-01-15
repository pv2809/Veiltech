from core.ml_codec import encode_ml, decode_ml

original = b"AAAAABBBBBCCCCCDDDDDEEEEEFFFFFGGGGG"
encoded = encode_ml(original)
decoded = decode_ml(encoded)

decoded = decoded[:len(original)]

print("Original:", original)
print("Decoded :", decoded)

if original == decoded:
    print("✅ Autoencoder reconstruction SUCCESS")
else:
    print("❌ Reconstruction mismatch")
