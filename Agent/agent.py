import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

# Load .env from the project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# FastAPI lifespanイベントでエージェント初期化
from contextlib import asynccontextmanager

agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    server_path = str(Path(__file__).parent.parent / "MCPServer" / "server.py")
    client = MultiServerMCPClient(
        {
            "flightaware": {
                "transport": "stdio",
                "command": "python",
                "args": [server_path],
            }
        }
    )
    mcp_tools = await client.get_tools()
    system_message = """あなたは航空情報の専門家です。
提供されたツールを使って正確なフライト情報を答えてください。
日本語で、聞かれた場合、ツールに渡すパラメータの時刻は標準時 (UTC) に変換して渡してください。
年月日の指定がない場合、今日の日付を使用してください。
未来の時刻であれば、スケジュールを取得するツール。
過去の時刻が含まれていれば、実績を取得するツールを使用してください。

ただし、回答の際は以下の点に注意してください：
- 時刻は日本時間 (JST) で答えてください。
- フライト情報はフライトごとに改行して見やすくしてください。
"""
    agent = create_agent(llm, mcp_tools, system_prompt=system_message)
    yield


app = FastAPI(lifespan=lifespan)
# CORSミドルウェア追加（全許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html><head><title>FlightAware MCP</title></head>
    <body><h1>Working!</h1>
    <a href="/view">/viewへ移動</a></body></html>
    """


# staticファイルの配置先(frontend/public)を/viewで配信
static_dir = Path(__file__).parent / "public"
app.mount("/view", StaticFiles(directory=static_dir, html=True), name="static")


@app.post("/api/agent")
async def ask_agent(request: Request):
    data = await request.json()
    user_input = data.get("input", "")
    if not user_input:
        return JSONResponse({"error": "input is required"}, status_code=400)
    global agent
    if agent is None:
        return JSONResponse({"error": "agent not initialized"}, status_code=500)
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_input}]}
    )
    messages = response.get("messages", [])
    if messages:
        last_message = messages[-1]
        return {"output": last_message.content}
    else:
        return {"output": str(response)}


if __name__ == "__main__":
    uvicorn.run("Agent.agent:app", host="0.0.0.0", port=8000, reload=True)
