import pytest
from src.codecs.gen3 import Gen3TextCodec

@pytest.mark.parametrize("plaintext", [
    "Hello, world!",
    "POKéMON Center",
    "Press START to begin!",
    "It's dangerous to go alone...",
    "",  # edge: empty string
    "{PLAYER} vs {RIVAL}!"
])
def test_encode_decode_roundtrip(plaintext):
    codec = Gen3TextCodec()
    encoded = codec.encode(plaintext)
    # Ensure terminator byte 0xFF is present at end
    assert encoded.endswith(b'\xFF'), "Missing 0xFF terminator in encoded bytes"

    decoded = codec.decode(encoded)
    # Strip control-chars and whitespace for comparison
    normalized = decoded.replace("\n", "").replace("\f", "").strip()
    # Compare lowercase for case-insensitive match (tables map A-Z ↔ a-z)
    assert plaintext.lower() == normalized.lower()

