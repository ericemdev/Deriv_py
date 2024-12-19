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
        websocket = await websockets.connect(f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}")
        await websocket.send(json.dumps({"authorize": API_TOKEN}))
        response = json.loads(await websocket.recv())
        if "error" in response:
            raise Exception(f"Authentication failed: {response['error']['message']}")
        return websocket
    except Exception as e:
        raise Exception(f"Connection error: {e}")


async def execute_commands(websocket, commands, return_dict):
    print("Executing commands", commands)
    results = []

    for command in commands:
        try:
            side = command["side"].upper()
            print(f"Executing {side} command for symbol: {command.get('symbol', 'N/A')}")

            if side == "BALANCE":
                await websocket.send(json.dumps({"balance": 1}))
                response = json.loads(await websocket.recv())
                print("Balance response:", response)
                balance = response.get("balance", {}).get("balance", "N/A")
                results.append(f"Balance: {balance}")

            elif side == "SYMBOLS":
                option_type = command.get("type", "BINARY")
                await websocket.send(json.dumps({"active_symbols": "brief"}))
                response = json.loads(await websocket.recv())
                print("Symbols response:", response)
                symbols = [s["symbol"] for s in response.get("active_symbols", [])]
                results.append(f"Available Symbols: {', '.join(symbols)}")


            elif side in ["BUY", "SELL"]:
                if not command.get("symbol") or not command.get("stake"):
                    results.append("Error: Missing 'symbol' or 'stake' for trade.")
                    continue

                trade_type = "CALL" if side == "BUY" else "PUT"
                trade_request = {
                    "buy": 1,
                    "price": command["stake"],
                    "parameters": {
                        "symbol": command["symbol"],
                        "basis": "stake",
                        "duration": command.get("expiry", 1),
                        "duration_unit": command.get("duration_unit", "d"),
                        "contract_type": trade_type,
                        "currency": "USD",
                        "amount": command["stake"]
                    },
                }

                if "sl" in command:
                    trade_request["parameters"]["stop_loss"] = command["sl"]
                if "tp" in command:
                    trade_request["parameters"]["take_profit"] = command["tp"]

                print(f"Sending trade request: {trade_request}")
                await websocket.send(json.dumps(trade_request))
                response = json.loads(await websocket.recv())
                print("Trade response:", response)

                if "error" in response:
                    raise Exception(f"Trade error: {response['error']['message']}")
                else:
                    results.append(f"Trade Executed: {response.get('buy', 'Unknown response')}")

            elif side == "CLOSE":
                if not command.get("symbol"):
                    results.append("Error: Missing 'symbol' for close trade.")
                    continue

                close_request = {
                    "sell": command.get("symbol"),
                    "price": command.get("stake", 0),
                }

                print(f"Sending close request: {close_request}")
                await websocket.send(json.dumps(close_request))
                response = json.loads(await websocket.recv())
                print("Close response:", response)

                if "error" in response:
                    raise Exception(f"Close error: {response['error']['message']}")
                else:
                    results.append(f"Trade Closed: {response.get('sell', 'Unknown response')}")

        except Exception as e:
            results.append(f"Error: {e}")
            break

    return_dict["result"] = "\n".join(results)


def execute(data, return_dict):
    print("Executing", data)
    async def run_execution():
        try:
            websocket = await connect()
            await execute_commands(websocket, data["executes"], return_dict)
            await websocket.close()
        except Exception as e:
            return_dict["result"] = f"Execution failed: {e}"

    asyncio.run(run_execution())

def deriv(req):
    started = time.time()

    attributes = req["message"]["attributes"]
    body = base64.b64decode(req["message"]["data"]).decode()

    msg = attributes
    msg["created"] = datetime.datetime.now(tz=datetime.timezone.utc)
    msg["message"] = body

    def finish(status, results):
        msg["result"] = results
        saveLog(msg)
        return results, status

    executes = []
    commands = body.upper().split("\n")
    for command in commands:
        params, message = extract(["quantity", "expiry", "symbol", "stake", "sl" "tp"], command)

        if message.strip():
            params["side"] = message.split()[0]
        else:
            continue

        if "side" in params and params["side"]:
            executes.append(params)

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    data = {"attributes": attributes, "executes": executes}
    executor = multiprocessing.Process(target=execute, args=(data, return_dict))
    executor.start()
    executor.join()

    return finish(200, list(return_dict.values())[0])