from __future__ import annotations
from typing import Deque
from collections import deque
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from .models import AuditRequest, AuditResult, AuditList
from .checker import audit_url


app = FastAPI(title="Security Header Audit", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[], allow_credentials=False, allow_methods=["GET"], allow_headers=[],
)


_HISTORY: Deque[AuditResult] = deque(maxlen=10)


@app.get("/audit", response_model=AuditList)
def get_audit_history() -> AuditList:
    return AuditList(results=list(_HISTORY)[::-1])


@app.post("/audit", response_model=AuditList, status_code=status.HTTP_201_CREATED)
def post_audit(req: AuditRequest) -> AuditList:
    try:
        # Convert HttpUrl to string before passing to audit_url
        data = audit_url(str(req.url))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


    result = AuditResult(**data)
    _HISTORY.append(result)
    return AuditList(results=[result])


# Entrypoint for console script


def main() -> None:
    import uvicorn
    uvicorn.run("urlscanner.api:app", host="127.0.0.1", port=8000, reload=False)