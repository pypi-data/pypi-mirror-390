from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto import Random

def read_private_key(path: str):
    with open(path, 'rb') as f:
        data = f.read()
    key = RSA.importKey(data)
    return key

def decode_msg_v1_5(cipherbytes, private_key):
    """  Should consider using the more robust PKCS1 OAEP. """
    sentinel = Random.new().read(256)      # data length is 256
    cipher = PKCS1_v1_5.new(private_key)
    messagereceived = cipher.decrypt(cipherbytes, sentinel)
    return messagereceived

def decryt(rsa_file: str, cipherbytes: bytes):
    private_key = read_private_key(rsa_file)

    # Decrypt the data
    return decode_msg_v1_5(cipherbytes, private_key)

if __name__ == '__main__':
    import os
    import base64
    
    encrypted_data = base64.b64decode(b"iICR6L42w6lqTNsOcZEs9fu7OmRDLSyfpW8v85u0hEkD4gObbwAM+SXO64ZCpKrzJPwoQPggmOaPybgOS4ZZtHsXeNq/CAznK+dz/fxp9FQher+yp6TBZ2BFe5B0NOj3NLDVImLBYPcXZ99IAQNrIylBkF7Ns6ZxPPBeqh3jlIZMTmoyO3PMBvPDmOyOP3zir2SG/CDU2quYKBRSNXNjo+Y2jeO/SPJqBjRWlsSW5xWz2+kqcxsXUhvQH56sQVT+MbYtvTfgQMkPS81Mk9JFJd6mlGgCKUrXKbW6wO9xfkdi92hOLSwGCQEbdaXqyQaYv62+Rb5KtM6Mw8/zoBJx7wNhkR/CWJt0jygEix57s+qKop1+KU9UZVbFdQDgyWCz7Un8v0kHEcMEF8TbgHSqajwqGumaXKQYy3bMkLAT816TeGWd4Yl1pD2SuTHoO1N76q1oLwmXhiZ9TQeDXuLOhwP0Fqc9SzbcB3ZUjUWHF/vCjF+UPbAtCBIotymNA+4Xc3YLHMJOCeRVhrorn4sG+Iu1tUjLtNqhYDgtuauzE7sB8cR0Q+qDajlTZw7iDLAkleQ8K+kDNUjaT37/AM37/m6Q2k9rT7EZMBDihkbXd3Y2u4z2yzxItArI1kPAd4HmBoc2R0JdnZnPJBr02SurGrYRwnJRrTW5UXWnmTjVBFA=")

    decrypted_data = decryt(os.path.expanduser('~/.ssh/id_rsa'), encrypted_data)
    # Print the decrypted data
    print(decrypted_data)
