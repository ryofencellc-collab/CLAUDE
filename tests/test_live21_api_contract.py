"""Every request the live client makes, checked against Kalshi's published OpenAPI spec (v3.36.0, fetched
2026-11-07 by .github/workflows/probe.yml): the path and method exist, query parameters are known, and order
bodies match CreateOrderV2Request exactly (required fields, no unknown fields, enums, types)."""
import json
import re
from pathlib import Path

import pytest
import yaml

from edge import live21 as L

SPEC = yaml.safe_load((Path(__file__).parent / "fixtures" / "kalshi_openapi_3.36.yaml").read_text())
SCH = SPEC["components"]["schemas"]


def resolve(x):
    while isinstance(x, dict) and "$ref" in x:
        name = x["$ref"].split("/")[-1]
        x = SCH.get(name) or SPEC["components"]["parameters"][name]
    if isinstance(x, dict) and "allOf" in x:
        out = {}
        for part in x["allOf"]:
            out.update(resolve(part))
        return out
    return x


def spec_op(method, path):
    for tmpl, ops in SPEC["paths"].items():
        if re.fullmatch(re.sub(r"\{[^}]+\}", "[^/]+", tmpl), path) and method.lower() in ops:
            return ops[method.lower()]
    return None


def check_body(body, schema_name):
    sch = SCH[schema_name]
    missing = set(sch.get("required", [])) - set(body)
    unknown = set(body) - set(sch["properties"])
    assert not missing and not unknown, (missing, unknown)
    for k, v in body.items():
        f = resolve(sch["properties"][k])
        if "enum" in f:
            assert v in f["enum"], (k, v)
        t = f.get("type")
        assert t is None or {"string": str, "integer": int, "boolean": bool}[t] is type(v), (k, v, t)


class Recorder:
    """Stands in for requests.Session: records every request and answers with a minimal valid response."""

    def __init__(self):
        self.reqs = []

    def request(self, method, url, headers=None, params=None, data=None, timeout=None):
        path = url.split("/trade-api/v2", 1)[1]
        self.reqs.append((method, path, params or {}, json.loads(data) if data else None))
        body = {"order_id": "o1", "client_order_id": "r21-x", "fill_count": "0.00", "remaining_count": "5.00",
                "ts_ms": 1, "reduced_by": "5.00", "balance": 100000, "balance_dollars": "1000.0000",
                "orders": [], "market_positions": [], "fills": [], "settlements": [], "cursor": ""}

        class R:
            status_code, text = 200, json.dumps(body)

            def json(self):
                return body
        return R()


@pytest.fixture
def client():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    pem = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    k = L.Kalshi("kid", pem)
    k.s = Recorder()
    return k


def test_every_client_call_matches_the_published_api(client):
    client.balance_usd()
    client.resting()
    client.positions()
    client.filled("KXBTC15M-X", "o1")
    client.filled("KXBTC15M-X")
    client.recent_settlement_pnls(1_700_000_000)
    o = client.buy("KXBTC15M-X", "no", 5, expires=1_800_000_000)
    client.cancel(o["order_id"], "KXBTC15M-X")
    assert o["order_id"] == "o1" and o["status"] == "resting"
    for method, path, params, body in client.s.reqs:
        op = spec_op(method, path)
        assert op is not None, f"{method} {path} is not in Kalshi's API"
        assert not op.get("deprecated"), f"{method} {path} is deprecated"
        known = {resolve(p)["name"] for p in op.get("parameters", [])}
        assert set(params) <= known, (method, path, set(params) - known)
        if body is not None:
            ref = op["requestBody"]["content"]["application/json"]["schema"]["$ref"].split("/")[-1]
            assert ref == "CreateOrderV2Request"
            check_body(body, ref)


def test_both_sides_and_the_selftest_orders_are_valid_v2_bodies():
    for side in ("yes", "no"):
        for cents in (99, 1):
            check_body(L.order_body("KXBTC15M-X", side, 3, cents=cents, expires=1_800_000_000), "CreateOrderV2Request")


def test_the_read_fields_the_bot_uses_exist_in_the_spec():
    def props(n):
        return set(SCH[n]["properties"])
    assert {"balance", "balance_dollars"} <= props("GetBalanceResponse")
    assert {"order_id", "client_order_id", "ticker", "status"} <= props("Order")
    assert {"ticker", "position_fp"} <= props("MarketPosition")
    assert {"order_id", "ticker", "count_fp"} <= props("Fill")
    assert {"settled_time", "revenue", "yes_total_cost_dollars", "no_total_cost_dollars", "fee_cost"} <= props("Settlement")
    assert "dollar" in SCH["Settlement"]["properties"]["fee_cost"]["$ref"].lower()   # fee_cost is in dollars now
    assert "cents" in SCH["Settlement"]["properties"]["revenue"]["description"]       # revenue still in cents
    assert {"order_id", "remaining_count"} <= props("CreateOrderV2Response")


def test_settlement_pnl_uses_the_right_units(client):
    client.s.request = lambda *a, **kw: type("R", (), {"status_code": 200, "text": "x", "json": lambda self: {
        "settlements": [{"settled_time": "2026-11-10T12:15:01Z", "revenue": 53000, "yes_total_cost_dollars": "0",
                         "no_total_cost_dollars": "524.7000", "fee_cost": "0.0900", "yes_count_fp": "0.00",
                         "no_count_fp": "530.00", "market_result": "no"}], "cursor": ""}})()
    (t, pnl), = client.recent_settlement_pnls(0)
    assert abs(pnl - (530.0 - 524.70 - 0.09)) < 1e-9                           # $5.21 profit, not $5.2991


def test_fills_are_counted_by_order_even_for_a_no_buy(client):
    fills = [{"order_id": "o1", "ticker": "T", "count_fp": "200.00", "outcome_side": "no", "book_side": "ask",
              "action": "sell", "side": "yes"},                                # legacy fields say 'sell yes'
             {"order_id": "o1", "ticker": "T", "count_fp": "330.00", "outcome_side": "no", "book_side": "ask"},
             {"order_id": "other", "ticker": "T", "count_fp": "999.00"}]
    client.s.request = lambda *a, **kw: type("R", (), {"status_code": 200, "text": "x",
                                                       "json": lambda self: {"fills": fills, "cursor": ""}})()
    assert client.filled("T", "o1") == 530.0
