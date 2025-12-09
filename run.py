"""
Run the FastAPI application.
"""

import uvicorn

from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=1201,
        reload=settings.DEBUG,
        log_level="info",
        timeout_keep_alive=300,  # Important for streaming
        limit_concurrency=None,  # No limit on concurrent connections
    )
