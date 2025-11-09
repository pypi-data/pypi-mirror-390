from __future__ import annotations
import json
import os
from typing import Optional
import typer
import requests


app = typer.Typer(help="urlscanner CLI — single-route header audit")
DEFAULT_URL = "http://127.0.0.1:8000"


def _base(url: Optional[str]) -> str:
    return (url or os.getenv("urlscanner_URL") or DEFAULT_URL).rstrip("/")


@app.command()
def get(url: Optional[str] = typer.Option(None, help="Base API URL")):
    base = _base(url)
    r = requests.get(f"{base}/audit", timeout=10)
    r.raise_for_status()
    typer.echo(json.dumps(r.json(), indent=2))


@app.command()
def post(target: str = typer.Argument(..., help="URL to audit"), url: Optional[str] = typer.Option(None, help="Base API URL")):
    base = _base(url)
    payload = {"url": target}
    r = requests.post(f"{base}/audit", json=payload, timeout=15)
    if r.status_code >= 400:
        typer.echo(r.text)
        raise typer.Exit(code=1)
    typer.echo(json.dumps(r.json(), indent=2))