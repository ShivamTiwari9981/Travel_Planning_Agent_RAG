import os 
import asyncio

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq

load_dotenv()
llm = ChatGroq(
    model = "llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

tavily_api_key=os.getenv("TAVILY_API_KEY")
WEATHER_API_KEY=os.getenv("WEATHER_API_KEY")

client = MultiServerMCPClient({
    "tavily_server": {
        "transport": "streamable_http",
        "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={tavily_api_key}"
    },

    "aviationstack": {
        "transport": "stdio",
        "command": r"E:\Travel_Planning_Agent\aviationstack-mcp\.venv\Scripts\python.exe",
        "args": [
            "-m",
            "aviationstack_mcp",
            "mcp",
            "run"
        ],
        "env": {
            "AVIATION_STACK_API_KEY": os.getenv("AVIATIONSTACK_API_KEY")
        }
    },

    "weather_mcp_server": {
        "transport": "stdio",
        "command": r"E:\Travel_Planning_Agent\travel_plan\Scripts\python.exe",
        "args": [
            r"E:\Travel_Planning_Agent\custom_weather_mcp_server.py"
        ],
        "env": {
            "WEATHER_API_KEY": WEATHER_API_KEY
        }
    }
})

# async def main ():
#     tools = await client.get_tools()

#     print("\n Available MCP Tools : \n")

#     for tool in tools:
#         print(tool.name)


# async def main ():
#     tools = await client.get_tools()

#     search_tool = next( tool for tool in tools if tool.name == "tavily_search")

#     result = await search_tool.ainvoke({
#         "query" :"Best hotels in Delhi"
#     })

#     print(result)


# if __name__ == "__main__":
#     asyncio.run(main())


# only for Tavily api

# search_tool = None
# async def initialize_mcp():
#     global search_tool 
#     if search_tool is not None:
#         return
    
#     tools = await client.get_tools()

#     print("\nAvailable MCP Tools :")

#     for tool in tools:
#         print(tool)

#     search_tool = next (tool for tool in tools in tool.name == "tavily_search")



search_tool = None
aviation_tools = {}
async def initialize_mcp():
    global search_tool 
    global aviation_tools
    if search_tool is not None:
        return
    
    tools = await client.get_tools()

    print("\nAvailable MCP Tools :")

    for tool in tools:
        print(tool)

        search_tool = next(
        tool for tool in tools
        if tool.name == "tavily_search"
    )

    aviation_tools = {
        tool.name: tool
        for tool in tools
        if tool.name != "tavily_search"
    }

async def tavily_mcp_search(query:str):
    await initialize_mcp()

    result = await search_tool.ainvoke({
        "query" : query
    })
    return result


async def avition_mcp_call(tool_name:str, tool_args : dict = None):

    tools = await client.get_tools()

    tool = next(t for t in tools if t.name == tool_name)

    result = await tool.ainvoke(tool_args  or {})

    return result


async def get_airports():
    await initialize_mcp()

    tool = aviation_tools.get("list_airports")

    if not tool :
        return "Airport tool unavailable"
    
    result = await tool.ainvoke({})

    return result


async def get_airlines():
    await initialize_mcp()

    tool = aviation_tools.get("list_airlines")

    if not tool :
        return "Airline tool unavailable"
    
    result = await tool.ainvoke({})

    return result


weather_tool = None
forecast_tool = None


async def initialize_weather_tools():

    global weather_tool, forecast_tool

    if weather_tool is not None:
        return

    tools = await client.get_tools()

    weather_tool = next(
        t for t in tools
        if t.name == "get_current_weather"
    )

    forecast_tool = next(
        t for t in tools
        if t.name == "get_forecast"
    )


async def weather_mcp_search(city: str):

    await initialize_weather_tools()

    return await weather_tool.ainvoke(
        {
            "city": city
        }
    )


async def forecast_mcp_search(city: str):

    await initialize_weather_tools()

    return await forecast_tool.ainvoke(
        {
            "city": city
        }
    )


def extract_destination(query : str):
    prompt = f"""
    Extract only the destination ciry or country.

    Query :
    {query}


    return only destination name

    """

    response = llm.invoke(prompt)

    return response.content.strip()



   