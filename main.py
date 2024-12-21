import websockets
import multiprocessing
import asyncio
import time
import datetime
import base64
import json
import os

from dotenv import load_dotenv
from utils import extract, saveLog

# Load environment variables from .env file
load_dotenv()
APP_ID = os.getenv("APP_ID")
API_TOKEN = os.getenv("API_TOKEN")


async def connect():
    try:
        ws = await websockets.connect(f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}")
        await ws.send(json.dumps({"authorize": API_TOKEN}))
        res = json.loads(await ws.recv())
        if "error" in res: raise Exception(res['error']['message'])
        return ws
    except Exception as e:
        raise Exception(f"Conn err: {e}")

async def exec_cmds(ws, cmds, ret):
    res = []
    for cmd in cmds:
        try:
            side = cmd["side"].upper()
            if side == "BALANCE":
                await ws.send(json.dumps({"balance": 1}))
                r = json.loads(await ws.recv())
                res.append(f"Bal: {r.get('balance', {}).get('balance', 'N/A')}")
            elif side == "PORTFOLIO":
                await ws.send(json.dumps({"portfolio": 1}))
                r = json.loads(await ws.recv())
                res.append(f"Port: {r.get('portfolio', {}).get('contracts', 'N/A')}")
            elif side == "SYMBOLS":
                await ws.send(json.dumps({"active_symbols": "brief"}))
                r = json.loads(await ws.recv())
                syms = [s["symbol"] for s in r.get("active_symbols", [])]
                res.append(f"Syms: {', '.join(syms)}")
            elif side in ["BUY", "SELL"]:
                if not cmd.get("symbol") or not cmd.get("stake"):
                    res.append("Err: Miss 'sym' or 'stk'")
                    continue
                tt = "CALL" if side == "BUY" else "PUT"
                ct = cmd.get("type", "binary").upper()
                tr = {
                    "buy": 1,
                    "price": cmd["stake"],
                    "parameters": {
                        "symbol": cmd["symbol"],
                        "basis": "stake",
                        "duration": cmd.get("duration", 1),
                        "duration_unit": cmd.get("duration_unit", "m"),
                        "contract_type": tt,
                        "currency": "USD",
                        "amount": cmd["stake"]
                    },
                }
                if ct == "DIGITAL": tr["parameters"]["barrier"] = cmd.get("barrier", 0.1)
                if "sl" in cmd: tr["parameters"]["stop_loss"] = cmd["sl"]
                if "tp" in cmd: tr["parameters"]["take_profit"] = cmd["tp"]
                await ws.send(json.dumps(tr))
                r = json.loads(await ws.recv())
                res.append(f"Trade executed✅: {r.get('buy', 'Unknown')}")
            elif side == "CANCEL":
                cid = cmd.get("contract_id")
                if not cid:
                    res.append("Err: Miss 'cid'")
                    continue
                await ws.send(json.dumps({"cancel": 1, "contract_id": cid}))
                r = json.loads(await ws.recv())
                res.append(f"Cancel: {r.get('cancel', 'Unknown')}")
            elif side == "CLOSE":
                if not cmd.get("symbol"):
                    res.append("Err: Miss 'sym'")
                    continue
                await ws.send(json.dumps({"sell": cmd.get("symbol"), "price": cmd.get("stake", 0)}))
                r = json.loads(await ws.recv())
                res.append(f"Close: {r.get('sell', 'Unknown')}")
        except Exception as e:
            res.append(f"Err: {e}")
            break
    ret["result"] = "\n".join(res)

def exec(data, ret):
    async def run_exec():
        try:
            ws = await connect()
            await exec_cmds(ws, data["executes"], ret)
            await ws.close()
        except Exception as e:
            ret["result"] = f"Exec failed: {e}"
    asyncio.run(run_exec())

def deriv(req):
    start = time.time()
    attr = req["message"]["attributes"]
    body = base64.b64decode(req["message"]["data"]).decode()
    msg = attr
    msg["created"] = datetime.datetime.now(tz=datetime.timezone.utc)
    msg["message"] = body

    def finish(st, res):
        msg["result"] = res
        saveLog(msg)
        return res, st

    execs = []
    cmds = body.upper().split("\n")
    for cmd in cmds:
        p, m = extract(["quantity", "expiry", "symbol", "stake", "type", "barrier", "sl", "tp"], cmd)
        if m.strip(): p["side"] = m.split()[0]
        else: continue
        if "side" in p and p["side"]:
            execs.append(p)

    mgr = multiprocessing.Manager()
    ret = mgr.dict()
    data = {"attributes": attr, "executes": execs}
    executor = multiprocessing.Process(target=exec, args=(data, ret))
    executor.start()
    executor.join()

    return finish(200, list(ret.values())[0])
