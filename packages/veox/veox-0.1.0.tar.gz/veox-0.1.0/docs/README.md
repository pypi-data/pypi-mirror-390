# Veox

Veox is a lightweight Python client that mimics an sklearn-style workflow for piloting experiments against the DOUG scheduler. It ships with a minimal in-memory model, a consistent persistence layer, and clean extension points for wiring DOUG API interactions without depending on the DOUG codebase directly.

## Features
- Familiar API surface: `fit`, `predict`, `save`, and `status`.
- Safe persistence helpers (`veox.io`) with defensive error handling.
- Typed state container (`veox.model`) for capturing training metadata and timestamps.
- Hooks for submitting datasets to the DOUG scheduler via HTTP (see [`docs/test_deepdive.md`](../doug/docs/test_deepdive.md) in the DOUG project for API expectations).
- Zero runtime dependencies; optional dev extras for testing and packaging.

## Quickstart
```python
from veox import Veox

model = Veox()
model.fit(X=[[1, 2], [3, 4]], y=[0, 1])
predictions = model.predict([[5, 6]])
model.save("veox_model.json")
print(model.status())
```

## Installation
Once published to PyPI:
```
pip install veox
```

For local development:
```
python -m pip install --upgrade pip
pip install -e .[dev]
```

## DOUG Scheduler Integration
Veox keeps the core HTTP integration optional so that local development does not require the DOUG repository. Configure the following environment variables before calling any DOUG-related helpers:

- `VEOX_DOUG_BASE_URL`: Base URL for the scheduler (e.g. `http://localhost:8088`).
- `VEOX_DOUG_API_KEY`: API key to attach via `X-API-Key`.
- `VEOX_DOUG_TIMEOUT`: Optional request timeout in seconds (defaults to `30`).

Refer to `/Users/bentaylor/Code/doug/doug/docs/test_deepdive.md` for end-to-end workflow expectations and recommended harness commands. Once configured you can submit a dataset directly:
```python
import os
from veox import Veox

os.environ["VEOX_DOUG_BASE_URL"] = "http://localhost:8088"
os.environ["VEOX_DOUG_API_KEY"] = "veox-demo-token"

model = Veox().fit([[1.0, 2.0], [3.0, 4.0]])
response = model.submit_to_doug(
    dataset_name="Human:Ackley",
    endpoint="/v1/jobs",
    hyperparameters={"population": 4, "generations": 2},
)
print(response)
```

## Development Workflow
- **Run tests**: `./scripts/run_tests.sh`
- **Build dist artifacts**: `./scripts/build_package.sh`
- **Publish to PyPI (requires credentials)**: `./scripts/publish_package.sh`
- **End-to-end dummy demo**: `python scripts/demo_dummy_submission.py`
- **Containerized tests**: `./scripts/docker_run_tests.sh` (uses Podman/Docker with detailed logging)
- **Containerized build**: `./scripts/docker_build_package.sh`
- **Publish & verify PyPI release**: `./scripts/publish_and_verify.sh` (pushes with `twine`, waits for propagation, installs released version in a fresh venv)

Each script sources a local `.env` (not tracked) for secrets. Create `.env` with:
```
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your-project-token
```

## Local Publishing
1. Create `~/.pypirc` with:
   ```
   [distutils]
     index-servers =
       pypi

   [pypi]
     username = __token__
     password = <project token, including pypi- prefix>
   ```
2. Build and upload:
   ```
   python -m build
   twine upload dist/*
   ```
3. To automate the full release cycle, set `TWINE_USERNAME/TWINE_PASSWORD` in `.env` and run `./scripts/publish_and_verify.sh` (defaults to a 180s wait before verifying `pip install` from PyPI). Use `PYPI_WAIT_SECONDS=300` if you need a longer propagation window.

## Continuous Integration
GitLab CI runs tests on every commit and builds packages for tag pipelines. Tagged releases also trigger a `twine` upload that reads `TWINE_USERNAME` and `TWINE_PASSWORD` from masked CI/CD variables.

## Next Steps
- Tag `v0.1.0` and push to trigger the CI build/publish pipeline.
- Exercise the DOUG verbose API harnesses with the persisted Veox model to validate remote dataset routing.
- Iterate on richer model logic and extend tests as real-world datasets become available.

