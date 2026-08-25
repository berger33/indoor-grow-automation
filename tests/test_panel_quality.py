from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]


class PanelQualityTests(TestCase):
    def test_keyboard_navigation_and_reduced_motion_are_explicit(self) -> None:
        app = (ROOT / "web/src/main.tsx").read_text(encoding="utf-8")
        styles = (ROOT / "web/src/styles.css").read_text(encoding="utf-8")
        self.assertIn("Pular para o conteúdo", app)
        self.assertIn('aria-current=', app)
        self.assertIn(":focus-visible", styles)
        self.assertIn("prefers-reduced-motion", styles)

    def test_offline_cache_never_caches_api_responses(self) -> None:
        worker = (ROOT / "web/public/service-worker.js").read_text(encoding="utf-8")
        self.assertIn('url.pathname.startsWith("/api/")', worker)
        self.assertIn('caches.match("/index.html")', worker)

    def test_help_explains_co2_and_unconfirmed_commands(self) -> None:
        help_page = (ROOT / "web/src/HelpPage.tsx").read_text(encoding="utf-8")
        self.assertIn("somente monitorado", help_page)
        self.assertIn("queued indica apenas pedido", help_page)
