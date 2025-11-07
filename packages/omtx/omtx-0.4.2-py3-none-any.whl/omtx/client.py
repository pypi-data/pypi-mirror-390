from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional

import requests

from .exceptions import (
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    OMTXError,
)

if TYPE_CHECKING:  # pragma: no cover
    import pandas as pd


_SELECTIVITY_DATASET = "selectivity"
_POINTS_DATASETS = {"public", "private", "community", "decoys"}
_MAX_SELECTIVE_LIMIT = 1_000_000
_MAX_POINTS_LIMIT = 1_000_000


def _canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value, separators=(",", ":"), sort_keys=True, ensure_ascii=False
        )
    except Exception:
        return str(value)


def _derive_idempotency_key(
    provided: Optional[str], method: str, path: str, body: Any
) -> str:
    if provided and len(provided) >= 8:
        return provided
    issued_at_ms = int(time.time() * 1000)
    payload = f"{issued_at_ms}|{method.upper()}|{path}|{_canonical_json(body)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class ClientConfig:
    base_url: str
    api_key: str
    timeout: int = 3600


class DataStream:
    """Wrapper around a streaming CSV response."""

    def __init__(self, response: requests.Response):
        self._resp = response

    @property
    def headers(self) -> Dict[str, str]:
        return {k: v for k, v in self._resp.headers.items()}

    def iter_bytes(self, chunk_size: int = 1 << 14) -> Iterator[bytes]:
        for chunk in self._resp.iter_content(chunk_size=chunk_size):
            if chunk:
                yield chunk

    def to_dataframe(
        self, *, max_bytes: int = 100_000_000, close: bool = True
    ) -> "pd.DataFrame":
        import io
        import pandas as pd

        buffer = io.BytesIO()
        read = 0
        try:
            for chunk in self.iter_bytes():
                buffer.write(chunk)
                read += len(chunk)
                if read >= max_bytes:
                    break
        finally:
            if close:
                self.close()
        buffer.seek(0)
        return pd.read_csv(buffer)

    def close(self) -> None:
        try:
            self._resp.close()
        except Exception:
            pass


class _BaseNamespace:
    def __init__(self, client: "OMTXClient"):
        self._client = client


class OMTXClient:
    """High-level SDK entry point for OM Gateway."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 3600,
        *,
        session: Optional[requests.Session] = None,
    ):
        api_key = api_key or os.getenv("OMTX_API_KEY") or os.getenv("API_KEY")
        if not api_key:
            raise OMTXError(
                "API key is required. Pass api_key or set OMTX_API_KEY/API_KEY."
            )

        base_url = (
            base_url
            or os.getenv("OMTX_BASE_URL")
            or "https://api-gateway-129153908223.us-central1.run.app"
        )
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        self.cfg = ClientConfig(base_url=base_url, api_key=api_key, timeout=timeout)
        self._session = session or requests.Session()
        self._pricing_cache: Optional[Dict[str, Any]] = None
        self._pricing_map: Dict[str, Dict[str, Any]] = {}

        self.pricing = _PricingNamespace(self)
        self.binders = _BindersNamespace(self)
        self.diligence = _DiligenceNamespace(self)
        self.users = _UsersNamespace(self)
        self.jobs = _JobsNamespace(self)
        self.gateway = _GatewayNamespace(self)

    # ------------------------------------------------------------------ #
    # Session helpers
    # ------------------------------------------------------------------ #
    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "OMTXClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - context mgr
        self.close()

    # ------------------------------------------------------------------ #
    # Internal HTTP helpers
    # ------------------------------------------------------------------ #
    def _headers(
        self, *, idem_key: Optional[str], accept: str
    ) -> Dict[str, str]:
        headers = {
            "x-api-key": self.cfg.api_key,
            "accept": accept,
        }
        if idem_key:
            headers["idempotency-key"] = idem_key
            headers["content-type"] = "application/json"
        return headers

    def _handle_error(self, resp: requests.Response, path: str) -> None:
        try:
            payload = resp.json()
        except Exception:
            payload = resp.text or ""

        detail = payload.get("detail") if isinstance(payload, dict) else payload
        status = resp.status_code

        if status == 401:
            raise AuthenticationError(detail or "Unauthorized")
        if status == 402:
            raise InsufficientCreditsError(detail or "Insufficient credits")
        message = detail or f"HTTP {status} for {path}"
        raise APIError(message, status_code=status)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        *,
        idempotency_key: Optional[str] = None,
        accept: str = "application/json",
        stream: bool = False,
    ) -> Any:
        method = method.upper()
        url = f"{self.cfg.base_url}{path}"

        idem_header = None
        body = json_body
        if method != "GET":
            body = json_body or {}
            idem_header = _derive_idempotency_key(
                idempotency_key, method, path, body
            )
        headers = self._headers(idem_key=idem_header, accept=accept)
        if method != "GET" and "content-type" not in headers:
            headers["content-type"] = "application/json"

        resp = self._session.request(
            method=method,
            url=url,
            params=params,
            json=body if method != "GET" else None,
            headers=headers,
            timeout=self.cfg.timeout,
            stream=stream,
        )

        if resp.status_code >= 400:
            self._handle_error(resp, path)

        if stream:
            return resp

        if not resp.content:
            return {}

        try:
            return resp.json()
        except Exception as exc:  # pragma: no cover - defensive
            raise OMTXError(f"Non-JSON response from {path}") from exc

    def _get_pricing_row(self, endpoint_path: str) -> Dict[str, Any]:
        if not self._pricing_cache:
            self.pricing.manifest(refresh=True)
        row = self._pricing_map.get(endpoint_path)
        if not row:
            raise OMTXError(f"No pricing metadata for {endpoint_path}")
        return row

    def _compute_pricing_cost(
        self, endpoint_path: str, usage: Dict[str, Any]
    ) -> Dict[str, Any]:
        row = self._get_pricing_row(endpoint_path)

        base = row.get("base_cost_cents")
        try:
            base_value = float(base or 0)
        except (TypeError, ValueError):
            base_value = 0
        if base_value <= 0:
            return {
                "endpoint": endpoint_path,
                "cost_cents": 0,
                "pricing": row,
                "usage": usage,
            }

        multiplier_field = row.get("multiplier_field")
        multiplier_value = 1.0
        if multiplier_field:
            if multiplier_field not in usage or usage[multiplier_field] is None:
                raise OMTXError(
                    f"Usage must include '{multiplier_field}' for {endpoint_path}"
                )
            try:
                multiplier_value = float(usage[multiplier_field])
            except (TypeError, ValueError) as exc:
                raise OMTXError(
                    f"Invalid multiplier value for {multiplier_field}"
                ) from exc

        weight_value = row.get("weight") or 1.0
        try:
            weight = float(weight_value)
        except (TypeError, ValueError):
            weight = 1.0

        cost = int(base_value * multiplier_value * weight)
        return {
            "endpoint": endpoint_path,
            "cost_cents": max(cost, 0),
            "pricing": row,
            "usage": usage,
        }

    def _stream_points(
        self,
        *,
        dataset: str,
        protein_uuid: str,
        limit: Optional[int],
        params: Optional[Dict[str, Any]] = None,
    ) -> DataStream:
        if dataset not in _POINTS_DATASETS:
            allowed = ", ".join(sorted(_POINTS_DATASETS))
            raise OMTXError(
                f"dataset must be one of {{{allowed}}} for points access"
            )
        if not protein_uuid:
            raise OMTXError("protein_uuid is required for points datasets")

        query: Dict[str, Any] = {"dataset": dataset, "protein_uuid": protein_uuid}
        if limit is not None:
            limit = int(limit)
            if limit < 1 or limit > _MAX_POINTS_LIMIT:
                raise OMTXError(
                    f"limit must be between 1 and {_MAX_POINTS_LIMIT:,} for points access"
                )
            query["limit"] = limit
        if params:
            query.update(params)

        resp = self._request(
            "GET",
            "/v2/data-access/points",
            params=query,
            accept="text/csv",
            stream=True,
        )
        return DataStream(resp)

    def _stream_selective(
        self,
        *,
        protein_uuid: str,
        limit: Optional[int],
        params: Optional[Dict[str, Any]] = None,
    ) -> DataStream:
        if not protein_uuid:
            raise OMTXError("protein_uuid is required for selective access")

        query: Dict[str, Any] = {
            "dataset": _SELECTIVITY_DATASET,
            "protein_uuid": protein_uuid,
        }
        if limit is not None:
            limit = int(limit)
            if limit < 1 or limit > _MAX_SELECTIVE_LIMIT:
                raise OMTXError(
                    f"limit must be between 1 and {_MAX_SELECTIVE_LIMIT:,} for selective access"
                )
            query["limit"] = limit
        if params:
            query.update(params)

        resp = self._request(
            "GET",
            "/v2/data-access/selective",
            params=query,
            accept="text/csv",
            stream=True,
        )
        return DataStream(resp)


class _PricingNamespace(_BaseNamespace):
    def manifest(self, *, refresh: bool = False) -> Dict[str, Any]:
        if refresh or not self._client._pricing_cache:
            data = self._client._request("GET", "/v2/pricing")
            pricing = data.get("pricing") if isinstance(data, dict) else None
            if not isinstance(pricing, list):
                raise OMTXError("Invalid pricing manifest response")
            self._client._pricing_cache = {"pricing": pricing}
            self._client._pricing_map = {
                row["endpoint_pattern"]: row for row in pricing
            }
        return dict(self._client._pricing_cache)  # shallow copy

    def cost_estimate(
        self,
        endpoint: str,
        *,
        usage: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        ep = endpoint.lower().strip()
        alias_map = {
            "data-access.points": "/v2/data-access/points",
            "/v2/data-access/points": "/v2/data-access/points",
            "data-access.selective": "/v2/data-access/selective",
            "/v2/data-access/selective": "/v2/data-access/selective",
            "access.unlock": "/v2/access/unlock",
            "/v2/access/unlock": "/v2/access/unlock",
            "diligence.generateclaims": "/v2/diligence/generateClaims",
            "/v2/diligence/generateclaims": "/v2/diligence/generateClaims",
            "diligence.synthesizereport": "/v2/diligence/synthesizeReport",
            "/v2/diligence/synthesizereport": "/v2/diligence/synthesizeReport",
            "diligence.deepresearch": "/v2/diligence/deep-research",
            "/v2/diligence/deep-research": "/v2/diligence/deep-research",
        }
        normalized = alias_map.get(ep)
        if not normalized:
            raise OMTXError(f"Unknown endpoint alias: {endpoint}")

        if normalized == "/v2/data-access/points":
            return self._client.binders.points.cost_estimate(**kwargs)
        if normalized == "/v2/data-access/selective":
            return self._client.binders.selectivity.cost_estimate(**kwargs)

        usage_payload = usage or {}
        return self._client._compute_pricing_cost(normalized, usage_payload)


class _BindersNamespace(_BaseNamespace):
    def __init__(self, client: OMTXClient):
        super().__init__(client)
        self.points = _PointsNamespace(client)
        self.selectivity = _SelectivityNamespace(client)
        self.public = _PointsDataset(client, self, "public")
        self.private = _PointsDataset(client, self, "private")
        self.community = _PointsDataset(client, self, "community")
        self.decoys = _PointsDataset(client, self, "decoys")

    # Unified entry points -------------------------------------------------
    def stream(
        self,
        *,
        dataset: str,
        protein_uuid: str,
        limit: Optional[int] = None,
    ) -> DataStream:
        dataset = dataset.strip().lower()
        if dataset == _SELECTIVITY_DATASET:
            return self.selectivity.stream(
                protein_uuid=protein_uuid,
                limit=limit,
            )
        return self.points.stream(
            dataset=dataset,
            protein_uuid=protein_uuid,
            limit=limit,
        )

    def stats(
        self,
        *,
        dataset: str,
        protein_uuid: Optional[str] = None,
    ) -> Dict[str, Any]:
        dataset = dataset.strip().lower()
        if dataset == _SELECTIVITY_DATASET:
            if not protein_uuid:
                raise OMTXError("protein_uuid is required for selective stats")
            return self.selectivity.stats(protein_uuid=protein_uuid)
        return self.points.stats(dataset=dataset, protein_uuid=protein_uuid)

    # Unlock helpers -------------------------------------------------------
    def unlock(
        self,
        *,
        protein_uuid: str,
        gene_name: Optional[str] = None,
        protein: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not protein_uuid:
            raise OMTXError("protein_uuid is required to unlock data access")
        payload: Dict[str, Any] = {"protein_uuid": protein_uuid}
        if gene_name:
            payload["gene_name"] = gene_name
        if protein:
            payload["protein"] = protein
        return self._client._request(
            "POST",
            "/v2/access/unlock",
            json_body=payload,
            idempotency_key=idempotency_key,
        )

    def list_unlocks(self) -> Dict[str, Any]:
        return self._client._request("GET", "/v2/access/unlocks")


class _PointsNamespace(_BaseNamespace):
    def stream(
        self,
        *,
        dataset: str,
        protein_uuid: str,
        limit: Optional[int] = None,
    ) -> DataStream:
        return self._client._stream_points(
            dataset=dataset,
            protein_uuid=protein_uuid,
            limit=limit,
        )

    def stats(
        self,
        *,
        dataset: str,
        protein_uuid: Optional[str],
    ) -> Dict[str, Any]:
        dataset = dataset.strip().lower()
        if dataset not in _POINTS_DATASETS:
            allowed = ", ".join(sorted(_POINTS_DATASETS))
            raise OMTXError(
                f"dataset must be one of {{{allowed}}} for points stats"
            )
        if dataset != "decoys" and not protein_uuid:
            raise OMTXError("protein_uuid is required for points stats")

        params: Dict[str, Any] = {"dataset": dataset}
        if protein_uuid:
            params["protein_uuid"] = protein_uuid
        return self._client._request(
            "GET", "/v2/data-access/points/stats", params=params
        )

    def cost_estimate(
        self,
        *,
        dataset: str,
        protein_uuid: str,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        stats = self.stats(dataset=dataset, protein_uuid=protein_uuid)
        total_rows = int(stats.get("total_rows") or 0)
        if limit is not None:
            limit = int(limit)
            if limit < 1 or limit > _MAX_POINTS_LIMIT:
                raise OMTXError(
                    f"limit must be between 1 and {_MAX_POINTS_LIMIT:,} for points access"
                )
            rows = min(limit, total_rows or limit)
        else:
            rows = total_rows

        usage = {
            "row_count": rows,
            "protein_uuid": protein_uuid,
        }
        result = self._client._compute_pricing_cost(
            "/v2/data-access/points", usage
        )
        result.update(
            {
                "rows": rows,
                "dataset": dataset,
                "stats": stats,
            }
        )
        return result


class _PointsDataset(_BaseNamespace):
    def __init__(self, client: OMTXClient, binders: "_BindersNamespace", dataset: str):
        super().__init__(client)
        self.dataset = dataset
        self._binders = binders

    def stream(
        self,
        *,
        protein_uuid: str,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
        format: Optional[str] = None,
    ) -> DataStream:
        return self._binders.points.stream(
            dataset=self.dataset,
            protein_uuid=protein_uuid,
            limit=limit,
        )

    def stats(self, *, protein_uuid: str) -> Dict[str, Any]:
        return self._binders.points.stats(
            dataset=self.dataset, protein_uuid=protein_uuid
        )

    def cost_estimate(
        self,
        *,
        protein_uuid: str,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        return self._binders.points.cost_estimate(
            dataset=self.dataset,
            protein_uuid=protein_uuid,
            limit=limit,
        )


class _SelectivityNamespace(_BaseNamespace):
    def stream(
        self,
        *,
        protein_uuid: str,
        limit: Optional[int] = None,
    ) -> DataStream:
        return self._client._stream_selective(
            protein_uuid=protein_uuid,
            limit=limit,
        )

    def stats(self, *, protein_uuid: str) -> Dict[str, Any]:
        params = {"dataset": _SELECTIVITY_DATASET, "protein_uuid": protein_uuid}
        return self._client._request(
            "GET", "/v2/data-access/selective/stats", params=params
        )

    def cost_estimate(
        self,
        *,
        protein_uuid: str,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        stats = self.stats(protein_uuid=protein_uuid)
        total_rows = int(stats.get("total_rows") or 0)
        if limit is not None:
            limit = int(limit)
            if limit < 1 or limit > _MAX_SELECTIVE_LIMIT:
                raise OMTXError(
                    f"limit must be between 1 and {_MAX_SELECTIVE_LIMIT:,} for selective access"
                )
            products = min(limit, total_rows or limit)
        else:
            products = total_rows

        usage = {
            "product_count": products,
            "protein_uuid": protein_uuid,
        }
        result = self._client._compute_pricing_cost(
            "/v2/data-access/selective", usage
        )
        result.update(
            {
                "products": products,
                "stats": stats,
            }
        )
        return result


# ---------------------------------------------------------------------- #
# Diligence namespace
# ---------------------------------------------------------------------- #
class _DiligenceNamespace(_BaseNamespace):
    def generate_claims(
        self,
        *,
        target: str,
        prompt: str,
    ) -> Dict[str, Any]:
        if not target:
            raise OMTXError("target is required for generate_claims")
        if not prompt:
            raise OMTXError("prompt is required for generate_claims")

        payload = {"target": target, "prompt": prompt}
        response = self._client._request(
            "POST",
            "/v2/diligence/generateClaims",
            json_body=payload,
        )
        return response

    def synthesize_report(
        self,
        *,
        gene_key: str,
    ) -> Dict[str, Any]:
        if not gene_key:
            raise OMTXError("gene_key is required for synthesize_report")
        payload = {"gene_key": gene_key}
        response = self._client._request(
            "POST",
            "/v2/diligence/synthesizeReport",
            json_body=payload,
        )
        return response

    def deep_research(
        self,
        *,
        query: str,
    ) -> Dict[str, Any]:
        if not query:
            raise OMTXError("query is required for deep_research")

        payload: Dict[str, Any] = {"query": query}

        response = self._client._request(
            "POST",
            "/v2/diligence/deep-research",
            json_body=payload,
        )
        return response

    def list_gene_keys(
        self,
    ) -> Dict[str, Any]:
        limit = 200
        offset = 0
        all_items: list[Dict[str, Any]] = []
        total_count: Optional[int] = None

        while True:
            payload = {"min_true": 1, "limit": limit, "offset": offset}
            page = self._client._request(
                "GET", "/v2/diligence/gene-keys", params=payload
            )
            items = page.get("items") or []
            all_items.extend(items)
            if total_count is None:
                total_count = page.get("count")

            if len(items) < limit:
                if total_count is not None and len(all_items) < total_count:
                    offset += limit
                    continue
                break

            offset += limit

        return {
            "items": all_items,
            "count": total_count if total_count is not None else len(all_items),
        }


# ---------------------------------------------------------------------- #
# Health namespace
# ---------------------------------------------------------------------- #
class _UsersNamespace(_BaseNamespace):
    def profile(self) -> Dict[str, Any]:
        credits = self._client._request("GET", "/v2/credits")
        return {
            "available_credits": credits.get("available_credits"),
            "auto_reload_enabled": credits.get("auto_reload_enabled"),
            "auto_reload_threshold": credits.get("auto_reload_threshold"),
            "auto_reload_amount": credits.get("auto_reload_amount"),
        }


class _GatewayNamespace(_BaseNamespace):
    def status(self) -> Dict[str, Any]:
        return self._client._request("GET", "/v2/health")


# ---------------------------------------------------------------------- #
# Jobs namespace
# ---------------------------------------------------------------------- #
class JobTimeoutError(OMTXError):
    """Raised when waiting for a job exceeds the allowed timeout."""


class _JobsNamespace(_BaseNamespace):
    def history(
        self,
        *,
        endpoint: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"limit": limit}
        if endpoint:
            payload["endpoint"] = endpoint
        if status:
            payload["status"] = status
        if cursor:
            payload["cursor"] = cursor
        return self._client._request("GET", "/v2/jobs/history", params=payload)

    def status(self, job_id: str) -> Dict[str, Any]:
        if not job_id:
            raise OMTXError("job_id is required")
        return self._client._request("GET", f"/v2/jobs/{job_id}")

    def result(self, job_id: str) -> Dict[str, Any]:
        return self.status(job_id)

    def wait(
        self,
        job_id: str,
        *,
        result_endpoint: Optional[str] = None,
        poll_interval: float = 5.0,
        timeout: Optional[float] = 3600.0,
    ) -> Dict[str, Any]:
        if not job_id:
            raise OMTXError("job_id is required")

        start = time.monotonic()
        while True:
            status = self.status(job_id)
            state = status.get("status")
            if state == "succeeded":
                if result_endpoint:
                    endpoint = result_endpoint.format(job_id=job_id)
                    return self._client._request("GET", endpoint)
                return status
            if state in {"failed", "canceled", "expired"}:
                status_code = (
                    status.get("status_code")
                    or status.get("response_status")
                    or 500
                )
                detail = (
                    status.get("error")
                    or status.get("detail")
                    or status.get("response_payload")
                )
                if isinstance(detail, dict):
                    detail = json.dumps(detail)
                message = detail or f"Job {job_id} finished with status {state}"
                raise APIError(message, status_code=status_code)

            if timeout is not None and (time.monotonic() - start) > timeout:
                raise JobTimeoutError(f"Timed out waiting for job {job_id}")
            time.sleep(poll_interval)
