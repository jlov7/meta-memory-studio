"""Shared API error envelope helpers."""

from fastapi import HTTPException


def error_detail(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


def http_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail=error_detail(code, message))
