import base64
import hashlib
import json

import http_sfv
from app.settings import conf
from http_message_signatures import (
    HTTPMessageSigner,
    HTTPMessageVerifier,
    HTTPSignatureKeyResolver,
    algorithms,
)
from jwt.jwks_client import PyJWKClient

jwks_client = PyJWKClient(conf.HTTP_SIG_VERIFY_JWKS_URI)


class ContentDigestMismatch(Exception):
    pass


class MissingContentDigest(Exception):
    pass


class AppKeyResolver(HTTPSignatureKeyResolver):
    def __init__(self):
        self.keys = {conf.PRIVATE_KEY.kid: conf.PRIVATE_KEY}

    def resolve_private_key(self, key_id: str):
        return self.keys[key_id].key

    def resolve_public_key(self, key_id: str):
        return jwks_client.get_signing_key(key_id).key


def inject_digest(headers, body):
    digest = http_sfv.Dictionary({"sha-256": hashlib.sha256(body).digest()})
    headers["Content-Digest"] = str(digest)


def verify_content_digest(headers, body):
    try:
        content_digest = headers["Content-Digest"]
    except KeyError:
        raise MissingContentDigest
    # digest_alg = content_digest.split("=")[0]
    incoming_digest = content_digest.split(":")[1]
    body_bytes = bytes(json.dumps(body), "utf8")

    calc_digest_bytes = hashlib.sha256(body_bytes).digest()
    # where \n in the end is coming from?
    calculated_digest = base64.encodebytes(calc_digest_bytes).decode("utf8")[:-1]
    if incoming_digest != calculated_digest:
        raise ContentDigestMismatch


key_resolver = AppKeyResolver()
http_sig_verifier = HTTPMessageVerifier(
    signature_algorithm=algorithms.RSA_V1_5_SHA256,
    key_resolver=key_resolver,
)
http_sig_signer = HTTPMessageSigner(
    signature_algorithm=algorithms.RSA_V1_5_SHA256,
    key_resolver=key_resolver,
)
