from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send
from typing import Callable, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class ResponseMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        if response.status_code >= 400:
            return response

        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return response

        # Read the response body safely
        resp_body = [section async for section in response.body_iterator]
        body_bytes = b"".join(resp_body)

        try:
            original_data = json.loads(body_bytes.decode("utf-8"))
        except Exception as e:
            logger.warning(f"Could not decode JSON response: {e}")
            return Response(content=body_bytes, status_code=response.status_code, headers=dict(response.headers))

        wrapped_response = {
            "success": True,
            "data": original_data,
            "meta": {
                "status": response.status_code,
                "endpoint": request.url.path
            }
        }

        return JSONResponse(content=wrapped_response, status_code=response.status_code)

