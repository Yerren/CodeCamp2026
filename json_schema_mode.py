import json

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from just_ask_1 import VALID_APPLICATIONS

load_dotenv()  # loads GEMINI_API_KEY from .env


class ParsedCommand(BaseModel):
    target_application: str = Field(description="The application the user wants to use")
    target_action: str = Field(
        description="The action to perform within that application"
    )
    additional_parameters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Parameters for the action mentioned in the transcript, as a mapping "
            "of parameter name (as listed for the chosen action) to value"
        ),
    )


def parse_transcript(
    text_in: str, valid_applications: dict[str, dict]
) -> ParsedCommand:
    message = f"""For the following transcript, determine the target action the user wants to take,
    the target application, and any additional parameters.\n
    The target application, action and parameters must be chosen from the following
    valid applications (each lists its actions and the parameters each action accepts):\n
    {json.dumps(valid_applications, indent=2)}\n

    transcript: {text_in}"""

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=message,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            # Native structured output: the response is constrained to this JSON schema
            response_json_schema=ParsedCommand.model_json_schema(),
        ),
    )

    print(response)
    # With response_json_schema, response.parsed is the already-decoded JSON (a dict),
    # so validate it into the Pydantic model
    return ParsedCommand.model_validate(response.parsed)


if __name__ == "__main__":
    transcript = "Hey Google, navigate to Ara."

    result = parse_transcript(transcript, VALID_APPLICATIONS)
    print(result.model_dump_json(indent=2))
