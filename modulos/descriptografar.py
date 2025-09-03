import base64
import logging
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
 
UTF_8 = "utf-8"
KEY_ALGORITHM = "AES"
BLOCK_LENGTH = 128
DEFAULT_IV_SEED = "space-station-default-iv"
IV_LENGTH = 16
 
def encrypt(content, key, ivSeed=DEFAULT_IV_SEED, useSecureRandom=False, fillIvIntoResult=False):
    if not content or len(content) == 0 or not key or len(key) == 0 or not ivSeed or len(ivSeed) == 0:
        raise ValueError("content/key/ivSeed must be non-empty")
 
    if len(ivSeed.encode()) < IV_LENGTH:
        raise ValueError("ivSeed must be at least 16 bytes long")
 
    try:
        # create cipher.
        cipher = AES.new(get_secret_key(key, useSecureRandom), AES.MODE_CBC, get_iv(ivSeed))
 
        byte_content = content.encode(UTF_8)
 
        result = cipher.encrypt(pad(byte_content, AES.block_size))
 
        merge_result = result if not fillIvIntoResult else merge_bytes(get_iv(ivSeed), result)
 
        # Return via Base64 transcoding.
        base64_result = base64.b64encode(merge_result).decode(UTF_8)
        return base64_result
    except Exception as ex:
        logging.warning("AES encryption failed: %s", ex)
 
    return None
 
def get_secret_key(key, randomKey):
    try:
        if randomKey:
            from Crypto.Random import get_random_bytes as grb
            from Crypto.Cipher import PKCS5Cipher
 
            kg = PKCS5Cipher.KeyGenerator(KEY_ALGORITHM)
            secure_random = get_random_bytes(16)
            kg.init(BLOCK_LENGTH, secure_random)
            secret_key = kg.generate_key()
            return secret_key.export_key()
        else:
            return key.encode(UTF_8)[:16]
    except Exception as ex:
        logging.warning("AES failed to generate encryption key: %s", ex)
        raise RuntimeError("AES failed to generate encryption key", ex)
 
def get_iv(ivSeed):
    ivSeedBytes = ivSeed.encode()
    ivBytes = bytearray(16)
    ivBytes[:] = ivSeedBytes[:16]
    return bytes(ivBytes)
 
def merge_bytes(data1, data2):
    data3 = bytearray(data1) + bytearray(data2)
    return bytes(data3)
 
def decrypt(content, key, iv=DEFAULT_IV_SEED, useSecureRandom=False):
    if not iv or len(iv.encode(UTF_8)) < IV_LENGTH:
        raise ValueError("ivSeed must be at least 16 bytes long")
 
    iv_seed_bytes = iv.encode(UTF_8)
    iv_bytes = bytearray(16)
    iv_bytes[:] = iv_seed_bytes[:16]
 
    if not content or not key:
        raise ValueError("Ciphertext and key cannot be empty")
 
    try:
        cipher = AES.new(get_secret_key(key, useSecureRandom), AES.MODE_CBC, iv_bytes)
        result = cipher.decrypt(base64.b64decode(content))
        return unpad(result, AES.block_size).decode(UTF_8)
 
    except Exception as ex:
        logging.warning("AES decryption failed: %s", ex)
 
    return None

def decrypt_KEY(encryption_key, data):
    """
    Descriptografa a secretKey vinda da API Shein usando AES.
    """
    decrypted = decrypt(data, encryption_key)
    if decrypted:
        return decrypted
    else:
        raise ValueError("Falha ao descriptografar secretKey")
 
# appSecretKey.
# encryption_key = "061753521A674765AE2193C07DA20344"
# data = "TqBBmI7I835XZf/jFv3AQ5ccGZUMmRYwY6KgWdSchoX5CUgYfYT/JE7UTmoDT3c3"
 
# decrypt_result = decrypt(data, encryption_key)
# print(decrypt_result)
 
# encrypt_result = encrypt(decrypt_result, encryption_key)
# print(encrypt_result)
# print(encrypt_result == data)