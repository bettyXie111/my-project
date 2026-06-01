# -*- coding: utf-8 -*-
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SmokeTest(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = [
            ROOT / "apps" / "api" / "main.py",
            ROOT / "apps" / "web" / "index.html",
            ROOT / "apps" / "web" / "app.css",
            ROOT / "apps" / "web" / "app.js",
            ROOT / "screenshot_plan.json",
        ]
        missing = [str(p) for p in required if not p.exists()]
        self.assertFalse(missing, f"missing required files: {missing}")

    def test_index_has_login_form_contract(self) -> None:
        html = (ROOT / "apps" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="app"', html)
        js = (ROOT / "apps" / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="login-form"', js)
        self.assertIn('name="username"', js)
        self.assertIn('name="password"', js)

    def test_api_domain_modules_exist(self) -> None:
        required = [
            ROOT / "apps" / "api" / "domain" / "store.py",
            ROOT / "apps" / "api" / "domain" / "router.py",
            ROOT / "apps" / "api" / "domain" / "validators.py",
            ROOT / "apps" / "api" / "domain" / "csv_tools.py",
        ]
        missing = [str(p) for p in required if not p.exists()]
        self.assertFalse(missing, f"missing domain modules: {missing}")


if __name__ == "__main__":
    unittest.main()
