class ResponseCache:
    def __init__(self):
        self._cache = {}

    def store(self, url: str, response) -> None:
        """Store response headers for a URL"""
        headers = {}
        if "ETag" in response.headers:
            headers["ETag"] = response.headers["ETag"]
        if "Last-Modified" in response.headers:
            headers["Last-Modified"] = response.headers["Last-Modified"]

        if headers:
            self._cache[url] = {
                "headers": headers,
                "data": response.json() if response.content else None,
            }

    def get_cached_headers(self, url: str) -> dict:
        """Get cached headers for conditional request"""
        if url not in self._cache:
            return {}

        headers = {}
        cached = self._cache[url]["headers"]

        if "ETag" in cached:
            headers["If-None-Match"] = cached["ETag"]
        if "Last-Modified" in cached:
            headers["If-Modified-Since"] = cached["Last-Modified"]

        return headers

    def get_cached_response(self, url: str):
        """Get cached response data"""
        return self._cache.get(url, {}).get("data")
