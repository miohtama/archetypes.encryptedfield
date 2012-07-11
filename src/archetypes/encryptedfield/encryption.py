from Crypto.Cipher import AES
import base64

# Crypto stuff from http://www.codekoala.com/blog/2009/aes-encryption-python-using-pycrypto/

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '{'

# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
encode_aes = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
decode_aes = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

#: This value is checked that our decryption key was correct
MARKER = "encrypted-value:"


def get_cipher(secret):
    """
    """
#   create a cipher object using the random secret
    cipher = AES.new(secret)
    return cipher


def encrypt_value(key, value):
    """
    :param key: Encryption secret

    :param value: String to encrypted as unicode string
    """

    if key is None:
        raise RuntimeError("Key was not provided")

    if value is None:
        raise RuntimeError("Value was None")

    if type(value) != unicode:
        raise RuntimeError("Values must be unicode strings")

    if not type(key) == str:
        raise RuntimeError("Encryption key must be ASCII string")

    if PADDING in value:
        raise RuntimeError("Padding char %s must not exist in value" % PADDING)

    value = value.encode("utf-8")

    value = MARKER + value

    cipher = get_cipher(key)

    return encode_aes(cipher, value)


def decrypt_value(key, value):
    """
    :return: Decrypted value as unicode string or None if the encryption key does not match
    """

    if key is None:
        raise RuntimeError("Key was not provided")

    if value is None:
        raise RuntimeError("Value was None")

    if type(value) != str:
        raise RuntimeError("Encrypted values must be stored as base64 encoded bytestrings")

    cipher = get_cipher(key)

    try:
        value = decode_aes(cipher, value)
    except ValueError:
        # Base64 decoding has failed
        # ValueError: Input strings must be a multiple of 16 in length
        return None

    marker = value[0:len(MARKER)]
    if marker != MARKER:
        return None

    value = value[len(MARKER):]

    value = value.decode("utf-8")

    return value
