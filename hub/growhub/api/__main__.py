"""Inicia o serviço local; credenciais são lidas somente do ambiente."""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.environ.get("GROWHUB_BIND_HOST", "127.0.0.1")
    port = int(os.environ.get("GROWHUB_BIND_PORT", "8000"))
    if not 1 <= port <= 65_535:
        raise ValueError("GROWHUB_BIND_PORT fora da faixa válida")
    uvicorn.run(
        "hub.growhub.api.runtime:build_runtime_app",
        factory=True,
        host=host,
        port=port,
    )


if __name__ == "__main__":
    main()
