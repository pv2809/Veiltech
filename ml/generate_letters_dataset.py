import random
import string

TARGET_MB = 12   # change to 10–15 if needed
OUTPUT_FILE = "letters_patterns_12mb.txt"

BYTES_PER_MB = 1024 * 1024
TARGET_SIZE = TARGET_MB * BYTES_PER_MB

alphabet = string.ascii_lowercase
alphabet_upper = string.ascii_uppercase

patterns = [
    lambda: "a" * 100,
    lambda: "b" * 100,
    lambda: "abc" * 40,
    lambda: "abab" * 50,
    lambda: "xyz" * 40,
    lambda: "".join(random.choice(alphabet) for _ in range(120)),
    lambda: "".join(random.choice(alphabet_upper) for _ in range(120)),
    lambda: "".join(random.choice(alphabet + alphabet_upper) for _ in range(120)),
]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    current_size = 0

    while current_size < TARGET_SIZE:
        block = random.choice(patterns)()
        block += "\n"
        f.write(block)
        current_size += len(block.encode("utf-8"))

print(f"✅ Generated {OUTPUT_FILE} ({current_size / BYTES_PER_MB:.2f} MB)")
