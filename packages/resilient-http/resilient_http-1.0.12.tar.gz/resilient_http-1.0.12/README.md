# 🚀 Resilient HTTP — Smart, Fault-Tolerant HTTP Client for Python

[![CI](https://github.com/pgnikolov/resilient-http/actions/workflows/tests.yml/badge.svg)](https://github.com/pgnikolov/resilient-http/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/pgnikolov/resilient-http/branch/main/graph/badge.svg)](https://codecov.io/gh/pgnikolov/resilient-http)
[![PyPI version](https://img.shields.io/pypi/v/resilient-http.svg)](https://pypi.org/project/resilient-http/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> A modern, production-grade HTTP client wrapper with **automatic retries**, **circuit breakers**, **jittered backoff**, and **metrics integration** — all built for reliability under failure.

---

## ✨ Features

| ⚙️ Capability | 💡 Description |
|---------------|----------------|
| 🔁 **Automatic Retries** | Configurable retry logic for transient errors and specific HTTP status codes. |
| ⛔ **Circuit Breaker** | Opens and closes circuits based on failures to prevent cascading service outages. |
| ⏱ **Exponential Backoff + Jitter** | Prevents thundering-herd retry storms under heavy load. |
| 📈 **Metrics Hooks** | Customizable metrics sinks for Prometheus, OpenTelemetry, or custom tracking. |
| ⚡ **Async + Sync Clients** | Full support for both `requests` and `httpx` async workflows. |
| 🧠 **Configurable Policies** | Fine-grained control of retry rules, idempotency, and exception handling. |
| 🧪 **100% Tested** | Comprehensive pytest suite with CI and coverage reports. |

---

## 📦 Installation

```bash
pip install resilient-http
````

or for the latest development version:

```bash
pip install git+https://github.com/pgnikolov/resilient-http.git
```

---

## 🚀 Quickstart Examples

### 🧩 Synchronous (Requests)

```python
from resilient_http.resilient_session import ResilientRequestsSession
from resilient_http.retry_policy import RetryPolicy
from resilient_http.circuit_breaker import CircuitBreaker

retry_policy = RetryPolicy(max_attempts=3)
cb = CircuitBreaker(max_failures=2, reset_timeout=10)

session = ResilientRequestsSession(retry_policy=retry_policy, circuit_breaker=cb)

response = session.get("https://httpbin.org/status/503")
print(response.status_code)
```

**Output example:**

```
503 (retrying...)
200
```

---

### ⚙️ Asynchronous (HTTPX)

```python
import asyncio
from resilient_http.resilient_async_client import ResilientAsyncClient
from resilient_http.retry_policy import RetryPolicy

async def main():
    client = ResilientAsyncClient(retry_policy=RetryPolicy(max_attempts=3))
    resp = await client.get("https://httpbin.org/status/503")
    print(resp.status_code)

asyncio.run(main())
```

---

## 🔄 Configuration

All retry and circuit breaker parameters are configurable:

| Parameter          | Type         | Default                | Description                                  |
| ------------------ | ------------ | ---------------------- | -------------------------------------------- |
| `max_attempts`     | `int`        | `3`                    | Maximum retry attempts per request           |
| `retry_on_status`  | `tuple[int]` | `(500, 502, 503, 504)` | Status codes that trigger retries            |
| `backoff_strategy` | `callable`   | `exponential_backoff`  | Backoff function controlling retry delay     |
| `max_failures`     | `int`        | `5`                    | Failures before circuit breaker opens        |
| `reset_timeout`    | `float`      | `30.0`                 | Time before circuit transitions to half-open |

Backoff functions can be customized via:

```python
from resilient_http.backoff import exponential_backoff, full_jitter

exp = exponential_backoff(base=2, factor=0.5, max_delay=8)
jittered = full_jitter(exp)
```

---

## 🧩 Metrics Integration

You can attach a metrics sink to collect circuit and retry events:

```python
from resilient_http.metrics import MetricsSink

class PrintMetrics(MetricsSink):
    def record_event(self, event: str, **data):
        print(f"[metrics] {event}: {data}")

session = ResilientRequestsSession(metrics_sink=PrintMetrics())
```

Output:

```
[metrics] retry: {'url': 'https://api.service', 'attempt': 1, 'reason': '503'}
[metrics] cb_open: {'key': 'GET https://api.service', 'failures': 5}
```

---

## 🧱 Project Structure

```
resilient-http/
├── resilient_http/
│   ├── __init__.py
│   ├── backoff.py
│   ├── circuit_breaker.py
│   ├── exceptions.py
│   ├── metrics.py
│   ├── resilient_async_client.py
│   ├── resilient_session.py
│   └── retry_policy.py
├── tests/
├── pyproject.toml
├── .coveragerc
└── README.md
```

---

## 🧪 Running Tests Locally

```bash
pytest --cov=resilient_http --cov-report=term-missing
```

Example output:

```
22 passed in 1.47s
TOTAL COVERAGE: 82%
```

---

## 🧰 Development Setup

```bash
git clone https://github.com/pgnikolov/resilient-http.git
cd resilient-http
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .[dev]
pytest
```

---

## 🧬 Continuous Integration (GitHub Actions)

The CI workflow runs tests on Linux, macOS, and Windows using multiple Python versions.

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e .[dev]
      - run: pytest --cov=resilient_http --cov-report=term-missing
```

---

## 🧾 License

This project is licensed under the terms of the **MIT License**.
See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Plamen Nikolov**
📍 Oosterhout, Netherlands
💼 GitHub: [@pgnikolov](https://github.com/pgnikolov)

---

## ❤️ Contributing

Contributions are welcome!
Please open issues or submit PRs with improvements or additional features.

---

## 🌟 Support

If this project helps you build more resilient systems, please ⭐ the repo on GitHub!
