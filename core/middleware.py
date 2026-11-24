"""FastAPI middleware for request tracing."""
import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from core.request_context import request_id_ctx_var

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assigns a request_id (from header or generated) to each request.

    The id is stored in a contextvar so every log line emitted while
    handling the request — including in service/database/LLM modules —
    can be tagged with it via RequestIDLogFilter, and it is echoed back
    in the response header for client-side correlation.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        token = request_id_ctx_var.set(request_id)
        start = time.time()
        try:
            logger.info(
                "request_started",
                extra={"method": request.method, "path": request.url.path},
            )
            response = await call_next(request)
            duration_ms = round((time.time() - start) * 1000, 2)
            logger.info(
                "request_completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            request_id_ctx_var.reset(token)
