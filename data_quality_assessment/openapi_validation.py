from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path
import yaml
import requests
from endpoints import ROOT

# openapi-core imports (version-dependent, this is a common pattern)
from openapi_core import OpenAPI
from openapi_core.validation.response.exceptions import ResponseValidationError
from openapi_core.contrib.requests import RequestsOpenAPIRequest, RequestsOpenAPIResponse


@dataclass
class EndpointCheckResult:
    method: str
    url: str
    status_code: int
    contract_valid: bool
    error: Optional[str] = None


def load_openapi(spec_path: str):
    with Path(spec_path).open("r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    return OpenAPI.from_dict(spec)


def validate_endpoint_response(app: OpenAPI, method: str, url: str, **kwargs) -> EndpointCheckResult:
    """
    Calls an endpoint and validates the actual response against the OpenAPI spec.
    """
    method = method.upper()

    try:
        resp = requests.request(method, url, timeout=15, **kwargs)

        # Wrap request/response for openapi-core
        req_wrapper = RequestsOpenAPIRequest(resp.request)
        resp_wrapper = RequestsOpenAPIResponse(resp)

        # Validate runtime response against spec contract
        app.validate_response(req_wrapper, resp_wrapper)

        return EndpointCheckResult(
            method=method,
            url=url,
            status_code=resp.status_code,
            contract_valid=True,
            error=None,
        )

    except ResponseValidationError as e:
        return EndpointCheckResult(
            method=method,
            url=url,
            status_code=getattr(locals().get("resp", None), "status_code", 0),
            contract_valid=False,
            error=f"OpenAPI response validation error: {e}",
        )
    except Exception as e:
        return EndpointCheckResult(
            method=method,
            url=url,
            status_code=getattr(locals().get("resp", None), "status_code", 0),
            contract_valid=False,
            error=f"Execution error: {e}",
        )


def scan_nulls(records):
    nullable_counts = {}
    for rec in records:
        # top-level
        for k, v in rec.items():
            if v is None:
                nullable_counts[k] = nullable_counts.get(k, 0) + 1
        # nested examples
        if isinstance(rec.get("country"), dict):
            for k, v in rec["country"].items():
                if v is None:
                    nullable_counts[f"country.{k}"] = nullable_counts.get(f"country.{k}", 0) + 1
        if isinstance(rec.get("region"), dict):
            for k, v in rec["region"].items():
                if v is None:
                    nullable_counts[f"region.{k}"] = nullable_counts.get(f"region.{k}", 0) + 1
    return nullable_counts


def main():
    spec_path = "go_api.yaml"
    app = load_openapi(spec_path)

    checks = [
        {"method": "GET", "url": f"{ROOT}api/v2/appeal"}
    ]

    results: List[EndpointCheckResult] = []
    for c in checks:
        r = validate_endpoint_response(app, c["method"], c["url"])
        results.append(r)

    # Simple scorecard
    passed = sum(1 for r in results if r.contract_valid)
    total = len(results)
    score = round((passed / total) * 100, 1) if total else 0

    print("\n=== Contract Validation Scorecard ===")
    print(f"Passed: {passed}/{total} ({score}%)")

    # Fetch payload for null diagnosis (use the same endpoint)
    resp = requests.get(f"{ROOT}api/v2/appeal", timeout=15)
    payload = resp.json()
    records = payload.get("results", []) if isinstance(payload, dict) else []

    diagnosis = scan_nulls(records)
    print("Null field counts:", diagnosis)

    for r in results:
        status = "✅ PASS" if r.contract_valid else "❌ FAIL"
        print(f"{status} {r.method} {r.url} -> HTTP {r.status_code}")
        if r.error:
            print("Error found")



if __name__ == "__main__":
    main()
