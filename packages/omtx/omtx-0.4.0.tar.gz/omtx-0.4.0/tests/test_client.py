from __future__ import annotations

import json
import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from omtx import OMTXClient, OMTXError
from omtx.client import JobTimeoutError
from omtx.exceptions import APIError


def make_response(status: int, payload: dict | str) -> MagicMock:
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status
    if isinstance(payload, dict):
        resp.json.return_value = payload
        resp.content = json.dumps(payload).encode("utf-8")
        resp.text = json.dumps(payload)
    else:
        resp.json.side_effect = ValueError
        resp.content = payload.encode("utf-8")
        resp.text = payload
    return resp


def make_stream_response() -> MagicMock:
    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.headers = {"X-Row-Count": "10"}
    resp.iter_content.return_value = [b"chunk-1", b"chunk-2"]
    return resp


def test_requires_api_key():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(OMTXError):
            OMTXClient()


def test_uses_env_api_key():
    with patch.dict(os.environ, {"OMTX_API_KEY": "env-key"}):
        client = OMTXClient(base_url="https://example.com")
        assert client.cfg.api_key == "env-key"
        client.close()


@patch("omtx.client.requests.Session.request")
def test_health_status_calls_gateway(mock_request):
    mock_request.return_value = make_response(200, {"status": "ok"})
    client = OMTXClient(api_key="key", base_url="https://example.com")

    result = client.gateway.status()
    assert result["status"] == "ok"

    kwargs = mock_request.call_args.kwargs
    assert kwargs["method"] == "GET"
    assert kwargs["url"].endswith("/v2/health")


@patch("omtx.client.requests.Session.request")
def test_users_credits(mock_request):
    mock_request.return_value = make_response(
        200, {"available_credits": 1234, "auto_reload_enabled": True}
    )
    client = OMTXClient(api_key="key", base_url="https://example.com")

    credits = client.users.profile()
    assert credits["available_credits"] == 1234

    kwargs = mock_request.call_args.kwargs
    assert kwargs["method"] == "GET"
    assert kwargs["url"].endswith("/v2/credits")


@patch("omtx.client.requests.Session.request")
def test_diligence_list_gene_keys_fetches_all(mock_request):
    mock_request.side_effect = [
        make_response(200, {"items": [{"gene_key": "acad8"}], "count": 2}),
        make_response(200, {"items": [{"gene_key": "tp53"}], "count": 2}),
    ]
    client = OMTXClient(api_key="key", base_url="https://example.com")

    result = client.diligence.list_gene_keys()
    assert result["count"] == 2
    assert [item["gene_key"] for item in result["items"]] == ["acad8", "tp53"]

    first_call = mock_request.call_args_list[0].kwargs
    assert first_call["params"]["limit"] == 200
    assert first_call["params"]["offset"] == 0
    assert len(mock_request.call_args_list) == 2


@patch("omtx.client.requests.Session.request")
def test_pricing_manifest_cached(mock_request):
    mock_request.return_value = make_response(
        200,
        {
            "pricing": [
                {
                    "endpoint_pattern": "/v2/data-access/points",
                    "base_cost_cents": 1,
                    "multiplier_field": "row_count",
                    "weight": 1.0,
                    "identifier_field": "protein_uuid",
                    "pricing_table": None,
                }
            ]
        },
    )
    client = OMTXClient(api_key="key", base_url="https://example.com")

    first = client.pricing.manifest()
    second = client.pricing.manifest()

    assert first["pricing"][0]["endpoint_pattern"] == "/v2/data-access/points"
    # Only one request should have been issued thanks to caching
    assert mock_request.call_count == 1


@patch("omtx.client.requests.Session.request")
def test_pricing_cost_estimate_points(mock_request):
    # Order of calls: stats -> manifest
    mock_request.side_effect = [
        make_response(
            200,
            {
                "dataset": "public",
                "total_rows": 1000,
                "protein_uuid": "uuid",
            },
        ),
        make_response(
            200,
            {
                "pricing": [
                    {
                        "endpoint_pattern": "/v2/data-access/points",
                        "base_cost_cents": 1,
                        "multiplier_field": "row_count",
                        "weight": 1.0,
                        "identifier_field": "protein_uuid",
                        "pricing_table": None,
                    }
                ]
            },
        ),
    ]

    client = OMTXClient(api_key="key", base_url="https://example.com")
    result = client.binders.points.cost_estimate(
        dataset="public", protein_uuid="uuid", limit=500
    )

    assert result["cost_cents"] == 500
    assert result["rows"] == 500
    assert result["pricing"]["endpoint_pattern"] == "/v2/data-access/points"


@patch("omtx.client.requests.Session.request")
def test_public_stream_sets_accept_header_and_dataset(mock_request):
    mock_request.return_value = make_stream_response()

    client = OMTXClient(api_key="key", base_url="https://example.com")
    stream = client.binders.public.stream(
        protein_uuid="uuid", limit=100
    )
    try:
        kwargs = mock_request.call_args.kwargs
        assert kwargs["method"] == "GET"
        assert kwargs["headers"]["accept"] == "text/csv"
        assert kwargs["params"]["dataset"] == "public"
        assert kwargs["params"]["limit"] == 100
    finally:
        stream.close()


@patch("omtx.client.requests.Session.request")
def test_unlock_payload(mock_request):
    mock_request.return_value = make_response(
        200, {"unlocked": True, "protein_uuid": "uuid"}
    )
    client = OMTXClient(api_key="key", base_url="https://example.com")

    client.binders.unlock(
        protein_uuid="uuid", gene_name="TP53", idempotency_key="abc"
    )

    kwargs = mock_request.call_args.kwargs
    assert kwargs["method"] == "POST"
    assert kwargs["json"] == {"protein_uuid": "uuid", "gene_name": "TP53"}
    assert kwargs["headers"]["idempotency-key"]
    assert kwargs["url"].endswith("/v2/access/unlock")


@patch("omtx.client.requests.Session.request")
def test_diligence_generate_claims(mock_request):
    mock_request.return_value = make_response(202, {"job_id": "job-123"})
    client = OMTXClient(api_key="key", base_url="https://example.com")

    resp = client.diligence.generate_claims(target="TP53", prompt="summary")
    assert resp["job_id"] == "job-123"

    kwargs = mock_request.call_args.kwargs
    assert kwargs["method"] == "POST"
    assert kwargs["json"] == {"target": "TP53", "prompt": "summary"}
    assert kwargs["headers"]["idempotency-key"]
    assert kwargs["url"].endswith("/v2/diligence/generateClaims")


def test_jobs_wait_success():
    client = OMTXClient(api_key="key", base_url="https://example.com")
    client.jobs.status = MagicMock(
        side_effect=[
            {"job_id": "abc", "status": "queued"},
            {"job_id": "abc", "status": "succeeded"},
        ]
    )
    client._request = MagicMock(return_value={"result": "ok"})

    with patch("omtx.client.time.sleep", return_value=None):
        result = client.jobs.wait(
            "abc", result_endpoint="/v2/jobs/foo/{job_id}", poll_interval=0.01
        )

    assert result == {"result": "ok"}
    client._request.assert_called_once()


def test_jobs_wait_failure():
    client = OMTXClient(api_key="key", base_url="https://example.com")
    client.jobs.status = MagicMock(
        side_effect=[
            {"job_id": "abc", "status": "failed", "error": "boom", "status_code": 422}
        ]
    )

    with patch("omtx.client.time.sleep", return_value=None):
        with pytest.raises(APIError) as excinfo:
            client.jobs.wait("abc", poll_interval=0.01, timeout=0.05)

    assert excinfo.value.status_code == 422
    assert "boom" in str(excinfo.value)


def test_jobs_wait_timeout():
    client = OMTXClient(api_key="key", base_url="https://example.com")
    client.jobs.status = MagicMock(return_value={"status": "queued"})

    with patch("omtx.client.time.sleep", return_value=None):
        with pytest.raises(JobTimeoutError):
            client.jobs.wait("abc", poll_interval=0.01, timeout=0.05)
