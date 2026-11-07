import json

from dotenv import load_dotenv
from google import genai

load_dotenv()  # loads GEMINI_API_KEY from .env


VALID_APPLICATIONS: dict[str, dict] = {
    "maps": {
        "description": "Navigation and location search",
        "actions": {
            "navigate": {
                "destination": "str",
                "mode": "driving | walking | cycling | transit",
            },
            "search_nearby": {"query": "str", "radius_km": "float"},
            "show_traffic": {},
        },
    },
    "music": {
        "description": "Music streaming and playback",
        "actions": {
            "play": {"song": "str", "artist": "str", "playlist": "str"},
            "pause": {},
            "skip": {},
            "set_volume": {"level": "int (0-100)"},
        },
    },
    "messages": {
        "description": "Send and read text messages",
        "actions": {
            "send_message": {"recipient": "str", "body": "str"},
            "read_latest": {"sender": "str"},
        },
    },
    "calendar": {
        "description": "Manage events and reminders",
        "actions": {
            "create_event": {
                "title": "str",
                "date": "YYYY-MM-DD",
                "time": "HH:MM",
                "duration_minutes": "int",
            },
            "list_events": {"date": "YYYY-MM-DD"},
            "set_reminder": {"text": "str", "time": "HH:MM"},
        },
    },
    "weather": {
        "description": "Weather forecasts and conditions",
        "actions": {
            "current_conditions": {"location": "str"},
            "forecast": {"location": "str", "days": "int"},
        },
    },
}


def parse_transcript(text_in: str, valid_applications: dict[str, dict]):
    schema_string = """
    {
        "target_application": "[application]",
        "target_action": "[action]",
        "additional_parameters": {
            "[parameter_name_1]": "[parameter_value_1]",
            ...
        }
    }
    """

    message = f"""For the following transcript, determine the target action the user wants to take, 
    the target application, and any additional parameters.\n 
    Do not include any additional information or preamble. \n
    The target application, action and parameters must be chosen from the following
    valid applications (each lists its actions and the parameters each action accepts):\n
    {json.dumps(valid_applications, indent=2)}\n
    Return the response as json following the schema:\n{schema_string}

    transcript: {text_in}"""

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=message,
    )

    return interaction.output_text


if __name__ == "__main__":
    transcript = "Hey Google, navigate to Ara."

    print(parse_transcript(transcript, VALID_APPLICATIONS))
