import os
from dotenv import load_dotenv
import requests

load_dotenv()

def flight_search(query):
    url = "https://api.aviationstack.com/v1/flights"

    param = {
        "access_key" : os.getenv("AVIATIONSTACK_API_KEY"),
        "limit" :5
    }

    response= requests.get(url, params=param)

    data = response.json()

    flights = []

    if "data" in data:
        for flight in data["data"][:5]:
            airline = flight.get("airline", {}).get("name", "N/A")
            departure = flight.get("departure", {}).get("airport", "N/A")
            arrival = flight.get("arrival", {}).get("airport", "N/A")
            status = flight.get("flight_status", "N/A")

            flights.append(
                f"""
Airline : {airline}
Departure : {departure}
Arrival : {arrival}
Status : {status}
""".strip()
            )

    return "\n\n".join(flights)

