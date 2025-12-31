---
title: FlightAware MCP Agent
emoji: ✈️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
---

# FlightAware API Tools

A collection of tools and utilities for working with the FlightAware API to access flight tracking data and aviation information.

## Overview

This project provides a set of tools to simplify interaction with FlightAware's data services, allowing developers to easily access real-time and historical flight data, airport information, and other aviation-related data.

## Project Structure

```
flightaware-api-tools/
├── Agent/              # FastAPI Agent with LangChain integration
│   ├── agent.py        # Main API server
│   └── public/         # Static files (frontend build output)
├── MCPServer/          # MCP (Model Context Protocol) Server
│   └── server.py       # FlightAware tools for AI agents
├── frontend/           # React frontend (Vite + TypeScript)
│   ├── App.tsx
│   ├── index.html
│   └── vite.config.ts
├── Dockerfile          # Multi-stage Docker build
├── .dockerignore       # Docker build exclusions
├── requirements.txt    # Python dependencies
└── *.py                # Standalone utility scripts
```

## Features

- **Agent**: FastAPI-based AI agent with LangChain and MCP integration
- **MCPServer**: MCP server providing FlightAware tools for AI assistants
- **Frontend**: React-based web interface for interacting with the agent
- Tools for querying flight tracking data
- Utilities for retrieving airport and aircraft information
- GeoJSON conversion for flight path visualization

## Prerequisites

- Python 3.11 or higher
- Node.js 20 or higher (for frontend development)
- Docker (optional, for containerized deployment)
- FlightAware API credentials (AeroAPI key)
- OpenAI API key (for AI agent)

## Installation

### Option 1: Local Development

1. Clone this repository:

   ```bash
   git clone https://github.com/tthogho1/flightaware-api-tools.git
   cd flightaware-api-tools
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. Configure your API credentials:
   Create a `.env` file in the project root:

   ```env
   FLIGHTAWARE_API_KEY=your_aeroapi_key
   OPENAI_API_KEY=your_openai_api_key
   ```

5. Build the frontend and copy to Agent/public:

   ```bash
   cd frontend
   npm run build
   # Copy dist/ contents to Agent/public/
   ```

6. Run the Agent server:

   ```bash
   python -m uvicorn Agent.agent:app --host 0.0.0.0 --port 8000
   ```

   Access the application at: http://localhost:8000/view/

### Option 2: Docker Deployment

1. Clone the repository and configure `.env` file as above.

2. Build the Docker image:

   ```bash
   docker build -t flightaware-agent .
   ```

3. Run the container:

   ```bash
   docker run -p 8000:8000 --env-file .env flightaware-agent
   ```

   Access the application at: http://localhost:8000/view/

## Architecture

### Agent (FastAPI)

The Agent is a FastAPI application that:

- Serves the React frontend at `/view/`
- Provides an API endpoint at `/api/agent` for AI interactions
- Uses LangChain with GPT-4 for intelligent responses
- Integrates with MCP Server via stdio transport

### MCPServer

The MCP Server provides tools for AI agents:

- `get_departures(airport_code)`: Retrieves departure flights from a specified airport

### Frontend

A React application built with Vite:

- TypeScript support
- Communicates with the Agent API
- Served at `/view/` path

## Python Utility Scripts

- **convertToGeoJson.py** - Converts flight route data to GeoJSON format for visualization on maps
- **getAireportInfo.py** - Retrieves detailed information about airports using the FlightAware API
- **getFlightInfor.py** - Retrieves flight route information for a specific flight using the FlightAware API
- **getFlightNumber.py** - Retrieves flight numbers for a specific airport using the FlightAware API
- **getMultiFlightGeoJson.py** - Combines the functionality of the other scripts to retrieve multiple flight routes and convert them to a single GeoJSON file with different colors for each flight

## Usage Examples

### Using the Agent API

```bash
curl -X POST http://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{"input": "羽田空港の出発便を教えてください"}'
```

### Example: Getting Airport Information

```python
from getAireportInfo import get_airport_info

# Get information about a specific airport
airport_info = get_airport_info("RJNA")  # Nagoya Airfield
```

### Example: Getting Flight Route Information

```python
from getFlightInfor import get_flight_route

# Get route information for a specific flight
flight_route = get_flight_route("ANA182-1747206976-airline-1811p")
```

### Example: Converting Flight Route to GeoJSON

```python
from getFlightInfor import get_flight_route
from convertToGeoJson import convert_To_GeoJson

# Get flight route and convert to GeoJSON
flight_data = get_flight_route("ANA182-1747206976-airline-1811p")
geojson = convert_To_GeoJson(flight_data)
```

### Example: Getting Multiple Flight Routes as GeoJSON

```python
from getMultiFlightGeoJson import get_multi_flight_geojson

# Get multiple flight routes from an airport and convert to GeoJSON
get_multi_flight_geojson()
```

## API Endpoints

| Endpoint     | Method | Description          |
| ------------ | ------ | -------------------- |
| `/view/`     | GET    | React frontend       |
| `/api/agent` | POST   | AI agent interaction |

## Environment Variables

| Variable              | Description              |
| --------------------- | ------------------------ |
| `FLIGHTAWARE_API_KEY` | FlightAware AeroAPI key  |
| `OPENAI_API_KEY`      | OpenAI API key for GPT-4 |

## FlightAware API Reference

This project uses the FlightAware AeroAPI. For official API documentation and to obtain API credentials, visit:

- [FlightAware AeroAPI Documentation](https://flightaware.com/aeroapi/docs/)
- [FlightAware AeroAPI Portal](https://flightaware.com/aeroapi/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FlightAware for providing the AeroAPI service
- OpenAI for GPT-4
- LangChain for AI agent framework
- Contributors to this project
