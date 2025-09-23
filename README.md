# Flight Agent

A Python flight assistant agent built with Google ADK (Agent Development Kit) that helps users find and check flight information.

## Features

- **Greeting Agent**: Welcomes users and handles initial interactions
- **Flight Checker Agent**: Searches and retrieves flight information based on location and date
- **Root Agent**: Coordinates between sub-agents to provide the best user experience

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Web Interface
Start the ADK web server:
```bash
adk web . --port 8001
```

Then open your browser to `http://localhost:8001`

### CLI Interface
Run the agent in CLI mode:
```bash
adk run flight_assistant
```

## Project Structure

```
flight_agent/
├── flight_assistant/
│   ├── __init__.py
│   └── agent.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Dependencies

- google-generativeai==0.8.5
- google-adk[database]==0.3.0
- deprecated (auto-installed as dependency)

## Agent Structure

The project consists of three main agents:

1. **GreetingAgent**: Handles user greetings and initial requests
2. **FlightCheckerAgent**: Processes flight search requests and returns formatted results
3. **Root Agent**: Main coordinator that switches between sub-agents based on user needs

## Functions

- `flight_checker(location: str, date: str)`: Searches for flight information based on provided parameters

## Contributing

Feel free to submit issues and enhancement requests!