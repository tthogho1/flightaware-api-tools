import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

# Load .env from the project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


async def main():
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # Get the absolute path to the MCP server script
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

    system_message = "あなたは航空情報の専門家です。提供されたツールを使って正確なフライト情報を答えてください。"

    agent = create_react_agent(llm, mcp_tools, prompt=system_message)

    user_input = "成田空港(RJAA)から出発する飛行機の目的地と出発時刻を教えてください。"

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_input}]}
    )

    print("\n--- AIからの回答 ---")
    # Get the last message from the response
    messages = response.get("messages", [])
    if messages:
        last_message = messages[-1]
        print(last_message.content)
    else:
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
