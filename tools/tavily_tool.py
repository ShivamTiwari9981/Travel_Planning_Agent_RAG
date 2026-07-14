import os
from dotenv import load_dotenv
import requests

from tavily import TavilyClient

load_dotenv()

client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

def tavily_search(query):
    response = client.search(
        query=query,
        max_results=5
    )

    results=[]

    for i, r in enumerate(response["results"],1):
        title = r.get("title","N/A")
        url = r.get("url","N/A")
        snippet = r.get("content","").strip()

        if len(snippet)>300:
            snippet = snippet[:300].rsplit(" ",1)[0] + "..."
        
        results.append(f"{i}. **{title} **\n  {url}\n {snippet}")

    d = "\n\n".join(results)
    print("Hotels details available ", d)
    return "\n\n".join(results)
