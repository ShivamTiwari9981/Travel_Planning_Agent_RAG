import os 
import asyncio

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
WEATHER_API_KEY=os.getenv("WEATHER_API_KEY")


 
client = MultiServerMCPClient({
    "weather_mcp_server" : {
        "transport" : "stdio",
        "command" : r"E:\Travel_Planning_Agent\travel_plan\Scripts\python.exe",
        "args":[
            r"E:\Travel_Planning_Agent\custom_weather_mcp_server.py"
        ],
        "env":{
            "WEATHER_API_KEY" : WEATHER_API_KEY
        }
    }
})
async def main ():
    tools = await client.get_tools()

    print("\n Available MCP Tools : \n")

    for tool in tools:
        print(tool.name)

asyncio.run(main())