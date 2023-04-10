import json

from app.http_sig import (
    http_sig_signer,
    http_sig_verifier,
    inject_digest,
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
    verify_content_digest(request.headers, request.json)
    http_sig_verifier.verify(request)
    data = {
        "humidity": 48,
        "pressure": 1015,
        "rain": False,
        "temp": 1.4600000000000364,
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
    return resp
