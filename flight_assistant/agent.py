from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google_flight_analysis.scrape import Scrape

def flight_checker(location: str, date: str) -> dict: 
    # 1 Check the flight 
    try: 
        scraper = Scrape()
        flight_data = scraper.get_flights(location, date)
        price = flight_data["price"]
        return { 
            "flight information": flight_data, 
            "price": price
        }
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
