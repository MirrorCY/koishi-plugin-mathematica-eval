import json
from fastapi import FastAPI, HTTPException, Request
from MathematicaEvaluator import MathematicaEvaluator
import os
import asyncio
import base64


AUTH_TOKEN = "https://forum.koishi.xyz/t/topic/6009/2"
MAX_TIMEOUT = 60

app = FastAPI()
evaluator = MathematicaEvaluator()
lock = asyncio.Lock()


def pngs2base64_dataURLs(pngs: list[str]) -> list[str]:
    dataURLs = []
    for png in pngs:
        with open(png, "rb") as f:
            dataURLs.append(
                f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
            )
    return dataURLs


@app.post("/evaluate/")
async def evaluate_expression(request: Request):
    async with lock:
        # TODO Check if the expression is valid

        if AUTH_TOKEN != request.headers.get("Authorization"):
            raise HTTPException(
                status_code=403, detail="THIS IS NOT A PUBLIC INTERFACE."
            )

        res = json.loads((await request.body()).decode("utf-8"))
        code, timeout, step = res["code"], res["timeout"], res["step"]

        if timeout < 0 or timeout > MAX_TIMEOUT:
            raise HTTPException(status_code=400, detail="Invalid timeout.")
        try:
            pngs_path = evaluator.evaluate(code, timeout, step)
            pngs = pngs2base64_dataURLs(pngs_path)
            # jsonify
            return {"pngs": pngs}

        except:
            os.system("taskkill /f /im Wolfram*")
            os.system("taskkill /f /im Mathematica*")
            exit(500)
