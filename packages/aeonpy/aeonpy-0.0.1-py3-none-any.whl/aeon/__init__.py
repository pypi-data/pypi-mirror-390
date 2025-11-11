import httpx
from typing import List, Optional, Callable, Any, TypedDict
from pydantic import SecretStr
import asyncio
import time
import functools


class Message(TypedDict):
    role: str
    content: str
    timestamp: float


class Aeon:
    api_key: SecretStr
    project_id: int
    agent: Optional[str] = None
    endpoint: Optional[str] = "https://withaeon.com"
    initialized: bool = False
    heartbeat_started = False

    @staticmethod
    def init(
        api_key: str,
        project_id: int,
        endpoint: Optional[str] = "https://withaeon.com",
    ):
        if Aeon.initialized:
            raise RuntimeError("Aeon has already been initialized")

        Aeon.initialized = True
        Aeon.api_key = SecretStr(api_key)
        Aeon.endpoint = endpoint
        Aeon.project_id = project_id

        print("Aeon initialized with endpoint: ", Aeon.endpoint)

    @staticmethod
    def track_agent(name: str):
        Aeon.agent = name

        def decorator(func: Callable[..., Any]):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):

                asyncio.create_task(Aeon._heartbeat())

                start = time.time()

                try:
                    result = func(*args, **kwargs)
                    if asyncio.iscoroutine(result):
                        result = await result

                    end = time.time()
                    latency = round((end - start) * 1000)

                    # Extract info
                    model_name = result.get("model") or "unknown"
                    costs = result.get("costs") or 0

                    # Track
                    await Aeon._track_execution(
                        success=True,
                        latency_ms=latency,
                        cost=costs,
                        model=model_name,
                    )

                    return result

                except Exception as e:

                    print("failed")
                    end = time.time()
                    latency = round((end - start) * 1000)

                    await Aeon._track_execution(
                        success=False,
                        latency_ms=latency,
                        cost=0,
                        error_type=type(e).__name__,
                    )

                    raise

            return wrapper

        return decorator

    @staticmethod
    async def track_conversation(
        conversation_id: str, model: str, messages: List[Message]
    ):
        if not Aeon.api_key or not Aeon.project_id:
            raise ValueError("Missing credentials")


        if len(messages) >= 40:
            raise RuntimeError("Reached messages limit")

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{Aeon.endpoint}/api/v1/projects/{Aeon.project_id}/agents/conversations",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"{Aeon.api_key.get_secret_value()}",
                    },
                    json={
                        "conversation_id": conversation_id,
                        "model": model,
                        "messages": messages,
                    },
                )
        except Exception as e:
            print(f"Aeon error: {e}")

    @staticmethod
    async def _track_execution(
        success: bool,
        latency_ms: int,
        cost: float,
        model: str = "unknown",
        error_type: Optional[str] = None,
    ):
        """Send metric to API"""

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{Aeon.endpoint}/api/v1/projects/{Aeon.project_id}/agents/sessions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"{Aeon.api_key.get_secret_value()}",
                    },
                    json={
                        "agent_name": Aeon.agent,
                        "success": success,
                        "latency": latency_ms,
                        "costs": cost,
                        "model": model,
                        "error_type": error_type,
                    },
                    timeout=10.0,
                )
        except Exception as e:
            print(f"Aeon error: {e}")

    @staticmethod
    async def _heartbeat():
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{Aeon.endpoint}/api/v1/projects/{Aeon.project_id}/agents/heartbeat",
                        headers={
                            "Authorization": f"{Aeon.api_key.get_secret_value()}",
                        },
                        json={"agent_name": Aeon.agent, "status": "running"},
                    )
            except Exception as e:
                print(f"Heartbeat error: {e}")
            await asyncio.sleep(15)  # every 15 seconds
