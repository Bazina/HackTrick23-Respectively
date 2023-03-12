import jwt
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend


def cipher_solver(question):
    pass


def captcha_solver(question):
    # Return solution
    pass


def pcap_solver(question):
    # Return solution
    pass


def server_solver(question):
    decoded_token = jwt.decode(question, options={"verify_signature": False}, algorithms=["RS256"])

    decoded_token['admin'] = True
    key = decoded_token['rand']

    new_token = jwt.encode(decoded_token, key)
    return new_token
