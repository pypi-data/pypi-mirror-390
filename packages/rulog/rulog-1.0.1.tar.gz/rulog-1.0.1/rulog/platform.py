class Parts_Platform:
    _platforms = {
        "android": {
            "app_name": "Main",
            "app_version": "3.5.7",
            "lang_code": "fa",
            "package": "app.rbmain.a",
            "temp_code": "31",
            "platform": "Android",
        },
        "web": {
            "app_name": "Main",
            "app_version": "4.4.6",
            "lang_code": "fa",
            "package": "web.rubika.ir",
            "platform": "Web",
        },
        "pwa": {
            "app_name": "Main",
            "app_version": "2.1.4",
            "lang_code": "fa",
            "package": "m.rubika.ir",
            "platform": "PWA",
        },
    }

    def __init__(self, platform: str):
        platform = platform.lower()
        self.platform = self._platforms.get(platform, self._platforms["pwa"]).copy()