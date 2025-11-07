import sys

from .custom_excepthook import custom_excepthook


class CustomExceptionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            custom_excepthook(exc_type, exc_value, exc_traceback)

    def __getattr__(self, attr):
        return getattr(self.original, attr)
