import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from MathematicaEvaluator import MathematicaEvaluator
import os
import asyncio


AUTH_TOKEN = "https://forum.koishi.xyz/t/topic/6009/2"
MAX_TIMEOUT = 60

app = FastAPI()
evaluator = MathematicaEvaluator()
lock = asyncio.Lock()


@app.post("/evaluate/")
async def evaluate_expression(request: Request):
    async with lock:
        #TODO Check if the expression is valid

        if AUTH_TOKEN != request.headers.get("Authorization"):
            raise HTTPException(
                status_code=403, detail="THIS IS NOT A PUBLIC INTERFACE."
            )

        res = json.loads((await request.body()).decode("utf-8"))
        code, timeout, step = res["code"], res["timeout"], res["step"]

        if timeout < 0 or timeout > MAX_TIMEOUT:
            raise HTTPException(status_code=400, detail="Invalid timeout.")

        gif_path = evaluator.evaluate(code, timeout, step)
        if gif_path and os.path.exists(gif_path):
            return FileResponse(
                gif_path, media_type="image/gif", filename=os.path.basename(gif_path)
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to evaluate.")
