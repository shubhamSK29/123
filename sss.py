# sss.py
"""
Wrapper for Shamir Secret Sharing.
Primary implementation: PyCryptodome (Crypto.Protocol.SecretSharing.Shamir).
Fallback: local pure-Python implementation (keeps backward compatibility).

Public API:
- split_bytes_into_shares(secret_bytes: bytes, n: int = 3, k: int = 2) -> List[bytes]
    Returns shares as bytes: b'<index_byte><share_payload>'

- recover_bytes_from_shares(share_bytes_list: List[bytes]) -> bytes
    Accepts a list of shares in the format above and returns the recovered secret bytes.
"""

from typing import List
import os

# Try to use PyCryptodome's Shamir if available
_USE_PYCRYPTO = False
try:
    from Crypto.Protocol.SecretSharing import Shamir as _PyCrypto_Shamir
    _USE_PYCRYPTO = True
except Exception:
    _USE_PYCRYPTO = False

# --- Fallback pure-Python (simple but correct) implementation (only used if pycryptodome missing) ---
# We'll reuse the big-prime integer-based approach for reliability.
_PRIME = 2**257 - 93

def _eval_poly(coeffs, x, prime=_PRIME):
    y = 0
    xp = 1
    for c in coeffs:
        y = (y + c * xp) % prime
        xp = (xp * x) % prime
    return y

def _lagrange_interpolate_at_0(points, prime=_PRIME):
    """
    points: list of (x, y) tuples (integers)
    computes f(0) via Lagrange interpolation modulo prime
    """
    total = 0
    k = len(points)
    for j in range(k):
        xj, yj = points[j]
        num = 1
        den = 1
        for m in range(k):
            if m == j:
                continue
            xm, _ = points[m]
            num = (num * (-xm)) % prime
            den = (den * (xj - xm)) % prime
        invden = pow(den, -1, prime)
        lj = (num * invden) % prime
        total = (total + (yj * lj)) % prime
    return total

def _split_bytes_pure(secret: bytes, n: int = 3, k: int = 2) -> List[bytes]:
    if not isinstance(secret, (bytes, bytearray)):
        raise TypeError("secret must be bytes")
    if not (1 < k <= n <= 255):
        raise ValueError("Require 1 < k <= n <= 255")
    secret_int = int.from_bytes(secret, "big")
    # polynomial coefficients: a0 = secret_int, a1..a_{k-1} random < PRIME
    coeffs = [secret_int] + [int.from_bytes(os.urandom(32), "big") % _PRIME for _ in range(k - 1)]
    shares = []
    for i in range(1, n + 1):
        x = i
        y = _eval_poly(coeffs, x, _PRIME)
        # serialize y to fixed size (size of PRIME)
        byte_len = ( _PRIME.bit_length() + 7 ) // 8
        y_bytes = y.to_bytes(byte_len, "big")
        shares.append(bytes([x]) + y_bytes)
    return shares

def _recover_bytes_pure(share_blobs: List[bytes]) -> bytes:
    if not share_blobs:
        raise ValueError("No shares provided")
    points = []
    for b in share_blobs:
        if len(b) < 2:
            raise ValueError("Invalid share format")
        x = b[0]
        y = int.from_bytes(b[1:], "big")
        points.append((x, y))
    secret_int = _lagrange_interpolate_at_0(points, _PRIME)
    # convert to bytes (minimal representation) - caller must pad if needed
    if secret_int == 0:
        return b'\x00'
    return secret_int.to_bytes((secret_int.bit_length() + 7) // 8, "big")


# --- PyCryptodome-backed implementation ---
# If pycryptodome is available, use it for splitting/combining bytes
if _USE_PYCRYPTO:
    def split_bytes_into_shares(secret_bytes: bytes, n: int = 3, k: int = 2) -> List[bytes]:
        """
        Use PyCryptodome Shamir.split
        PyCryptodome's Shamir.split(k, n, secret_bytes) returns list of (index, share_bytes).
        We normalize to bytes: index_byte + share_bytes
        """
        if not isinstance(secret_bytes, (bytes, bytearray)):
            raise TypeError("secret_bytes must be bytes")
        if not (1 < k <= n <= 255):
            raise ValueError("Require 1 < k <= n <= 255")
        
        # PyCryptodome requires exactly 16 bytes for the secret
        if len(secret_bytes) != 16:
            # Pad or truncate to 16 bytes
            if len(secret_bytes) < 16:
                secret_bytes = secret_bytes + b'\x00' * (16 - len(secret_bytes))
            else:
                secret_bytes = secret_bytes[:16]
        
        # PyCryptodome's API: Shamir.split(k, n, secret)
        shares = _PyCrypto_Shamir.split(k, n, secret_bytes)
        out = []
        for idx, sh in shares:
            if isinstance(idx, int):
                out.append(bytes([idx]) + sh)
            else:
                # some versions return idx as bytes; normalize
                out.append(bytes([int.from_bytes(idx, 'big')]) + sh)
        return out

    def recover_bytes_from_shares(share_bytes_list: List[bytes]) -> bytes:
        """
        Accept list of bytes of form index_byte + share_payload and call Shamir.combine
        """
        if not share_bytes_list:
            raise ValueError("No shares provided")
        shares = []
        for b in share_bytes_list:
            if len(b) < 2:
                raise ValueError("Invalid share format")
            idx = b[0]
            payload = b[1:]
            shares.append((idx, payload))
        # PyCryptodome's combine expects list of (index, share)
        secret = _PyCrypto_Shamir.combine(shares)
        # Remove padding if it was added
        return secret.rstrip(b'\x00') if secret.endswith(b'\x00') else secret

else:
    # fallback: use pure implementations above
    def split_bytes_into_shares(secret_bytes: bytes, n: int = 3, k: int = 2) -> List[bytes]:
        return _split_bytes_pure(secret_bytes, n=n, k=k)

    def recover_bytes_from_shares(share_bytes_list: List[bytes]) -> bytes:
        return _recover_bytes_pure(share_bytes_list)

