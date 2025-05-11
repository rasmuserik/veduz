import asyncio
from websockets.asyncio import client
from websockets.exceptions import ConnectionClosed
import cbor2
#import logging
#logging.basicConfig(level=logging.DEBUG)


class WsConnection:
    def __init__(self, url, *, onmessage, onconnect):
        self.url = url
        self.onmessage = onmessage
        self.onconnect = onconnect
        self.ws = None
        asyncio.create_task(self._loop())

    async def _loop(self):
        async for ws in client.connect(self.url):
            self.ws = ws
            onconnect = self.onconnect
            try:
                await onconnect()
                while True:
                    msg = await ws.recv()
                    try:
                        onmessage = self.onmessage
                        await onmessage(msg)
                    except Exception as e:
                        print("Error handling message:", e)
            except ConnectionClosed as e:
                self.ws = None
                continue
    async def send(self, msg):
        while not self.ws:
            await asyncio.sleep(0.1)
        await self.ws.send(msg)



async def main():
    async def onmessage(msg):
        print("incomming message:", cbor2.loads(msg))
    ws = WsConnection("wss://ws.veduz.com/ws", onmessage=onmessage)
    await ws.send(cbor2.dumps(["rpc", "addRole", "123", "veduz-client-test"]))
    while True: await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
