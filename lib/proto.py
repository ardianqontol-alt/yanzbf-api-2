from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV  = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])


def encode_varint(n):
    if n < 0:
        return b""
    out = []
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            b |= 0x80
        out.append(b)
        if not n:
            break
    return bytes(out)


def proto_field(num, value):
    if isinstance(value, dict):
        nested = b"".join(proto_field(k, v) for k, v in value.items())
        return encode_varint((num << 3) | 2) + encode_varint(len(nested)) + nested
    if isinstance(value, int):
        return encode_varint((num << 3) | 0) + encode_varint(value)
    if isinstance(value, (str, bytes)):
        raw = value.encode() if isinstance(value, str) else value
        return encode_varint((num << 3) | 2) + encode_varint(len(raw)) + raw
    return b""


def build_proto(fields):
    return b"".join(proto_field(k, v) for k, v in fields.items())


def aes_encrypt(raw_bytes):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(raw_bytes, AES.block_size))