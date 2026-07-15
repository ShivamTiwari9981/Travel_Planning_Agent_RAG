import os 
import asyncio

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
aviation_stack_api_key=os.getenv("AVIATIONSTACK_API_KEY")

client = MultiServerMCPClient({
    "aviationstack" : {
        "transport" : "stdio",
        "command" : r"E:\Travel_Planning_Agent\aviationstack-mcp\.venv\Scripts\python.exe",
        "args":[
            "-m",
            "aviationstack_mcp",
            "mcp",
            "run"
        ],
        "env":{
            "AVIATION_STACK_API_KEY" : aviation_stack_api_key
        }
    }
})
async def main ():
    tools = await client.get_tools()

    print("\n Available MCP Tools : \n")

    for tool in tools:
        print(tool.name)

asyncio.run(main())