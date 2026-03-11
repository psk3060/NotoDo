import re, uuid

UUID_PATTERN = re.compile(r"^[0-9a-fA-F-]{32,36}$")

def ensure_uuid(val: str) -> str:
    if UUID_PATTERN.fullmatch(val):
        return val
    return str(uuid.uuid4())