import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

from just_ask_1 import VALID_APPLICATIONS

load_dotenv()  # loads GEMINI_API_KEY from .env


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

    interaction = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=message,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )

    return interaction.text


if __name__ == "__main__":
    transcript = "Hey Google, navigate to Ara."

    print(parse_transcript(transcript, VALID_APPLICATIONS))
