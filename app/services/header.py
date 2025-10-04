import random

class HeaderService:
    def __init__(self): 
        self.base_url = "https://editorial.rottentomatoes.com/guide/best-movies-of-all-time/"
        
        # Lists for rotation
        self._user_agents = [
            # Windows Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36",
            # Mac Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
            # iPhone
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            # Android Chrome
            "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Mobile Safari/537.36",
            # Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.6; rv:118.0) Gecko/20100101 Firefox/118.0",
        ]

        self._accept_languages = [
            "en-US,en;q=0.9",
            "en-GB,en-US;q=0.9,en;q=0.8",
            "en-US;q=0.9,th;q=0.8",
            "en-US,en;q=0.5,fr;q=0.3",
            "en;q=0.8,es;q=0.6,en-US;q=0.4",
        ]

        # Some possible referers
        self._referers = [
            "https://www.google.com/",
            "https://www.bing.com/",
            "https://www.reddit.com/",
            "https://twitter.com/",
            "https://www.facebook.com/",
            "https://www.youtube.com/",
            "https://www.rottentomatoes.com/",
            self.base_url,
        ]

        # Optional: extra Accept header variations
        self._accepts = [
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "text/html,application/xml;q=0.9,*/*;q=0.8",
            "text/html,application/xhtml+xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        ]
        
    def build_headers(self) -> dict:
        return {
            "User-Agent": random.choice(self._user_agents),
            "Accept-Language": random.choice(self._accept_languages),
            "Accept": random.choice(self._accepts),
            "Referer": random.choice(self._referers),
        }
