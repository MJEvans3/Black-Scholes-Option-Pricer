import json

def get_ai_response(user_query, financial_data_json):
    """
    Placeholder for AI chat function.
    In a real application, this would interact with an LLM API.
    """
    response = f"You asked: '{user_query}'.\n\n"
    response += "This is a dummy response. Here is the portfolio data I received:\n"
    
    try:
        # Pretty-print the JSON data
        data = json.loads(financial_data_json)
        response += f"```json\n{json.dumps(data, indent=2)}\n```"
    except json.JSONDecodeError:
        response += financial_data_json # Fallback to raw string if not valid JSON

    return response