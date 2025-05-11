import asyncio
import secrets

async def keeprunning():
    while True:
        await asyncio.sleep(1)

id = secrets.token_urlsafe(3)
def log(*args):
    print(f"{id}:", *args)