# core/file_policy.py

ALLOWED_FILE_TYPES = {
    # Documents
    "application/pdf": 10 * 1024 * 1024,      # 10 MB
    "text/plain": 15 * 1024 * 1024,            # 15 MB
    "text/csv": 10 * 1024 * 1024,               # 10 MB
    "application/json": 5 * 1024 * 1024,        # 5 MB
    "application/xml": 5 * 1024 * 1024,         # 5 MB

    # Images
    "image/png": 8 * 1024 * 1024,               # 8 MB
    "image/jpeg": 8 * 1024 * 1024,              # 8 MB
    "image/bmp": 6 * 1024 * 1024,               # 6 MB

    # Archives
    "application/zip": 20 * 1024 * 1024,        # 20 MB
}

def validate_file_policy(mime_type: str, file_size: int):
    """
    Enforce allowed file types and size limits.
    """
    if not mime_type:
        raise ValueError("MIME_TYPE_MISSING")

    if mime_type not in ALLOWED_FILE_TYPES:
        raise ValueError("FILE_TYPE_NOT_ALLOWED")

    max_size = ALLOWED_FILE_TYPES[mime_type]

    if file_size > max_size:
        raise ValueError("FILE_TOO_LARGE")

    return True
