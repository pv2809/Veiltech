def chunk_bytes(data: bytes, chunk_size: int = 256):
    return [
        data[i:i + chunk_size]
        for i in range(0, len(data), chunk_size)
    ]
