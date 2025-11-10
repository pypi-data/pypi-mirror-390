"""Simple session context example for Brizz Python SDK."""

import asyncio
import uuid

from brizz import Brizz, asession_context, awith_session_id, session_context, with_session_id

# Initialize SDK
Brizz.initialize(
    base_url="http://localhost:4318",
    disable_batch=True,
    app_name="session-example",
)


async def endpoint_async(user_id: str) -> str:
    """Async operation with session context."""
    Brizz.emit_event("operation.started", attributes={"user_id": user_id})
    return f"Processed user {user_id}"


def endpoint_sync(task: str) -> str:
    """Sync operation with session context."""
    Brizz.emit_event("task.completed", attributes={"task": task})
    return f"Completed {task}"


async def endpoint_async_decorator(task: str) -> str:
    """Sync operation with session context."""
    session_id = uuid.uuid4().hex

    @asession_context(session_id)
    async def inner_async_decorator(task: str) -> str:
        """Async operation with session context."""
        Brizz.emit_event("task.completed", attributes={"task": task})
        return f"Completed {task}"

    return await inner_async_decorator(task)


def endpoint_sync_decorator(task: str) -> str:
    """Sync operation with session context."""
    session_id = uuid.uuid4().hex

    @session_context(session_id)
    def inner_sync_decorator(task: str) -> str:
        """Sync operation with session context."""
        Brizz.emit_event("task.completed", attributes={"task": task})
        return f"Completed {task}"

    return inner_sync_decorator(task)


async def main() -> None:
    """Main function to demonstrate session context usage."""
    session_id = uuid.uuid4().hex
    result1 = await awith_session_id(session_id, endpoint_async, "doo")
    result2 = with_session_id(session_id, endpoint_sync, "goo")
    result3 = await endpoint_async_decorator("foo")
    result4 = endpoint_sync_decorator("bar")

    print(f"Async: {result1}")
    print(f"Sync: {result2}")
    print(f"Async Decorator: {result3}")
    print(f"Sync Decorator: {result4}")


if __name__ == "__main__":
    asyncio.run(main())
