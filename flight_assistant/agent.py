from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from amadeus import Client, ResponseError
from .config import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET, GOOGLE_API_KEY
import os

def flight_checker(location: str, date: str) -> dict: 
    # 1 Check the flight 
    try: 
        # Validate that API credentials are available
        if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
            return {"error": "Amadeus API credentials not found. Please check your .env file."}
        
        # Initialize Amadeus client
        amadeus = Client(
            client_id=AMADEUS_CLIENT_ID,
            client_secret=AMADEUS_CLIENT_SECRET
        )
        
        # Parse location (assuming format: "origin-destination")
        if "-" not in location:
            return {"error": "Location format should be 'ORIGIN-DESTINATION' (e.g., 'JFK-LAX')"}
        
        try:
            origin, destination = location.split("-")
            origin = origin.strip().upper()
            destination = destination.strip().upper()
        except ValueError:
            return {"error": "Invalid location format. Use 'ORIGIN-DESTINATION' format."}
        
        # Validate IATA codes (should be 3 characters)
        if len(origin) != 3 or len(destination) != 3:
            return {"error": "Airport codes must be 3-letter IATA codes (e.g., JFK, LAX)"}
        
        # Format date (assuming YYYY-MM-DD format)
        # Amadeus requires date in ISO format (YYYY-MM-DD)
        if not date or len(date) != 10 or date.count('-') != 2:
            return {"error": "Date must be in YYYY-MM-DD format"}
        
        # Search for flights
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            max=10  # Limit results to avoid overwhelming response
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
        error_msg = f"Amadeus API error: {error}"
        if hasattr(error, 'response') and error.response:
            if error.response.status_code == 400:
                error_msg += "\n400 Bad Request - Check your airport codes and date format."
                error_msg += "\nEnsure airport codes are valid 3-letter IATA codes and date is in YYYY-MM-DD format."
            elif error.response.status_code == 401:
                error_msg += "\n401 Unauthorized - Check your Amadeus API credentials."
        return {"error": error_msg}
    except Exception as e: 
        return {"error": f"General error: {str(e)}"}


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
