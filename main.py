import operator
import os 
from typing import TypedDict,Annotated

import psycopg
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    AnyMessage,
    SystemMessage,
    AIMessage,
    HumanMessage
)

from langchain_groq import ChatGroq

from tools.tavily_tool import tavily_search
from tools.flight_tool import flight_search
import time
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")


llm = ChatGroq(
    model = "llama-3.3-70b-versatile"
)

class TravelState(TypedDict):
    messages : Annotated[list[AnyMessage],operator.add]
    user_query :str
    flight_results : str
    hotel_results :str
    itinerary :str
    llm_calls : int


def flight_agent(state:TravelState):
    print("Running flight_agent")
    start = time.time()
    query = state["user_query"]

    flight_data = flight_search(query=query)

    # print("="*50,"Flight flight_agent")
    # print(flight_data)
    # print("Flight Agent:", time.time() - start)
    return {
        "flight_results" : flight_data,
        "messages" :[
            AIMessage(content=f"Flight results fetched")

        ],
        # "llm_calls" : state.get("llm_calls" , 0) +1
    }


def hotel_agent(state:TravelState):
    print("Running hotel_agent")

    query = f"Best hotels for {state['user_query']}"

    hotel_results = tavily_search(query=query)

    # print("="*50,"Hotel hotel_agent")
    # print(hotel_results)

    return {
        "hotel_results" : hotel_results,
        "messages" :[
            AIMessage(content=f"Hotel results fetched")

        ],
        # "llm_calls" : state.get("llm_calls" , 0) +1
    }


def itienrary_agent(state : TravelState):
    print("Running itienrary_agent")
    prompt =f"""
    Create a travel itinerary.

    User Query:
    {state['user_query']}

    Flight Results :
    {state['flight_results']}

    Hotel Results :
    {state['hotel_results']}

    """

    # print("itienrary Agent ", {prompt})
    
    response = llm.invoke([
        SystemMessage(
            content="You are an expert travel planner"
        ),
        HumanMessage(
            content=prompt
        )
    ])

    print("itienrary Agent Resonse ", response)
    
    return {
        "itinerary" : response.content,
        "messages" :[response],
        # "llm_calls" :state.get("llm_calls",0)+1

    }



def final_agent(state : TravelState):
    print("Running final_agent")
    final_prompt =f"""
    Generate final travel response.

    Flights:
    {state["flight_results"]}

    Hotels:
    {state["hotel_results"]}

    Itienrary:
    {state["itinerary"]}
    """

    print("Final Agent Prompt" , final_prompt)
    response = llm.invoke([
        HumanMessage(content=final_prompt)
    ])

    print("Final Agent Response" , response)
    return {
        "messages":[response],
        # "llm_calls" :state.get("llm_calls",0)+1
    }



graph = StateGraph(TravelState)


graph.add_node("flight_agent",flight_agent)
graph.add_node("hotel_agent",hotel_agent)
graph.add_node("itienrary_agent",itienrary_agent)
graph.add_node("final_agent",final_agent)


graph.add_edge(START,"flight_agent")
graph.add_edge("flight_agent","hotel_agent")
graph.add_edge("hotel_agent","itienrary_agent")
graph.add_edge("itienrary_agent","final_agent")
graph.add_edge("final_agent",END)

_conn= psycopg.connect(DATABASE_URL, autocommit=True)
checkpointer=PostgresSaver(_conn)
checkpointer.setup()


app = graph.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    config ={"configurable" :{
            "thread_id" : "shivam_tiwari"
    }}

    user_input=input("Enter travel request :")

    result = app.invoke({
        "messages":[
            HumanMessage(content=user_input)
        ],
        "user_query" : user_input,
        "flight_results" : "",
        "hotel_results" :" ",
        "itinerary" : " ",
        "llm_calls" :" "
    },
    config=config
    
    )

    print("\n FINAL RESULT : \n")

    for msg in result["messages"]:
        print(msg.content)


