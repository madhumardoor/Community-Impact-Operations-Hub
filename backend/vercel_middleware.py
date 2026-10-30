"""ASGI middleware to remove the public /api prefix before FastAPI routing."""
class StripApiPrefix:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path == "/api":
                scope = dict(scope)
                scope["path"] = "/"
                scope["raw_path"] = b"/"
            elif path.startswith("/api/"):
                scope = dict(scope)
                scope["path"] = path[4:]
                scope["raw_path"] = scope["path"].encode("utf-8")
        await self.app(scope, receive, send)
