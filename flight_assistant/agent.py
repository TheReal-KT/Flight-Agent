from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from amadeus import Client, ResponseError
from .config import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET

def flight_checker(location: str, date: str) -> dict: 
    # 1 Check the flight 
    try: 
        # Initialize Amadeus client
        amadeus = Client(
            client_id=AMADEUS_CLIENT_ID,
            client_secret=AMADEUS_CLIENT_SECRET
        )
        
        # Parse location (assuming format: "origin-destination")
        origin, destination = location.split("-")
        
        # Format date (assuming YYYY-MM-DD format)
        # Amadeus requires date in ISO format (YYYY-MM-DD)
        
        # Search for flights
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin.strip(),
            destinationLocationCode=destination.strip(),
            departureDate=date,
            adults=1
        )
        
        # Process the response
        flights = response.data
        
        if not flights:
            return {"error": "No flights found for the given criteria"}
        
        # Extract relevant information from the first flight offer
        flight_data = {
            "carrier": flights[0]["validatingAirlineCodes"][0],
            "departure": flights[0]["itineraries"][0]["segments"][0]["departure"]["at"],
            "arrival": flights[0]["itineraries"][0]["segments"][-1]["arrival"]["at"],
            "duration": flights[0]["itineraries"][0]["duration"],
            "stops": len(flights[0]["itineraries"][0]["segments"]) - 1
        }
        
        # Extract price
        price = {
            "amount": flights[0]["price"]["total"],
            "currency": flights[0]["price"]["currency"]
        }
        
        return { 
            "flight information": flight_data, 
            "price": price,
            "all_options": len(flights)
        }
    except ResponseError as error:
        return {"error": f"Amadeus API error: {error}"}
    except Exception as e: 
        return {"error": str(e)}


greeting_agent = LlmAgent(
    name="GreetingAgent",
    model="gemini-2.5-flash",
    description="Greets the user.",
    instruction=
    """
    You are a receptionist, you greet the user by their name formally. 
    * Ask what the user needs regard to available flights.
    """, 

    tools=[google_search],
    output_key="greeting"
)

flight_checker_agent = LlmAgent(
    name="FlightCheckerAgent",
    model="gemini-2.5-flash",
    description="Flight agent checker", 
    instruction=
    """
    You are a flight agent, that will check the latest flights for the user based on their needed flights
    * Ask what the user needs regard to available flights.
    * The location parameter should be in the format "ORIGIN-DESTINATION" where ORIGIN and DESTINATION are IATA airport codes (e.g., "JFK-LAX").
    * The date parameter should be in the format "YYYY-MM-DD".
    
    Present the information in simple bullet point form, and summarise the data.
    """, 
    tools=[flight_checker],
    output_key="flight_information"
)

root_agent = LlmAgent(
    name="flight_assistant",
    description="Flight agent",
    model="gemini-2.5-flash",
    instruction="""
    You are the main agent. Switch between agents that can handle task best for user's needs
    """,
    sub_agents=[greeting_agent, flight_checker_agent]
)
