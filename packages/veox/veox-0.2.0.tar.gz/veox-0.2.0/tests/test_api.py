from __future__ import annotations

from pathlib import Path

import pytest

from veox import Veox


def test_can_instantiate_and_status():
    model = Veox()
    status = model.status()
    assert status["version"] == "0.2.0"
    assert status["is_fitted"] is False
    assert status["timestamp"] is None
    assert "doug_configured" in status


def test_fit_and_predict(sample_features, sample_targets):
    model = Veox()
    model.fit(sample_features, sample_targets, experiment="unit-test")
    predictions = model.predict(sample_features)
    assert len(predictions) == len(sample_features)
    assert all(isinstance(val, float) for val in predictions)

    status = model.status()
    assert status["is_fitted"] is True
    assert status["n_features"] == len(sample_features[0])
    assert status["metadata"]["targets_provided"] == str(len(sample_targets))
    assert status["metadata"]["experiment"] == "unit-test"


def test_save_creates_file(sample_features, model_path: Path):
    model = Veox()
    model.fit(sample_features)
    saved_path = model.save(model_path)
    assert saved_path.exists()
    assert saved_path.read_text(encoding="utf-8")

    status = model.status()
    assert status["last_saved_path"] == str(saved_path)


@pytest.mark.usefixtures("dummy_doug_server")
def test_submit_to_doug(dummy_doug_server, sample_features, monkeypatch):
    monkeypatch.setenv("VEOX_DOUG_BASE_URL", dummy_doug_server.url)
    monkeypatch.setenv("VEOX_DOUG_API_KEY", "test-token")

    model = Veox()
    model.fit(sample_features)
    response = model.submit_to_doug(
        "Human:Ackley",
        endpoint="/v1/jobs",
        hyperparameters={"population": 2, "generations": 1},
    )

    assert response["status"] == 200
    assert response["body"]["status"] == "queued"
    assert response["body"]["job_id"] == "dummy-job"

    last_request = dummy_doug_server.last_request
    assert last_request is not None
    assert last_request.path == "/v1/jobs"
    headers = {k.lower(): v for k, v in last_request.headers.items()}
    assert headers["x-api-key"] == "test-token"
    assert last_request.payload["dataset"] == "Human:Ackley"
    assert last_request.payload["metadata"]["is_fitted"] is True
    assert last_request.payload["hyperparameters"] == {"population": 2, "generations": 1}

