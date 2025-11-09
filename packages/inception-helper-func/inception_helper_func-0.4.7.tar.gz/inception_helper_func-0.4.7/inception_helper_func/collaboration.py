import os
import time
import aiohttp
from fastapi import Request
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    url: str = ""

    env_file: str = os.path.join(os.path.dirname(__file__), "collaboration.env")
    load_dotenv(dotenv_path=env_file)
    model_config = SettingsConfigDict(env_file=env_file)


def init_collaboration_service_connection(url: str):

    env_file = os.path.join(os.path.dirname(__file__), "collaboration.env")
    with open(env_file, "w") as f:
        f.write(f'url="{url}"\n')

    time.sleep(3)
    os.chmod(env_file, 0o777)


def get_collaboration_service_setting():
    return Settings()



async def create_chat(payload: dict, request: Request):
    """
    Helper function to create a chat with the collaboration service.
    """
    try:
        c_setting = get_collaboration_service_setting()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{c_setting.url}/api/v1/chats",
                headers={
                    "Authorization": request.headers.get("Authorization"),
                    "Content-Type": "application/json",
                },
                json=payload,
            ) as response:
                if response.status in (200, 201):
                    return await response.json()
                else:
                    error_detail = await response.json()
                    raise Exception(
                        f"Request failed with status {response.status}: {error_detail}"
                    )
    except Exception as e:
        print(f"[ERROR] Failed to create chat: {e}")
        raise Exception(
            {
                "status_code": 500,
                "type": "error",
                "content": str(e),
            }
        )

async def update_chat(payload: dict, request: Request):
    """
    Helper function to update a chat with the collaboration service.
    """
    try:
        c_setting = get_collaboration_service_setting()
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{c_setting.url}/api/v1/chats/{payload['id']}",
                headers={
                    "Authorization": request.headers.get("Authorization"),
                    "Content-Type": "application/json",
                },
                json=payload,
            ) as response:
                if response.status in (200, 201):
                    return await response.json()
                else:
                    error_detail = await response.json()
                    raise Exception(
                        f"Request failed with status {response.status}: {error_detail}"
                    )
    except Exception as e:
        print(f"[ERROR] Failed to update chat: {e}")
        raise Exception(
            {
                "status_code": 500,
                "type": "error",
                "content": str(e),
            }
        )