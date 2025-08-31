"""
Utility functions for API path generation and inspection
"""
from fastapi import FastAPI
from typing import Dict, List, Any
import inspect
from pydantic import BaseModel


def get_all_api_paths(app: FastAPI) -> Dict[str, Any]:
    """
    Generate a comprehensive list of all API paths with their details
    including methods, parameters, request/response models
    """
    api_paths = {}

    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            route_info = {
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'Unknown'),
                "summary": getattr(route, 'summary', ''),
                "description": getattr(route, 'description', ''),
                "tags": getattr(route, 'tags', []),
            }

            # Get endpoint function details
            if hasattr(route, 'endpoint'):
                endpoint = route.endpoint
                route_info["endpoint_name"] = endpoint.__name__ if endpoint else 'Unknown'

                # Get function signature and parameters
                if endpoint:
                    sig = inspect.signature(endpoint)
                    parameters = {}

                    for param_name, param in sig.parameters.items():
                        param_info = {
                            "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                            "default": str(param.default) if param.default != inspect.Parameter.empty else None,
                            "required": param.default == inspect.Parameter.empty
                        }
                        parameters[param_name] = param_info

                    route_info["parameters"] = parameters

            # Get path parameters
            if hasattr(route, 'path_regex'):
                path_params = []
                # Extract path parameters from the route path
                import re
                path_param_pattern = r'\{([^}]+)\}'
                matches = re.findall(path_param_pattern, route.path)
                for match in matches:
                    path_params.append(match)
                route_info["path_parameters"] = path_params

            api_paths[f"{route.path}_{list(route.methods)}"] = route_info

    return api_paths


def generate_request_payload_schema(app: FastAPI) -> Dict[str, Any]:
    """
    Generate schema for request payloads for all endpoints
    """
    payload_schemas = {}

    for route in app.routes:
        if hasattr(route, 'endpoint') and hasattr(route, 'path') and hasattr(route, 'methods'):
            if route.endpoint:
                sig = inspect.signature(route.endpoint)

                for param_name, param in sig.parameters.items():
                    # Check if parameter is a Pydantic model (request body)
                    if (param.annotation != inspect.Parameter.empty and
                        hasattr(param.annotation, '__bases__') and
                        BaseModel in param.annotation.__mro__):

                        route_key = f"{route.path}_{list(route.methods)}"
                        if route_key not in payload_schemas:
                            payload_schemas[route_key] = {}

                        # Get the schema of the Pydantic model
                        try:
                            schema = param.annotation.model_json_schema()
                            payload_schemas[route_key][param_name] = {
                                "model_name": param.annotation.__name__,
                                "schema": schema
                            }
                        except Exception as e:
                            payload_schemas[route_key][param_name] = {
                                "model_name": param.annotation.__name__,
                                "error": str(e)
                            }

    return payload_schemas


def print_all_api_info(app: FastAPI) -> None:
    """
    Print comprehensive API information
    """
    print("=" * 80)
    print("API PATHS AND REQUEST PAYLOADS")
    print("=" * 80)

    api_paths = get_all_api_paths(app)
    payload_schemas = generate_request_payload_schema(app)

    for route_key, route_info in api_paths.items():
        print(f"\n{'-' * 60}")
        print(f"Path: {route_info['path']}")
        print(f"Methods: {', '.join(route_info['methods'])}")
        print(f"Endpoint: {route_info.get('endpoint_name', 'Unknown')}")

        if route_info.get('summary'):
            print(f"Summary: {route_info['summary']}")

        if route_info.get('path_parameters'):
            print(f"Path Parameters: {', '.join(route_info['path_parameters'])}")

        # Print request payload schema if available
        if route_key in payload_schemas:
            print("Request Payload Models:")
            for param_name, payload_info in payload_schemas[route_key].items():
                print(f"  - {param_name}: {payload_info['model_name']}")
                if 'schema' in payload_info:
                    print(f"    Schema: {payload_info['schema']}")

        print(f"{'-' * 60}")
