"""
Entry point for the Gateway service.

Run the FastAPI application using uvicorn.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
