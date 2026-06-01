import unittest

from apps.api.main import create_app


class SmokeTests(unittest.TestCase):
    def test_app_factory(self) -> None:
        app = create_app()
        self.assertEqual(app.title, "多场景英语教学音频播放与管控软件 API")


if __name__ == "__main__":
    unittest.main()

