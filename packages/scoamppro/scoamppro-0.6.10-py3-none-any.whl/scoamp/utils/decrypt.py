import binascii

# pip install pycryptodome
from Crypto.Cipher import AES


def encrypt_aes256gcm(key: str, data: str, iv: bytes) -> str:
    key = _sanitize_key(key)
    cipher = AES.new(key, AES.MODE_GCM, iv)
    ed, auth_tag = cipher.encrypt_and_digest(data.encode())
    return binascii.hexlify(iv + ed + auth_tag).decode()


def decrypt_aes256gcm(key: str, ciphertext: str) -> str:
    key = _sanitize_key(key)
    hex_ciphertext = binascii.unhexlify(ciphertext)

    iv = hex_ciphertext[:12]
    data = hex_ciphertext[12:-16]
    auth_tag = hex_ciphertext[-16:]
    cipher = AES.new(key, AES.MODE_GCM, iv)
    dd = cipher.decrypt_and_verify(data, auth_tag)
    return dd.decode()


def _sanitize_key(key: str):
    if len(key) == 32:
        return key.encode()
    elif len(key) == 64:
        return binascii.unhexlify(key)
    else:
        raise ValueError("invalid key, length should be 32(raw) or 64(hex-encode)")
