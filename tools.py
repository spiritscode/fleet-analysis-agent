import anthropic

# Tool definitions — this is what you pass to Claude
TOOLS = [
    {
        "name": "get_anomaly_scores",
        "description": "Returns anomaly scores for a vehicle from the Isolation Forest model. Score > 0.7 means high risk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "vehicle_id": {
                    "type": "string",
                    "description": "Vehicle ID, e.g. 'V-104'"
                }
            },
            "required": ["vehicle_id"]
        }
    },
    {
        "name": "forecast_delay",
        "description": "Returns delay probability (0-1) for a given route using the logistics model.",
        "input_schema": {
            "type": "object", 
            "properties": {
                "route_id": {
                    "type": "string",
                    "description": "Route ID, e.g. 'R-7'"
                }
            },
            "required": ["route_id"]
        }
    },
    {
        "name": "send_slack_alert",
        "description": "Sends an alert to the ops Slack channel. Use when anomaly score > 0.7.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Alert message to send"
                },
                "severity": {
                    "type": "string",
                    "enum": ["LOW", "MEDIUM", "HIGH"]
                }
            },
            "required": ["message", "severity"]
        }
    }
]

# Tool execution — maps tool name to actual function
def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "get_anomaly_scores":
        # In real life: call your Isolation Forest model
        # For demo: return mock data
        scores = {"V-101": 0.3, "V-102": 0.5, "V-103": 0.9, "V-104": 0.82}
        vehicle = tool_input["vehicle_id"]
        score = scores.get(vehicle, 0.1)
        return f"Anomaly score for {vehicle}: {score}"

    elif tool_name == "forecast_delay":
        delays = {"R-5": 0.2, "R-6": 0.45, "R-7": 0.73, "R-8": 0.6}
        route = tool_input["route_id"]
        prob = delays.get(route, 0.1)
        return f"Delay probability for {route}: {prob} (73% = HIGH)"

    elif tool_name == "send_slack_alert":
        # In real life: call Slack API
        print(f"\n🚨 SLACK ALERT [{tool_input['severity']}]: {tool_input['message']}")
        return "Alert sent to #ops-alerts successfully"