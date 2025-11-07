from __future__ import annotations

import hashlib
import json
import os
import time
import warnings
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

_SELECTIVE_DATASET = "selectivity"
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


class JobTimeoutError(OMTXError):
    """Raised when waiting for a job exceeds the allowed timeout."""


class OMTXClient:
    """Lightweight Python client for the OM Gateway."""

    class SelectiveStream:
        """Wrapper around streaming responses for data access endpoints."""

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
            """Materialize the stream as a pandas DataFrame.

            Args:
                max_bytes: Maximum number of bytes to read before giving up.
                close: Whether to close the underlying HTTP response when done.
            """
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

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "OMTXClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _headers(
        self, idem_key: Optional[str], *, accept: Optional[str] = None
    ) -> Dict[str, str]:
        headers = {
            "x-api-key": self.cfg.api_key,
            "accept": accept or "application/json",
        }
        if idem_key:
            headers["idempotency-key"] = idem_key
            headers["content-type"] = "application/json"
        return headers

    @staticmethod
    def _validate_selective_dataset(dataset: Optional[str]) -> str:
        value = (dataset or _SELECTIVE_DATASET).strip().lower()
        if value != _SELECTIVE_DATASET:
            raise OMTXError(
                f"dataset must be '{_SELECTIVE_DATASET}' for selective access"
            )
        return _SELECTIVE_DATASET

    @staticmethod
    def _normalize_points_dataset(dataset: Optional[str]) -> str:
        value = (dataset or "public").strip().lower()
        if value not in _POINTS_DATASETS:
            allowed = ", ".join(sorted(_POINTS_DATASETS))
            raise OMTXError(
                f"dataset must be one of {{{allowed}}} for points access"
            )
        return value

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
        body: Optional[Dict[str, Any]] = None,
        *,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        method = method.upper()
        url = f"{self.cfg.base_url}{path}"

        if method == "GET":
            params = body or {}
            json_payload = None
            headers = self._headers(None)
        else:
            json_payload = body or {}
            params = None
            idem = _derive_idempotency_key(idempotency_key, method, path, json_payload)
            headers = self._headers(idem)
            if "content-type" not in headers:
                headers["content-type"] = "application/json"

        resp = self._session.request(
            method=method,
            url=url,
            headers=headers,
            json=json_payload,
            params=params,
            timeout=self.cfg.timeout,
        )

        if resp.status_code >= 400:
            self._handle_error(resp, path)

        if not resp.content:
            return {}

        try:
            return resp.json()
        except Exception:
            raise OMTXError(f"Non-JSON response from {path}")

    # ------------------------------------------------------------------ #
    # Health & credits
    # ------------------------------------------------------------------ #
    def health(self) -> Dict[str, Any]:
        return self._request("GET", "/v2/health", {})

    def credits(self) -> Dict[str, Any]:
        return self._request("GET", "/v2/credits", {})

    # ------------------------------------------------------------------ #
    # Jobs
    # ------------------------------------------------------------------ #
    def jobs_history(
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
        return self._request("GET", "/v2/jobs/history", payload)

    def job_status(self, job_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v2/jobs/{job_id}", {})

    def wait_for_job(
        self,
        job_id: str,
        *,
        result_endpoint: Optional[str] = None,
        poll_interval: float = 5.0,
        timeout: Optional[float] = 3600.0,
    ) -> Dict[str, Any]:
        """Poll the gateway until a job succeeds or fails."""
        start = time.monotonic()
        while True:
            status = self.job_status(job_id)
            state = status.get("status")
            if state == "succeeded":
                if result_endpoint:
                    endpoint = result_endpoint.format(job_id=job_id)
                    return self._request("GET", endpoint, {})
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
                raise APIError(
                    f"{message}", status_code=status_code
                )
            if timeout is not None and (time.monotonic() - start) > timeout:
                raise JobTimeoutError(f"Timed out waiting for job {job_id}")
            time.sleep(poll_interval)

    def job_result(self, job_id: str) -> Dict[str, Any]:
        """Return the stored payload and metadata for a job."""
        return self.job_status(job_id)

    # ------------------------------------------------------------------ #
    # Diligence endpoints (job-backed)
    # ------------------------------------------------------------------ #
    def diligence_generate_claims(
        self,
        *,
        target: str,
        prompt: str,
        idempotency_key: Optional[str] = None,
        wait: bool = False,
        poll_interval: float = 5.0,
        timeout: Optional[float] = 3600.0,
    ) -> Dict[str, Any]:
        if not target:
            raise OMTXError("target is required for generate claims")
        if not prompt:
            raise OMTXError("prompt is required for generate claims")
        payload = {"target": target, "prompt": prompt}
        response = self._request(
            "POST",
            "/v2/diligence/generateClaims",
            payload,
            idempotency_key=idempotency_key,
        )
        job_id = response.get("job_id")
        if wait and job_id:
            return self.wait_for_job(
                job_id,
                result_endpoint="/v2/jobs/generateClaims/{job_id}",
                poll_interval=poll_interval,
                timeout=timeout,
            )
        return response

    def diligence_synthesize_report(
        self,
        *,
        gene_key: str,
        idempotency_key: Optional[str] = None,
        wait: bool = False,
        poll_interval: float = 5.0,
        timeout: Optional[float] = 3600.0,
    ) -> Dict[str, Any]:
        if not gene_key:
            raise OMTXError("gene_key is required for synthesize report jobs")
        payload = {"gene_key": gene_key}
        response = self._request(
            "POST",
            "/v2/diligence/synthesizeReport",
            payload,
            idempotency_key=idempotency_key,
        )
        job_id = response.get("job_id")
        if wait and job_id:
            return self.wait_for_job(
                job_id,
                result_endpoint="/v2/jobs/synthesizeReport/{job_id}",
                poll_interval=poll_interval,
                timeout=timeout,
            )
        return response

    def diligence_deep_research(
        self,
        *,
        query: str,
        max_iterations: Optional[int] = None,
        prompts_per_iteration: Optional[int] = None,
        final_report_provider: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        wait: bool = False,
        poll_interval: float = 5.0,
        timeout: Optional[float] = 3600.0,
    ) -> Dict[str, Any]:
        if not query:
            raise OMTXError("query is required for deep research")
        payload: Dict[str, Any] = {"query": query}
        if max_iterations is not None:
            payload["max_iterations"] = max_iterations
        if prompts_per_iteration is not None:
            payload["prompts_per_iteration"] = prompts_per_iteration
        if final_report_provider is not None:
            payload["final_report_provider"] = final_report_provider

        response = self._request(
            "POST",
            "/v2/diligence/deep-research",
            payload,
            idempotency_key=idempotency_key,
        )
        job_id = response.get("job_id")
        if wait and job_id:
            return self.wait_for_job(
                job_id,
                result_endpoint="/v2/jobs/deep-research/{job_id}",
                poll_interval=poll_interval,
                timeout=timeout,
            )
        return response

    def diligence_get_generate_claims_job(self, job_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v2/jobs/generateClaims/{job_id}", {})

    def diligence_get_synthesize_report_job(self, job_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v2/jobs/synthesizeReport/{job_id}", {})

    def diligence_get_deep_research_job(self, job_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v2/jobs/deep-research/{job_id}", {})

    def diligence_list_gene_keys(
        self,
        *,
        min_true: int = 1,
        limit: int = 100,
        offset: int = 0,
        q: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "min_true": min_true,
            "limit": limit,
            "offset": offset,
        }
        if q:
            payload["q"] = q
        return self._request("GET", "/v2/diligence/gene-keys", payload)

    # ------------------------------------------------------------------ #
    # Access credits & data access
    # ------------------------------------------------------------------ #
    def access_unlock(
        self,
        *,
        protein_uuid: str,
        gene_name: Optional[str] = None,
        protein: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not protein_uuid:
            raise OMTXError("protein_uuid is required for access_unlock")
        payload: Dict[str, Any] = {"protein_uuid": protein_uuid}
        if gene_name:
            payload["gene_name"] = gene_name
        if protein:
            payload["protein"] = protein
        return self._request(
            "POST",
            "/v2/access/unlock",
            payload,
            idempotency_key=idempotency_key,
        )

    def list_access_unlocks(self) -> Dict[str, Any]:
        return self._request("GET", "/v2/access/unlocks", {})

    def data_access_selective_stream(
        self,
        *,
        dataset: str = _SELECTIVE_DATASET,
        protein_uuid: Optional[str] = None,
        limit: Optional[int] = None,
        get_all: bool = False,
    ) -> "OMTXClient.SelectiveStream":
        normalized_dataset = self._validate_selective_dataset(dataset)
        if not protein_uuid:
            raise OMTXError("protein_uuid is required for selective dataset access")

        params: Dict[str, Any] = {
            "dataset": normalized_dataset,
            "protein_uuid": protein_uuid,
        }
        if limit is not None:
            limit = int(limit)
            if limit < 1 or limit > _MAX_SELECTIVE_LIMIT:
                raise OMTXError(
                    f"limit must be between 1 and {_MAX_SELECTIVE_LIMIT:,} for selective access"
                )
            params["limit"] = limit
        if get_all:
            warnings.warn(
                "get_all is deprecated for selective access; "
                "use stats + limit instead.",
                RuntimeWarning,
                stacklevel=2,
            )
            params["get_all"] = "true"

        resp = self._session.get(
            f"{self.cfg.base_url}/v2/data-access/selective",
            headers=self._headers(None, accept="text/csv"),
            params=params,
            stream=True,
            timeout=self.cfg.timeout,
        )
        if resp.status_code >= 400:
            self._handle_error(resp, "/v2/data-access/selective")
        return OMTXClient.SelectiveStream(resp)

    def data_access_points_stream(
        self,
        *,
        dataset: str = "public",
        protein_uuid: Optional[str] = None,
        limit: Optional[int] = None,
        get_all: bool = False,
    ) -> "OMTXClient.SelectiveStream":
        normalized_dataset = self._normalize_points_dataset(dataset)
        params: Dict[str, Any] = {"dataset": normalized_dataset}

        requires_protein = normalized_dataset != "decoys"
        if requires_protein:
            if not protein_uuid:
                raise OMTXError(
                    "protein_uuid is required for public/private/community datasets"
                )
            params["protein_uuid"] = protein_uuid
        elif protein_uuid:
            params["protein_uuid"] = protein_uuid

        if limit is not None:
            limit = int(limit)
            if limit < 1 or limit > _MAX_POINTS_LIMIT:
                raise OMTXError(
                    f"limit must be between 1 and {_MAX_POINTS_LIMIT:,} for points access"
                )
            params["limit"] = limit
        if get_all:
            warnings.warn(
                "get_all is deprecated for points access; "
                "use stats + limit instead.",
                RuntimeWarning,
                stacklevel=2,
            )
            params["get_all"] = "true"

        resp = self._session.get(
            f"{self.cfg.base_url}/v2/data-access/points",
            headers=self._headers(None, accept="text/csv"),
            params=params,
            stream=True,
            timeout=self.cfg.timeout,
        )
        if resp.status_code >= 400:
            self._handle_error(resp, "/v2/data-access/points")
        return OMTXClient.SelectiveStream(resp)

    def data_access_selective_stats(
        self,
        *,
        dataset: str = _SELECTIVE_DATASET,
        protein_uuid: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_dataset = self._validate_selective_dataset(dataset)
        if not protein_uuid:
            raise OMTXError("protein_uuid is required for selective stats")
        payload: Dict[str, Any] = {
            "dataset": normalized_dataset,
            "protein_uuid": protein_uuid,
        }
        return self._request(
            "GET",
            "/v2/data-access/selective/stats",
            payload,
        )

    def data_access_points_stats(
        self,
        *,
        dataset: str = "public",
        protein_uuid: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_dataset = self._normalize_points_dataset(dataset)
        payload: Dict[str, Any] = {"dataset": normalized_dataset}
        requires_protein = normalized_dataset != "decoys"
        if requires_protein:
            if not protein_uuid:
                raise OMTXError(
                    "protein_uuid is required for public/private/community stats"
                )
            payload["protein_uuid"] = protein_uuid
        elif protein_uuid:
            payload["protein_uuid"] = protein_uuid
        return self._request(
            "GET",
            "/v2/data-access/points/stats",
            payload,
        )

    def data_access_points_cost_estimate(
        self,
        *,
        dataset: str = "public",
        protein_uuid: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Estimate rows and cents that will be billed for a points stream."""
        stats = self.data_access_points_stats(
            dataset=dataset, protein_uuid=protein_uuid
        )
        total_rows = int(stats.get("total_rows") or 0)

        if limit is None:
            effective_limit = total_rows
        else:
            limit = int(limit)
            if limit < 1 or limit > _MAX_POINTS_LIMIT:
                raise OMTXError(
                    f"limit must be between 1 and {_MAX_POINTS_LIMIT:,} for points access"
                )
            effective_limit = min(limit, total_rows)

        cost_cents = effective_limit  # 1¢ per row
        return {
            "rows": effective_limit,
            "cost_cents": cost_cents,
            "pricing": {
                "base_cost_cents": 1,
                "multiplier_field": "row_count",
                "total_rows": total_rows,
            },
            "stats": stats,
        }
