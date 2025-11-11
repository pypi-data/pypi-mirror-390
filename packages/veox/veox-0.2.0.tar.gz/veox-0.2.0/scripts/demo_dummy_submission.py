#!/usr/bin/env python
"""Run a self-contained demo submitting to a dummy DOUG server."""
from __future__ import annotations

import os
import sys
from contextlib import closing

from veox import Veox
from veox.dummy import DummyDougServer


def main() -> int:
    with DummyDougServer() as server:
        print(f"[veox] Started dummy DOUG server at {server.url}")
        os.environ.setdefault("VEOX_DOUG_BASE_URL", server.url)
        os.environ.setdefault("VEOX_DOUG_API_KEY", "demo-token")

        model = Veox()
        model.fit([[1.0, 2.0], [3.0, 4.0]], experiment="demo-script")

        response = model.submit_to_doug(
            "Human:Ackley",
            endpoint="/v1/jobs",
            hyperparameters={"population": 4, "generations": 2},
        )

        print("[veox] DOUG response:", response)
        last_request = server.last_request
        if last_request:
            print("[veox] Recorded request payload:", last_request.payload)
        else:
            print("[veox] No request recorded!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

