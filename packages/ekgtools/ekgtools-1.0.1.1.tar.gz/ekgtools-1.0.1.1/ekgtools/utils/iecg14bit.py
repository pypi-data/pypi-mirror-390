import numpy as np
import numpy.typing as npt
from typing import List, MutableSequence, Optional, Dict
from array import array
from ekgtools.utils.iecg import LzwDecoder

INT16_MIN, INT16_MAX = -32768, 32767

# ---------- helpers: header + LZW -> uint8 ----------

def _read_header_le_8(h: bytes) -> tuple[int, int]:
    """Return (size, start) from an 8-byte little-endian header."""
    if len(h) != 8:
        raise ValueError(f"Header must be 8 bytes, got {len(h)}")
    size  = int.from_bytes(h[0:4], "little", signed=False)
    start = int.from_bytes(h[4:8], "little", signed=True)
    return size, start

def _lzw_to_u8(decoder) -> np.ndarray:
    """Stream LZW bytes into a uint8 numpy array."""
    buf = bytearray()
    while True:
        b = decoder.read()
        if b == -1:
            break
        if not (0 <= b <= 255):
            raise ValueError(f"LZW produced non-byte value {b}")
        buf.append(b)
    return np.frombuffer(bytes(buf), dtype=np.uint8)

# ---------- 14-bit unpack (little-endian bit order) ----------

def _sign_extend_twos(x: np.ndarray, bits: int) -> np.ndarray:
    """Vectorized two's-complement sign extension to int32."""
    sign = 1 << (bits - 1)
    return ((x ^ sign) - sign).astype(np.int32)

def unpack_14bit_le(u8: np.ndarray) -> np.ndarray:
    """
    Unpack tightly bit-packed 14-bit samples (little-endian bit order per sample).
    Layout: each 7 input bytes produce 4 output samples (56 bits total).
    Returns int16 array of samples for a SINGLE channel/chunk.
    """
    nblocks = u8.size // 7
    if nblocks == 0:
        return np.empty(0, dtype=np.int16)

    # Use only full 7-byte groups
    b = u8[: nblocks * 7].reshape(-1, 7).astype(np.uint32)

    # Bit slices (LSB-first within each 14-bit sample)
    s0 = ( b[:,0]        | ((b[:,1] & 0x3F) << 8) )
    s1 = ( (b[:,1] >> 6) |  (b[:,2]        << 2)  | ((b[:,3] & 0x0F) << 10) )
    s2 = ( (b[:,3] >> 4) |  (b[:,4]        << 4)  | ((b[:,5] & 0x03) << 12) )
    s3 = ( (b[:,5] >> 2) |  (b[:,6]        << 6) )

    packed14 = np.stack([s0, s1, s2, s3], axis=1).reshape(-1)  # uint32
    signed32 = _sign_extend_twos(packed14, bits=14)            # int32 wide for math safety
    return np.clip(signed32, INT16_MIN, INT16_MAX).astype(np.int16)

# ---------- your recurrence, per chunk/channel ----------

def xli_decode_deltas_14bit(samples14: np.ndarray, first: int) -> np.ndarray:
    """
    Apply the same second-order recurrence you used, on a SINGLE channel vector.
    Input: int16 array of unpacked 14-bit samples (already sign-extended to int16).
    Output: int16 array (same length).
    """
    if samples14.size < 2:
        return samples14.copy()

    d = samples14.astype(np.int64, copy=True)  # wide math
    x = int(d[0])
    y = int(d[1])
    last = int(first)

    for i in range(2, d.size):
        z = (y + y) - x - last
        d[i] = z
        last = int(d[i]) - 64
        x, y = y, z

    return np.clip(d, INT16_MIN, INT16_MAX).astype(np.int16)

# ---------- main entry: decode 14-bit files (one chunk == one channel) ----------

def xli_decode_14bit(data: bytes, labels: List[str]) -> List[npt.NDArray[np.int16]]:
    """
    Decode an XLI blob that stores 14-bit packed samples.
    Returns a list with one int16 array per chunk/channel.
    This mirrors your 16-bit xli_decode signature so you can A/B compare.
    """
    samples: List[npt.NDArray[np.int16]] = []
    offset = 0
    chunk_idx = 0

    while offset + 8 <= len(data):
        header = data[offset: offset + 8]; offset += 8
        size, start = _read_header_le_8(header)

        if offset + size > len(data):
            raise ValueError(f"Chunk {chunk_idx}: declared size {size} exceeds remaining {len(data)-offset}")

        chunk = data[offset: offset + size]; offset += size

        # LZW decode to bytes
        decoder = LzwDecoder(chunk, bits=10)
        u8 = _lzw_to_u8(decoder)

        # Unpack 14-bit packed samples
        d14 = unpack_14bit_le(u8)
        if d14.size == 0 and (u8.size % 7) != 0:
            raise ValueError(f"Chunk {chunk_idx}: 14-bit payload not a multiple of 7 bytes")

        # Apply recurrence per chunk and append
        deltas = xli_decode_deltas_14bit(d14, first=start)
        samples.append(deltas)
        chunk_idx += 1

    if offset != len(data):
        raise ValueError(f"Trailing {len(data)-offset} unparsed bytes at end")

    return samples