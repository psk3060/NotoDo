import re, uuid, json
import hashlib
from typing import Any

UUID_PATTERN = re.compile(r"^[0-9a-fA-F-]{32,36}$")

# uuid 형태인지 확인
def ensure_uuid(val: str) -> str:
    if UUID_PATTERN.fullmatch(val):
        return val
    return str(uuid.uuid4())

# json(dict)을 string으로
def json_to_string(data: dict[str, Any]) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",",":")
    )

# 문자열을 Hash화
def replace_hash_string(target: str) -> str:
    return hashlib.sha256(target.encode()).hexdigest()
