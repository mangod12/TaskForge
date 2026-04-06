from __future__ import annotations

import asyncio

startup_complete = asyncio.Event()
startup_error: str | None = None
