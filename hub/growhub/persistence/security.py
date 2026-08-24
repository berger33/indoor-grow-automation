"""Repositório PostgreSQL de contas locais."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ..services.security import UserAccount, UserRole
from .models import UserRow


class SqlUserRepository:
    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self._sessions = sessions

    def load(self) -> tuple[UserAccount, ...]:
        with self._sessions() as session:
            return tuple(
                UserAccount(row.user_id, row.display_name, UserRole[row.role.upper()], row.password_hash, row.enabled)
                for row in session.scalars(select(UserRow).order_by(UserRow.user_id)).all()
            )

    def save(self, account: UserAccount) -> None:
        with self._sessions.begin() as session:
            if session.get(UserRow, account.user_id) is not None:
                raise ValueError("usuário já existe no banco")
            session.add(
                UserRow(
                    user_id=account.user_id,
                    display_name=account.display_name,
                    role=account.role.name.lower(),
                    password_hash=account.password_hash,
                    enabled=account.enabled,
                    created_at=datetime.now(UTC),
                )
            )
