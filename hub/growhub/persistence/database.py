"""Criação explícita do engine e de sessões do hub."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def create_database_engine(url: str, *, echo: bool = False) -> Engine:
    if not url or "://" not in url:
        raise ValueError("URL de banco inválida")
    return create_engine(url, echo=echo, pool_pre_ping=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
