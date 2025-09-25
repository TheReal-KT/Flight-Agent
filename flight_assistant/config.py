import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API credentials from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")