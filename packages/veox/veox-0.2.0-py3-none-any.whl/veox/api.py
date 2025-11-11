"""User-facing API for the Veox package."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from . import __version__  # type: ignore circular import handled at runtime
from .io import write_json
from .model import (
    DougConfig,
    VeoxDataError,
    VeoxState,
    compute_column_means,
    prepare_matrix,
)
from .doug import VeoxDougError, post_json

LOGGER = logging.getLogger(__name__)


class Veox:
    """A minimal, sklearn-inspired interface for DOUG scheduler experimentation."""

    def __init__(self, *, logger: logging.Logger | None = None) -> None:
        self._logger = logger or LOGGER
        self._state: VeoxState | None = None
        self._doug_config = DougConfig.from_env()
        self._last_saved_path: Path | None = None
        self._logger.debug("Initialized Veox with DOUG config: %s", self._doug_config)

    # --------------------------------------------------------------------- #
    # Core training & inference
    # --------------------------------------------------------------------- #
    def fit(
        self,
        X: Sequence[Iterable[float]],
        y: Sequence[Iterable[float]] | Sequence[float] | None = None,
        **kwargs: Any,
    ) -> "Veox":
        """
        Fit the model on the provided dataset.

        Parameters
        ----------
        X:
            Sequence of feature rows. Each row must be numeric and equal length.
        y:
            Optional targets. Present for API compatibility but unused in this baseline implementation.
        kwargs:
            Additional metadata (stored for inspection via :meth:`status`).
        """
        matrix = prepare_matrix(X)
        column_means = compute_column_means(matrix)

        metadata: Dict[str, str] = {"rows": str(len(matrix))}
        if y is not None:
            metadata["targets_provided"] = str(len(y))
        metadata.update({key: str(value) for key, value in kwargs.items()})

        self._state = VeoxState(
            n_features=len(column_means),
            column_means=column_means,
            metadata=metadata,
        )
        self._logger.info(
            "Veox fitted on %d rows with %d features.", len(matrix), len(column_means)
        )
        return self

    def predict(self, X: Sequence[Iterable[float]], **_: Any) -> List[float]:
        """
        Generate deterministic predictions based on stored column means.

        Returns a list whose length matches the number of input rows.
        """
        if self._state is None or not self._state.is_fitted:
            raise RuntimeError("Model has not been fitted yet.")

        matrix = prepare_matrix(X)
        if len(matrix[0]) != self._state.n_features:
            raise VeoxDataError(
                f"Expected {self._state.n_features} features, received {len(matrix[0])}."
            )

        predictions = []
        for row in matrix:
            residual = sum((value - mean) ** 2 for value, mean in zip(row, self._state.column_means))
            predictions.append(residual)

        self._logger.debug("Generated %d predictions.", len(predictions))
        return predictions

    # --------------------------------------------------------------------- #
    # Persistence
    # --------------------------------------------------------------------- #
    def save(self, path: str | Path) -> Path:
        """Persist the current model state to a JSON file."""
        if self._state is None or not self._state.is_fitted:
            raise RuntimeError("Cannot save an unfitted model.")

        payload = self._state.to_dict()
        target = write_json(path, payload)
        self._last_saved_path = target
        self._logger.info("Saved Veox model to %s", target)
        return target

    # --------------------------------------------------------------------- #
    # Instrumentation
    # --------------------------------------------------------------------- #
    def status(self) -> Dict[str, Any]:
        """Return diagnostic information about the model."""
        fitted = self._state.is_fitted if self._state else False
        timestamp = self._state.created_at.isoformat() if self._state else None

        return {
            "version": __version__,
            "is_fitted": fitted,
            "timestamp": timestamp,
            "n_features": self._state.n_features if self._state else None,
            "metadata": self._state.metadata if self._state else {},
            "doug_configured": self._doug_config is not None,
            "last_saved_path": str(self._last_saved_path) if self._last_saved_path else None,
        }

    # --------------------------------------------------------------------- #
    # DOUG integration scaffolding
    # --------------------------------------------------------------------- #
    def build_doug_payload(self, dataset_name: str, **extra: Any) -> Dict[str, Any]:
        """
        Compose a minimal payload for submitting a dataset to the DOUG scheduler.

        Parameters
        ----------
        dataset_name:
            The dataset identifier recognised by the DOUG HTTP API.
        extra:
            Additional keyword arguments appended to the payload.
        """
        if not dataset_name:
            raise ValueError("dataset_name must be provided.")

        payload = {"dataset": dataset_name, "metadata": self.status()}
        payload.update(extra)
        self._logger.debug("Prepared DOUG payload for dataset %s: %s", dataset_name, payload)
        return payload

    def submit_to_doug(
        self,
        dataset_name: str,
        *,
        endpoint: str = "/v1/jobs",
        timeout: float | None = None,
        **extra: Any,
    ) -> Dict[str, Any]:
        """
        Submit a dataset payload to the DOUG scheduler and return the JSON response.

        Parameters
        ----------
        dataset_name:
            Identifier recognised by the DOUG API.
        endpoint:
            Endpoint path relative to the configured base URL (defaults to ``/v1/jobs``).
        timeout:
            Optional override for the request timeout in seconds.
        extra:
            Additional fields merged into the payload.
        """
        if self._doug_config is None:
            raise VeoxDougError(
                "DOUG configuration is missing. Set VEOX_DOUG_BASE_URL (and optional API key)."
            )

        payload = self.build_doug_payload(dataset_name, **extra)
        base_url = self._doug_config.base_url.rstrip("/")
        rel_endpoint = endpoint.lstrip("/")
        url = f"{base_url}/{rel_endpoint}"
        headers = self._doug_config.headers()
        response = post_json(url, payload, headers=headers, timeout=timeout or self._doug_config.timeout)
        self._logger.info(
            "Submitted dataset '%s' to DOUG endpoint %s (status %d).",
            dataset_name,
            endpoint,
            response.status,
        )
        return response.to_dict()

