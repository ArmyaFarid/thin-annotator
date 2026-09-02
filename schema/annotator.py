import base64
import binascii
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class AnnotatorProfile:
    full_name: str
    username: str
    level: str          # label, e.g. "expert"
    level_rank: int


class MalformedAnnotatorHeader(Exception):
    pass


def _decode_b64(raw: str) -> bytes:
    # btoa always pads, but re-pad defensively in case a proxy or client
    # strips trailing '=' characters.
    return base64.b64decode(raw + "=" * (-len(raw) % 4))


def parse_annotator_header(raw: str | None) -> AnnotatorProfile | None:
    if not raw:
        return None
    try:
        payload = json.loads(_decode_b64(raw).decode("utf-8"))
    except (binascii.Error, ValueError, UnicodeDecodeError) as exc:
        raise MalformedAnnotatorHeader(str(exc)) from exc

    if not isinstance(payload, dict):
        raise MalformedAnnotatorHeader("expected a JSON object")

    try:
        return AnnotatorProfile(
            full_name=str(payload["fullName"]),
            username=str(payload["username"]),
            level=str(payload["level"]),
            level_rank=int(payload["levelRank"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise MalformedAnnotatorHeader(str(exc)) from exc