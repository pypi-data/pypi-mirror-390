#!/usr/bin/env python3


from .utils import clear_terminal

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import Crypto.Protocol.KDF
from getpass import getpass
import json
import pickle

_ITERATIONS = 1000
_ENCODING = "utf-8"
_SANITY_CHECK = "this is a sanity check."


def get_credentials():
    """
    Get username and password for the AO3 account.

    Returns
    -------

    name: str
        AO3 username

    pswd: str
        AO3 password
    """

    username = input("Enter your AO3 username:\n")
    pswd = getpass(
        "Enter your AO3 password:\n(For security reasons, the letters won't be shown as you type.)\n"
    )
    return username, pswd


def _get_password_hash(
    password,
    salt,
):
    if salt is None:
        salt = get_random_bytes(16)

    password_hash = Crypto.Protocol.KDF.PBKDF2(
        password, salt, dkLen=16, count=_ITERATIONS, prf=None, hmac_hash_module=None
    )

    return password_hash, salt


def store_secrets(key: str, username: str, password: str, filename: str):
    """
    Encrypt username and password using a key and dump
    them as a pickle into `filename`
    """

    salt = get_random_bytes(16)
    IV = get_random_bytes(16)

    # The key needs to multiple of 16 in length.
    # So we need a Key Derivation Function.
    key_hash, salt = _get_password_hash(key, salt)

    # store username and password as text to be encrypted
    secret = json.dumps(
        {"username": username, "password": password, "sanity_check": _SANITY_CHECK}
    )
    secret = secret.encode(_ENCODING)

    cipher = AES.new(key_hash, AES.MODE_CFB, iv=IV)
    encrypted = cipher.encrypt(secret)

    iv_64 = b64encode(cipher.iv).decode(_ENCODING)
    encrypted_64 = b64encode(encrypted).decode(_ENCODING)
    salt_64 = b64encode(salt).decode(_ENCODING)

    payload = json.dumps({"iv": iv_64, "salt": salt_64, "secret": encrypted_64})

    file = open(filename, "wb")
    pickle.dump(payload, file)
    file.close()

    return


def read_secrets(key: str, filename: str, retry: bool = False):
    """
    Read secrets back from `filename` and decrypt them
    using `key`. If `retry` is True, let user try again
    if they provided wrong password.
    """

    # Read in file
    file = open(filename, "rb")
    payload = pickle.load(file)
    file.close()

    # Extract data from pickle
    b64 = json.loads(payload)
    iv = b64decode(b64["iv"])
    salt = b64decode(b64["salt"])
    secret_encrypted = b64decode(b64["secret"])

    attempt = 0
    max_attempts = 5
    decrypted = False

    while attempt < max_attempts:
        attempt += 1

        # generate key from provided string
        key_hash, salt = _get_password_hash(key, salt)

        try:
            # decrypt using key and Initialization Vector
            cipher = AES.new(key_hash, AES.MODE_CFB, iv=iv)
            secret_decrypted_encoded = cipher.decrypt(secret_encrypted)
            secret_decrypted = secret_decrypted_encoded.decode(_ENCODING)
            secret = json.loads(secret_decrypted)

            # sanity check
            decrypted = secret["sanity_check"] == _SANITY_CHECK
            assert decrypted

        except (ValueError, IndexError):
            if not retry:
                print("Invalid password.")
                quit(1)
            else:
                print(f"Invalid password [{attempt}/{max_attempts}]. Try again.")
                key = getpass("Enter master password (not your AO3 login password):\n")

    if attempt == max_attempts and not decrypted:
        print("Invalid password.")
        print("Too many attempts. Aborting.")
        quit(1)

    if not decrypted:
        raise ValueError("Something went wrong with decryption.")

    # extract the goodies
    username = secret["username"]
    password = secret["password"]

    return username, password
