import json
import os
from collections.abc import Sequence

import requests
from mcp.types import (
    EmbeddedResource,
    ImageContent,
    TextContent,
    Tool,
)

from . import toolhandler

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


class GeocodeToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("google_maps_geocode")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Convert an address into geographic coordinates.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The address to convert into geographic coordinates.",
                    }
                },
                "required": ["address"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        # https://maps.googleapis.com/maps/api/geocode/json
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={args['address']}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "location": data["results"][0]["geometry"]["location"],
                        "formatted_address": data["results"][0]["formatted_address"],
                        "place_id": data["results"][0]["place_id"],
                    },
                    indent=2,
                ),
            )
        ]


class ReverseGeocodeToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("google_maps_reverse_geocode")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Convert geographic coordinates into an address.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        # https://maps.googleapis.com/maps/api/geocode/json
        url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={args['latitude']},{args['longitude']}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "formatted_address": data["results"][0]["formatted_address"],
                        "place_id": data["results"][0]["place_id"],
                    },
                    indent=2,
                ),
            )
        ]


class SearchPlacesToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("google_maps_search_places")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Search for places using Google Places API""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "location": {
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                        },
                        "description": "Optional center point for the search",
                    },
                    "radius": {
                        "type": "number",
                        "description": "Search radius in meters (max 50000)",
                    },
                },
                "required": ["query"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        # https://maps.googleapis.com/maps/api/place/textsearch/json
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={args['query']}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return [TextContent(type="text", text=json.dumps(data, indent=2))]


class PlaceDetailsToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("google_maps_place_details")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Get details about a place using Google Places API""",
            inputSchema={
                "type": "object",
                "properties": {
                    "place_id": {"type": "string"},
                },
                "required": ["place_id"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        # https://maps.googleapis.com/maps/api/place/details/json
        url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={args['place_id']}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return [TextContent(type="text", text=json.dumps(data, indent=2))]


class DistanceMatrixToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("google_maps_distance_matrix")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Get distance and duration between two places using Google Maps API""",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                },
                "required": ["origin", "destination"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        # https://maps.googleapis.com/maps/api/distancematrix/json
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={args['origin']}&destinations={args['destination']}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return [TextContent(type="text", text=json.dumps(data, indent=2))]


class ElevationToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("google_maps_elevation")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Get elevation at a given location using Google Maps API""",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                },
                "required": ["location"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        # https://maps.googleapis.com/maps/api/elevation/json
        url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={args['location']}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return [TextContent(type="text", text=json.dumps(data, indent=2))]


class DirectionsToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("google_maps_directions")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Get directions between two points using Google Maps API""",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Starting point address or coordinates",
                    },
                    "destination": {
                        "type": "string",
                        "description": "Ending point address or coordinates",
                    },
                    "mode": {
                        "type": "string",
                        "description": "Travel mode (driving, walking, bicycling, transit)",
                        "enum": ["driving", "walking", "bicycling", "transit"],
                    },
                },
                "required": ["origin", "destination"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        # https://maps.googleapis.com/maps/api/directions/json
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={args['origin']}&destination={args['destination']}&mode={args['mode']}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return [TextContent(type="text", text=json.dumps(data, indent=2))]
