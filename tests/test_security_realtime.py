import asyncio
from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.services.realtime import RealtimeBuffer
from hub.growhub.services.security import AuthService, PasswordHasher, UserAccount, UserRole


class SecurityTests(TestCase):
    def test_password_hash_is_salted_and_token_expires(self) -> None:
        hasher = PasswordHasher()
        first = hasher.hash("correct-horse-battery")
        second = hasher.hash("correct-horse-battery")
        self.assertNotEqual(first, second)
        self.assertTrue(hasher.verify("correct-horse-battery", first))
        account = UserAccount("operator", "Operador", UserRole.OPERATOR, first)
        auth = AuthService(b"0123456789abcdef0123456789abcdef", (account,))
        now = datetime(2026, 8, 24, tzinfo=UTC)
        token = auth.issue(account, now=now, lifetime=timedelta(minutes=5))
        self.assertEqual(account, auth.verify(token, now=now))
        self.assertIsNone(auth.verify(token, now=now + timedelta(minutes=5)))
        self.assertIsNone(auth.verify("not.a.valid.token", now=now))


class RealtimeTests(TestCase):
    def test_buffer_replay_and_slow_subscriber_drop_oldest(self) -> None:
        async def scenario() -> None:
            buffer = RealtimeBuffer(maximum_events=10)
            queue = buffer.subscribe()
            now = datetime(2026, 8, 24, tzinfo=UTC)
            for index in range(120):
                await buffer.publish("sample", "grow_a", now, {"index": index})
            self.assertEqual(100, queue.qsize())
            self.assertEqual(21, queue.get_nowait().event_id)
            self.assertEqual(tuple(range(111, 121)), tuple(event.event_id for event in buffer.after(110)))
            buffer.unsubscribe(queue)

        asyncio.run(scenario())

