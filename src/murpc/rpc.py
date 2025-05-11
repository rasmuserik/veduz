import secrets
import asyncio
import cbor2
import inspect
from murpc.websocket import WsConnection
from murpc.util import keeprunning

class Message:
    def __init__(self, peer, fn, rid, payload):
        self.peer = peer
        self.fn = fn
        self.rid = rid
        self.payload = payload
    def pack(self):
        return cbor2.dumps([self.peer, self.fn, self.rid, self.payload])
    def __str__(self):
        return f"Message(peer={self.peer}, fn={self.fn}, rid={self.rid}, payload={self.payload})"
    @staticmethod
    def unpack(data):
        return Message(*cbor2.loads(data))

id = secrets.token_urlsafe(3)
def log(*args):
    print(f"{id}:", *args)

conn = None


pending = {}
exposed = {}

class RemoteError(Exception):
    def __init__(self, msg):
        self.msg = msg

def _send(peer, type, rid, payload):
    asyncio.create_task(conn.send(Message(peer, type, rid, payload).pack()))

async def _onmessage(msg):
    msg = Message.unpack(msg)
    if msg.fn == "return":
        return pending[msg.rid].set_result(msg.payload)
    if msg.fn == "throw":
        raise pending[msg.rid].set_exception(RemoteError(msg.payload))
    if msg.fn in exposed:
        (fn, allow) = exposed[msg.fn]
        try:
            result = fn(*msg.payload)
            if inspect.isasyncgen(result):
                async for item in result:
                    _send(msg.peer, "yield", msg.rid, item)
                return
            elif asyncio.iscoroutine(result):
                return _send(msg.peer, "return", msg.rid, await result)
            else:
                return _send(msg.peer, "return", msg.rid, result)
        except Exception as e:
            return _send(msg.peer, "throw", msg.rid, str(e))
        
    raise Exception("unknown fn: " + msg.fn)

async def call(peer, fn, *args):
    rid = secrets.token_urlsafe(12)
    pending[rid] = asyncio.Future()
    asyncio.create_task(conn.send(Message(peer, fn, rid, args).pack()))
    try:
        result = await asyncio.wait_for(pending[rid], 30)
        pending.pop(rid)
        return result
    except Exception as e:
        pending.pop(rid)
        raise e

def expose(name, *, allow):
    if isinstance(allow, str):
        allow = [allow]
    def decorator(fn):
        exposed[name] = (fn, allow)
        return fn
    return decorator


async def start():
    global conn
    async def onconnect():
        log('connected')
    conn = WsConnection("wss://ws.veduz.com/ws", onconnect=onconnect, onmessage=_onmessage)

async def main():
    await start()

    @expose("hello", allow="any")
    async def hello(*args):
        log("hello from", *args)
        return "hello"

    @expose("hello2", allow="any")
    async def hello2(*args):
        for i in range(10):
            await asyncio.sleep(0.1)
            yield i

    veduz_test = await call("rpc", 'addRole', 'veduz-client-test')
    result = await call(veduz_test, 'hello', "python_" + id)
    log("got result", result)
    result = await call(veduz_test, 'hello2', "python_" + id)
    async for item in result:
        log("got item", item)
    #await conn.send(Message("rpc", 'addRole', '123', 'veduz-client-test'))
    await keeprunning()

if __name__ == "__main__":
    asyncio.run(main())
