from array import array
from typing import Dict, MutableSequence, Optional, List, Tuple
import zlib
import numpy as np
import numpy.typing as npt

class LzwDecoder:
    """
    Fixed-width MSB-first LZW with no clear/EOI codes.
    Typical for ECG XML B7 pipelines with 10-bit codewords.
    """

    def __init__(self, buffer: bytes, bits: int = 10):
        self.buffer = buffer
        self.bits = bits
        self.max_code = (1 << bits) - 2

        # bitstream state
        self.offset = 0
        self.bit_count = 0
        self.bit_buffer = 0

        # dictionary state
        self.previous: MutableSequence[int] = array("B")
        self.next_code = 256
        self.strings: Dict[int, MutableSequence[int]] = {
            c: array("B", [c]) for c in range(256)
        }

        # output cursor
        self.current: Optional[MutableSequence[int]] = None
        self.position = 0

    def read(self) -> int:
        if self.current is None or self.position >= len(self.current):
            self.current = self._read_next_string()
            self.position = 0
            if not self.current:
                return -1
        b = self.current[self.position] & 0xFF
        self.position += 1
        return b

    def _read_next_string(self) -> MutableSequence[int]:
        code = self._read_codepoint()
        if 0 <= code <= self.max_code:
            if code not in self.strings:
                # KwKwK case
                data = self.previous[:]
                data.append(self.previous[0])
                self.strings[code] = data
            else:
                data = self.strings[code]

            if self.previous and self.next_code <= self.max_code:
                nxt = self.previous[:]
                nxt.append(data[0])
                self.strings[self.next_code] = nxt
                self.next_code += 1

            self.previous = data
            return data

        return array("B")  # EOS

    def _read_codepoint(self) -> int:
        # Ensure we have at least bits in the MSBs of bit_buffer
        while self.bit_count <= 24:
            if self.offset < len(self.buffer):
                nxt = self.buffer[self.offset]
                self.offset += 1
                self.bit_buffer = (
                    self.bit_buffer | ((nxt & 0xFF) << (24 - self.bit_count))
                ) & 0xFFFFFFFF
                self.bit_count += 8
            elif self.bit_count < self.bits:
                return -1
            else:
                break

        mask = (1 << self.bits) - 1
        code = (self.bit_buffer >> (32 - self.bits)) & mask
        self.bit_buffer = (self.bit_buffer << self.bits) & 0xFFFFFFFF
        self.bit_count -= self.bits
        return code

def hexdump(b: bytes, n: int = 16) -> str:
    return " ".join(f"{x:02X}" for x in b[:n])

def _looks_like_zlib(buf: bytes) -> bool:
    if len(buf) < 2:
        return False
    cmf, flg = buf[0], buf[1]
    if cmf != 0x78:
        return False
    return ((cmf << 8) | flg) % 31 == 0

def _inflate_all(buf: bytes) -> bytes:
    """
    Inflate one or more concatenated zlib streams; if that fails,
    try raw DEFLATE (no zlib header). Returns input unchanged if neither applies.
    """
    # Try concatenated zlib streams
    view = memoryview(buf)
    out = bytearray()
    progressed = False
    while len(view) >= 2 and _looks_like_zlib(view.tobytes()):
        d = zlib.decompressobj()  # zlib wrapper
        chunk = d.decompress(view)
        out += chunk
        progressed = True
        rest = d.unused_data
        if not rest:
            break
        view = memoryview(rest)
    if progressed:
        return bytes(out)

    # Try raw DEFLATE (some exports do this)
    try:
        d = zlib.decompressobj(-zlib.MAX_WBITS)  # raw DEFLATE
        raw = d.decompress(buf) + d.flush()
        if raw:
            return raw
    except zlib.error:
        pass

    return buf  # not compressed, or unknown wrapper

# -------------------- byte joining --------------------

def _join_planar_msb_lsb(buf: bytes) -> npt.NDArray[np.int16]:
    arr = np.frombuffer(buf, dtype=np.uint8)
    n = arr.size // 2
    if n == 0:
        return np.zeros(0, dtype=np.int16)
    msb = arr[:n].astype(np.uint16)
    lsb = arr[n:].astype(np.uint16)
    u16 = (msb << 8) | lsb
    return u16.view(np.int16)

def _join_planar_lsb_msb(buf: bytes) -> npt.NDArray[np.int16]:
    arr = np.frombuffer(buf, dtype=np.uint8)
    n = arr.size // 2
    if n == 0:
        return np.zeros(0, dtype=np.int16)
    lsb = arr[:n].astype(np.uint16)
    msb = arr[n:].astype(np.uint16)
    u16 = (msb << 8) | lsb
    return u16.view(np.int16)

def _join_interleaved_le(buf: bytes) -> npt.NDArray[np.int16]:
    return np.frombuffer(buf, dtype='<i2')

def _join_interleaved_be(buf: bytes) -> npt.NDArray[np.int16]:
    return np.frombuffer(buf, dtype='>i2')

def _choose_best_words(post_bytes: bytes) -> npt.NDArray[np.int16]:
    """
    Pick the words array (int16) among four join patterns using a simple smoothness pre-score.
    """
    candidates = []
    for join_fn in (_join_planar_msb_lsb, _join_planar_lsb_msb, _join_interleaved_le, _join_interleaved_be):
        try:
            w = join_fn(post_bytes)
        except Exception:
            continue
        if w.size >= 2:
            # Pre-score: mean abs first difference (lower is better)
            d1 = np.diff(w.astype(np.int32))
            pre = float(np.mean(np.abs(d1)))
            candidates.append((pre, w))
    if not candidates:
        return np.zeros(0, dtype=np.int16)
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]

def _score_ecg_full(sig: npt.NDArray[np.int32]) -> float:
    """
    Lower is better. Penalize roughness (2nd diff), clipping, and drift (mean of deltas).
    """
    if sig.size < 10:
        return 1e12
    x = sig.astype(np.int32)
    d1 = np.diff(x)
    d2 = np.diff(x, n=2)
    rough = float(np.mean(np.abs(d2)))
    clip = float(np.mean((np.abs(x) > 30000))) * 1e4
    drift = float(abs(np.mean(d1))) * 10.0
    return rough + clip + drift

def _reconstruct_first_order(words: npt.NDArray[np.int16],
                             first_sample: int,
                             bias: int,
                             second_is_abs: bool) -> npt.NDArray[np.int32]:
    """s[n] = s[n-1] + (w[n] - bias)"""
    w = words.astype(np.int32)
    out = np.empty_like(w, dtype=np.int32)
    s0 = int(first_sample)
    out[0] = s0
    if w.size == 1:
        return out
    if second_is_abs:
        out[1] = int(w[1])
    else:
        out[1] = s0 + (int(w[1]) - bias)
    for i in range(2, len(w)):
        out[i] = out[i-1] + (int(w[i]) - bias)
    return out

def _reconstruct_second_order(words: npt.NDArray[np.int16],
                              first_sample: int,
                              bias: int,
                              second_is_abs: bool) -> npt.NDArray[np.int32]:
    """s[n] = 2*s[n-1] - s[n-2] + (w[n] - bias)"""
    w = words.astype(np.int32)
    out = np.empty_like(w, dtype=np.int32)
    s0 = int(first_sample)
    out[0] = s0
    if w.size == 1:
        return out
    if second_is_abs:
        out[1] = int(w[1])
    else:
        out[1] = s0 + (int(w[1]) - bias)
    for i in range(2, len(w)):
        out[i] = (out[i-1] << 1) - out[i-2] + (int(w[i]) - bias)
    return out

def _best_reconstruct(words: npt.NDArray[np.int16],
                      first_sample: int) -> npt.NDArray[np.int16]:
    """
    Try:
      order in {first, second}
      bias in {0, 64, 128}
      second_is_abs in {True, False}
    Pick the best by combined smoothness/clip/drift score.
    """
    if words.size < 2:
        return words

    best_sig32 = None
    best_score = 1e99

    for order in ("first", "second"):
        for bias in (0, 64, 128):
            for second_is_abs in (True, False):
                if order == "first":
                    sig32 = _reconstruct_first_order(words, first_sample, bias, second_is_abs)
                else:
                    sig32 = _reconstruct_second_order(words, first_sample, bias, second_is_abs)
                s = _score_ecg_full(sig32)
                if s < best_score:
                    best_score = s
                    best_sig32 = sig32

    return best_sig32.astype(np.int16) if best_sig32 is not None else np.array([], dtype=np.int16)

def _decode_lzw_to_bytes(payload: bytes, code_bits: int) -> bytes:
    dec = LzwDecoder(payload, bits=code_bits)
    out = bytearray()
    while True:
        b = dec.read()
        if b < 0:
            break
        out.append(b)
    if len(out) & 1:
        out.append(0)
    return bytes(out)

def _parse_chunk_header_u16(h: bytes) -> Tuple[int, int]:
    """
    8-byte header: [size:u16][flags:u16][start:i16][spare:u16]
    Returns (size, start).
    """
    size = int.from_bytes(h[0:2], "little", signed=False)
    start = int.from_bytes(h[4:6], "little", signed=True)
    return size, start

def _decode_chunk(payload: bytes, start: int) -> npt.NDArray[np.int16]:
    """
    Robust per-chunk decode:
    1) Try direct join (no LZW) — some exports zlib-compress the planar bytes
    2) Else try LZW with code_bits in [10, 9, 11]
    """
    # A) Direct join (no LZW)
    words = _choose_best_words(payload)
    if words.size >= 2:
        return _best_reconstruct(words, first_sample=start)

    # B) LZW attempts with multiple code widths
    for cb in (10, 9, 11):
        post = _decode_lzw_to_bytes(payload, code_bits=cb)
        if not post:
            continue
        words = _choose_best_words(post)
        if words.size >= 2:
            return _best_reconstruct(words, first_sample=start)

    raise ValueError(
        f"Chunk decode failed. payload_len={len(payload)}, head={hexdump(payload)}"
    )

def xli_decode_chunked(data: bytes, labels: List[str]) -> List[npt.NDArray[np.int16]]:
    """
    Decode concatenated B7 chunks with 8-byte u16-sized headers.
    """
    samples: List[npt.NDArray[np.int16]] = []
    off = 0
    n = len(data)
    while off < n:
        if off + 8 > n:
            raise ValueError(f"Truncated chunk header at {off}")
        h = data[off:off + 8]
        size, start = _parse_chunk_header_u16(h)
        off += 8
        if size <= 0 or off + size > n:
            raise ValueError(
                f"Unrecognized chunk header at {off - 8}, first 16 bytes: "
                + hexdump(data[off - 8:off + 8], 16)
            )
        payload = data[off:off + size]
        off += size
        samples.append(_decode_chunk(payload, start))
    return samples

def xli_decode_single(data: bytes, labels: List[str]) -> List[npt.NDArray[np.int16]]:
    """
    Single-block variant:
    1) Try direct-join on inflated bytes
    2) Else try LZW with code_bits in [10, 9, 11]
    First sample taken from the chosen words stream itself.
    """
    # A) Direct join (no LZW)
    words = _choose_best_words(data)
    if words.size >= 2:
        s0 = int(words[0])
        sig = _best_reconstruct(words, first_sample=s0)
        return [sig]

    # B) LZW attempts
    for cb in (10, 9, 11):
        post = _decode_lzw_to_bytes(data, code_bits=cb)
        if not post:
            continue
        words = _choose_best_words(post)
        if words.size >= 2:
            s0 = int(words[0])
            sig = _best_reconstruct(words, first_sample=s0)
            return [sig]

    raise ValueError(
        f"Single-block decode failed. len(data)={len(data)}, head={hexdump(data)}"
    )

def xli_decode(data: bytes, labels: List[str]) -> List[npt.NDArray[np.int16]]:
    """
    Entry point. Handles optional compression, then:
    1) Try chunked (u16-sized headers)
    2) Fall back to single-block
    Auto-selects byte-join layout and the best reconstruction model.
    """
    inner = _inflate_all(data)
    try:
        return xli_decode_chunked(inner, labels)
    except ValueError:
        return xli_decode_single(inner, labels)