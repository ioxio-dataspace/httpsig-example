import json
import random

from app.http_sig import (
    http_sig_signer,
    http_sig_verifier,
    inject_digest,
    make_short_signature,
    verify_content_digest,
)
from app.settings import conf
from flask import Flask, Response, request

app = Flask(__name__)


@app.get("/.well-known/jwks.json")
def get_jwks():
    return {"keys": [conf.PRIVATE_KEY.jwk]}


@app.post("/draft/Weather/Current/Metric")
def get_weather():
    req_sig = make_short_signature(request.headers)
    print(
        f"Received request for /draft/Weather/Current/Metric with signature {req_sig}"
    )
    verify_content_digest(request.headers, request.json)
    print("Content digest is verified")
    http_sig_verifier.verify(request)
    print(f"Signature {req_sig} is verified")
    data = {
        "humidity": 48,
        "pressure": 1015,
        "rain": False,
        "temp": random.random() * 10,
        "windSpeed": 6.71,
        "windDirection": 1,
    }
    body = json.dumps(data).encode("utf8")
    resp = Response(response=body, status=200, mimetype="application/json", headers={})
    inject_digest(resp.headers, body)
    # Gotcha: HTTPSignatureComponentResolver requires `url` even in responses
    # We can probably subclass it to implement it properly
    resp.url = ""
    http_sig_signer.sign(
        resp,
        key_id=conf.PRIVATE_KEY.kid,
        covered_component_ids=("content-digest",),
    )
    resp_sig = make_short_signature(resp.headers)
    print(f"Signing response with signature {resp_sig}")
    return resp
